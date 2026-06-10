"""Deep neural controller for simplified rocket landing telemetry.

This module adapts the project's existing aerospace state vector to a PyTorch
supervised-learning controller.  It intentionally does not claim high-fidelity
flight control: the current simulator is vertical-dynamics focused, so the
network learns a bounded throttle policy from synthetic sensor/state vectors.

The architecture mirrors the portfolio deep-learning pattern used in the
quantum experiment: a dense encoder with LayerNorm, GELU activations, dropout,
and multiple task heads.  Here the heads are aerospace-specific:

* throttle_head: continuous throttle command in [0, 1]
* stability_head: landing-control quality score in [0, 1]
* phase_head: descent phase logits for coarse sensor/control interpretation
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset

from aerospace_sim.learning.telemetry_preprocessing import table_state_matrix


STATE_FEATURES: tuple[str, ...] = (
    "position_x_m",
    "position_y_m",
    "altitude_z_m",
    "velocity_x_mps",
    "velocity_y_mps",
    "vertical_velocity_z_mps",
    "roll_rad",
    "pitch_rad",
    "yaw_rad",
    "angular_velocity_x_radps",
    "angular_velocity_y_radps",
    "angular_velocity_z_radps",
    "fuel_mass_kg",
)

PHASE_LABELS: tuple[str, ...] = (
    "terminal_descent",
    "powered_descent",
    "approach",
    "high_altitude",
)

INPUT_DIM = len(STATE_FEATURES)
PHASE_CLASSES = len(PHASE_LABELS)


@dataclass(frozen=True)
class NeuralControllerConfig:
    """Configuration for the neural rocket controller."""

    input_dim: int = INPUT_DIM
    hidden_dim: int = 512
    latent_dim: int = 256
    phase_classes: int = PHASE_CLASSES
    dropout: float = 0.05


class NeuralRocketControllerNet(nn.Module):
    """Dense multi-head perceptron for rocket landing control.

    The network consumes the simulator's 13-dimensional state/sensor vector and
    returns bounded throttle, a stability score, and descent-phase logits.
    """

    def __init__(self, config: NeuralControllerConfig | None = None) -> None:
        super().__init__()
        self.config = config or NeuralControllerConfig()

        self.encoder = nn.Sequential(
            nn.Linear(self.config.input_dim, self.config.hidden_dim),
            nn.LayerNorm(self.config.hidden_dim),
            nn.GELU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.hidden_dim, self.config.hidden_dim),
            nn.LayerNorm(self.config.hidden_dim),
            nn.GELU(),
            nn.Dropout(self.config.dropout),
            nn.Linear(self.config.hidden_dim, self.config.latent_dim),
            nn.LayerNorm(self.config.latent_dim),
            nn.GELU(),
            nn.Linear(self.config.latent_dim, self.config.latent_dim),
            nn.LayerNorm(self.config.latent_dim),
            nn.GELU(),
        )

        self.throttle_head = nn.Sequential(
            nn.Linear(self.config.latent_dim, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

        self.stability_head = nn.Sequential(
            nn.Linear(self.config.latent_dim, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Linear(128, 64),
            nn.GELU(),
            nn.Linear(64, 1),
            nn.Sigmoid(),
        )

        self.phase_head = nn.Sequential(
            nn.Linear(self.config.latent_dim, 128),
            nn.LayerNorm(128),
            nn.GELU(),
            nn.Linear(128, self.config.phase_classes),
        )

        self.softmax = nn.Softmax(dim=1)

    def forward(
        self,
        x: torch.Tensor,
        return_probabilities: bool = False,
    ) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor] | tuple[
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
        torch.Tensor,
    ]:
        z = self.encoder(x)
        throttle = self.throttle_head(z)
        stability = self.stability_head(z)
        phase_logits = self.phase_head(z)

        if return_probabilities:
            return throttle, stability, phase_logits, self.softmax(phase_logits)

        return throttle, stability, phase_logits


def normalize_state_features(states: np.ndarray) -> np.ndarray:
    """Scale raw state vectors into numerically stable neural features.

    The constants are engineering-scale normalizers, not learned statistics.
    They make altitude, velocity, attitude, angular velocity, and fuel mass live
    in roughly comparable numeric ranges.
    """

    states = np.asarray(states, dtype=np.float32)
    scale = np.array(
        [
            100.0,
            100.0,
            1000.0,
            100.0,
            100.0,
            100.0,
            np.pi,
            np.pi,
            np.pi,
            10.0,
            10.0,
            10.0,
            1000.0,
        ],
        dtype=np.float32,
    )
    return states / scale


def expert_throttle_policy(states: np.ndarray) -> np.ndarray:
    """Generate a deterministic teacher throttle for supervised pretraining.

    The teacher is a conservative vertical landing heuristic: more downward
    speed and lower altitude increase throttle, while very high altitude keeps
    throttle moderate to avoid runaway ascent in the simplified simulator.
    """

    states = np.asarray(states, dtype=np.float32)
    altitude = np.maximum(states[:, 2], 0.0)
    vertical_velocity = states[:, 5]
    fuel_mass = np.maximum(states[:, 12], 1.0)

    altitude_term = np.clip((250.0 - altitude) / 250.0, 0.0, 1.0)
    descent_term = np.clip((-vertical_velocity - 2.0) / 45.0, 0.0, 1.0)
    fuel_penalty = np.clip((120.0 - fuel_mass) / 120.0, 0.0, 1.0)

    throttle = 0.18 + 0.42 * descent_term + 0.35 * altitude_term - 0.15 * fuel_penalty
    throttle = np.where(altitude < 5.0, np.minimum(throttle, 0.35), throttle)
    throttle = np.clip(throttle, 0.0, 1.0)
    return throttle.astype(np.float32).reshape(-1, 1)


def stability_score(states: np.ndarray, throttle: np.ndarray) -> np.ndarray:
    """Approximate control-quality score for training diagnostics."""

    states = np.asarray(states, dtype=np.float32)
    throttle = np.asarray(throttle, dtype=np.float32).reshape(-1)
    altitude = np.maximum(states[:, 2], 0.0)
    vertical_velocity = states[:, 5]
    attitude_error = np.linalg.norm(states[:, 6:9], axis=1)
    angular_rate = np.linalg.norm(states[:, 9:12], axis=1)

    soft_landing = np.exp(-np.abs(vertical_velocity + 2.0) / 30.0)
    attitude_quality = np.exp(-attitude_error / 0.5)
    rate_quality = np.exp(-angular_rate / 1.5)
    altitude_quality = 1.0 - np.clip(altitude / 1500.0, 0.0, 1.0) * 0.2
    throttle_smoothness = 1.0 - np.abs(throttle - 0.5) * 0.25

    score = soft_landing * attitude_quality * rate_quality * altitude_quality * throttle_smoothness
    return np.clip(score, 0.0, 1.0).astype(np.float32).reshape(-1, 1)


def descent_phase_labels(states: np.ndarray) -> np.ndarray:
    """Classify coarse flight-control phase from altitude."""

    altitude = np.asarray(states, dtype=np.float32)[:, 2]
    labels = np.zeros(len(altitude), dtype=np.int64)
    labels[(altitude >= 40.0) & (altitude < 180.0)] = 1
    labels[(altitude >= 180.0) & (altitude < 600.0)] = 2
    labels[altitude >= 600.0] = 3
    return labels


def generate_synthetic_rocket_states(n_samples: int, seed: int = 42) -> np.ndarray:
    """Create synthetic sensor/state samples for neural-controller pretraining."""

    rng = np.random.default_rng(seed)
    altitude = rng.uniform(0.0, 1000.0, size=n_samples)
    vertical_velocity = rng.uniform(-85.0, 25.0, size=n_samples)
    fuel_mass = rng.uniform(40.0, 900.0, size=n_samples)

    states = np.zeros((n_samples, INPUT_DIM), dtype=np.float32)
    states[:, 0] = rng.normal(0.0, 8.0, size=n_samples)
    states[:, 1] = rng.normal(0.0, 8.0, size=n_samples)
    states[:, 2] = altitude
    states[:, 3] = rng.normal(0.0, 5.0, size=n_samples)
    states[:, 4] = rng.normal(0.0, 5.0, size=n_samples)
    states[:, 5] = vertical_velocity
    states[:, 6:9] = rng.normal(0.0, 0.08, size=(n_samples, 3))
    states[:, 9:12] = rng.normal(0.0, 0.15, size=(n_samples, 3))
    states[:, 12] = fuel_mass
    return states


class RocketControlDataset(Dataset):
    """Supervised dataset for neural rocket-control pretraining."""

    def __init__(self, n_samples: int = 20_000, seed: int = 42) -> None:
        raw_states = generate_synthetic_rocket_states(n_samples=n_samples, seed=seed)
        throttle = expert_throttle_policy(raw_states)
        stability = stability_score(raw_states, throttle)
        phase = descent_phase_labels(raw_states)

        self.raw_states = torch.tensor(raw_states, dtype=torch.float32)
        self.x = torch.tensor(normalize_state_features(raw_states), dtype=torch.float32)
        self.y_throttle = torch.tensor(throttle, dtype=torch.float32)
        self.y_stability = torch.tensor(stability, dtype=torch.float32)
        self.y_phase = torch.tensor(phase, dtype=torch.long)

        permutation = torch.randperm(len(self.x), generator=torch.Generator().manual_seed(seed))
        self.raw_states = self.raw_states[permutation]
        self.x = self.x[permutation]
        self.y_throttle = self.y_throttle[permutation]
        self.y_stability = self.y_stability[permutation]
        self.y_phase = self.y_phase[permutation]

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.x[idx], self.y_throttle[idx], self.y_stability[idx], self.y_phase[idx]


class TelemetryControlDataset(Dataset):
    """Supervised dataset extracted from reproducible simulator trajectories."""

    def __init__(self, table, seed: int = 42) -> None:
        raw_states = table_state_matrix(table)
        throttle = table["target_throttle"].to_numpy(dtype=np.float32).reshape(-1, 1)
        stability = stability_score(raw_states, throttle)
        phase = descent_phase_labels(raw_states)

        self.raw_states = torch.tensor(raw_states, dtype=torch.float32)
        self.x = torch.tensor(normalize_state_features(raw_states), dtype=torch.float32)
        self.y_throttle = torch.tensor(throttle, dtype=torch.float32)
        self.y_stability = torch.tensor(stability, dtype=torch.float32)
        self.y_phase = torch.tensor(phase, dtype=torch.long)

        permutation = torch.randperm(len(self.x), generator=torch.Generator().manual_seed(seed))
        self.raw_states = self.raw_states[permutation]
        self.x = self.x[permutation]
        self.y_throttle = self.y_throttle[permutation]
        self.y_stability = self.y_stability[permutation]
        self.y_phase = self.y_phase[permutation]

    def __len__(self) -> int:
        return len(self.x)

    def __getitem__(self, idx: int) -> tuple[torch.Tensor, torch.Tensor, torch.Tensor, torch.Tensor]:
        return self.x[idx], self.y_throttle[idx], self.y_stability[idx], self.y_phase[idx]


def model_parameter_report(model: nn.Module) -> dict[str, int]:
    """Return parameter counts for documentation and tests."""

    total = sum(p.numel() for p in model.parameters())
    trainable = sum(p.numel() for p in model.parameters() if p.requires_grad)
    return {"total_parameters": total, "trainable_parameters": trainable}


def predict_throttle_from_state(
    model: NeuralRocketControllerNet,
    state: Iterable[float],
    device: str | torch.device = "cpu",
) -> float:
    """Run bounded throttle inference for one simulator state vector."""

    model.eval()
    array = np.asarray([list(state)], dtype=np.float32)
    features = torch.tensor(normalize_state_features(array), dtype=torch.float32, device=device)
    with torch.no_grad():
        throttle, _, _ = model(features)
    return float(throttle.cpu().item())
