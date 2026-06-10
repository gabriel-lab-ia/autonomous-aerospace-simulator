from __future__ import annotations

from pathlib import Path
from typing import Any

from aerospace_sim.core.state import RocketState


class NeuralController:
    """Experimental optional-PyTorch controller implementing compute_throttle."""

    def __init__(
        self,
        checkpoint_path: str | Path | None = None,
        *,
        allow_untrained: bool = False,
        device: str = "cpu",
    ) -> None:
        try:
            import torch
            from aerospace_sim.learning.neural_controller import (
                NeuralRocketControllerNet,
                predict_throttle_from_state,
            )
        except ImportError as exc:
            raise ImportError(
                "NeuralController requires the optional ml dependency group. "
                "Install it with: uv sync --group ml"
            ) from exc

        self._torch = torch
        self._predict_throttle = predict_throttle_from_state
        self.device = torch.device(device)
        self.checkpoint_path = Path(checkpoint_path) if checkpoint_path else None
        self.metadata: dict[str, Any] = {}

        if self.checkpoint_path is not None:
            checkpoint = torch.load(
                self.checkpoint_path,
                map_location=self.device,
                weights_only=True,
            )
            self.model = NeuralRocketControllerNet().to(self.device)
            self.model.load_state_dict(checkpoint["model_state_dict"])
            self.model.eval()
            self.metadata = checkpoint.get("metadata", {})
            self.is_trained = True
        elif allow_untrained:
            self.model = NeuralRocketControllerNet().to(self.device)
            self.model.eval()
            self.is_trained = False
        else:
            raise ValueError(
                "A checkpoint is required unless allow_untrained=True is explicitly set."
            )

    def compute_throttle(self, state: RocketState) -> float:
        """Predict and clamp throttle for the current simulator state."""
        throttle = self._predict_throttle(self.model, state.to_vector(), self.device)
        return max(0.0, min(1.0, float(throttle)))


def predict_throttle_from_state(controller: NeuralController, state: RocketState) -> float:
    """Predict a bounded throttle command through the controller contract."""
    return controller.compute_throttle(state)
