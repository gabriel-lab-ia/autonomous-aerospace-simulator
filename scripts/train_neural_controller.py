"""Train the optional deep neural rocket controller.

Run with the ML dependency group installed:

    uv sync --group ml
    uv run python scripts/train_neural_controller.py

The script trains a supervised neural controller on synthetic aerospace
telemetry/state vectors.  The teacher policy is intentionally conservative and
exists to pretrain a neural controller before future simulator-in-the-loop RL.
"""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import torch
import torch.nn as nn
from torch.utils.data import DataLoader, random_split

from aerospace_sim.learning import (
    PHASE_LABELS,
    NeuralRocketControllerNet,
    RocketControlDataset,
    model_parameter_report,
)

try:
    PROJECT_ROOT = Path(__file__).resolve().parents[1]
except NameError:
    PROJECT_ROOT = Path.cwd()

OUTPUTS_DIR = PROJECT_ROOT / "outputs" / "neural_controller"
FIGURES_DIR = OUTPUTS_DIR / "figures"
MODELS_DIR = OUTPUTS_DIR / "models"

FIGURES_DIR.mkdir(parents=True, exist_ok=True)
MODELS_DIR.mkdir(parents=True, exist_ok=True)

SEED = 42
DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


def train() -> None:
    torch.manual_seed(SEED)

    print("=== DEEP NEURAL ROCKET CONTROL NETWORK ===")
    print(f"Device: {DEVICE}")
    if torch.cuda.is_available():
        print("GPU:", torch.cuda.get_device_name(0))

    dataset = RocketControlDataset(n_samples=20_000, seed=SEED)
    train_size = int(0.8 * len(dataset))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = random_split(
        dataset,
        [train_size, val_size],
        generator=torch.Generator().manual_seed(SEED),
    )

    train_loader = DataLoader(train_dataset, batch_size=128, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=256, shuffle=False)

    model = NeuralRocketControllerNet().to(DEVICE)
    report = model_parameter_report(model)

    print("\n=== MODEL ARCHITECTURE ===")
    print(model)
    print("\n=== PARAMETERS ===")
    print(f"Total parameters: {report['total_parameters']:,}")
    print(f"Trainable parameters: {report['trainable_parameters']:,}")
    print("\n=== OUTPUT HEADS ===")
    print("Throttle command: 1 bounded value in [0, 1]")
    print("Stability score: 1 bounded value in [0, 1]")
    print(f"Descent phase logits: {len(PHASE_LABELS)} classes -> {PHASE_LABELS}")

    optimizer = torch.optim.AdamW(model.parameters(), lr=5e-4, weight_decay=2e-4)
    throttle_loss_fn = nn.MSELoss()
    stability_loss_fn = nn.MSELoss()
    phase_loss_fn = nn.CrossEntropyLoss()

    epochs = 80
    train_losses: list[float] = []
    val_losses: list[float] = []
    val_throttle_maes: list[float] = []
    val_stability_maes: list[float] = []
    val_phase_accuracies: list[float] = []

    print("\nStarting training...")
    for epoch in range(1, epochs + 1):
        model.train()
        total_train_loss = 0.0

        for batch_x, batch_throttle, batch_stability, batch_phase in train_loader:
            batch_x = batch_x.to(DEVICE)
            batch_throttle = batch_throttle.to(DEVICE)
            batch_stability = batch_stability.to(DEVICE)
            batch_phase = batch_phase.to(DEVICE)

            optimizer.zero_grad()
            throttle_pred, stability_pred, phase_logits = model(batch_x)

            loss_throttle = throttle_loss_fn(throttle_pred, batch_throttle)
            loss_stability = stability_loss_fn(stability_pred, batch_stability)
            loss_phase = phase_loss_fn(phase_logits, batch_phase)
            loss = loss_throttle + loss_stability + 0.25 * loss_phase

            loss.backward()
            optimizer.step()
            total_train_loss += loss.item() * batch_x.size(0)

        avg_train_loss = total_train_loss / len(train_loader.dataset)

        model.eval()
        total_val_loss = 0.0
        total_throttle_mae = 0.0
        total_stability_mae = 0.0
        correct_phase = 0
        total = 0

        with torch.no_grad():
            for batch_x, batch_throttle, batch_stability, batch_phase in val_loader:
                batch_x = batch_x.to(DEVICE)
                batch_throttle = batch_throttle.to(DEVICE)
                batch_stability = batch_stability.to(DEVICE)
                batch_phase = batch_phase.to(DEVICE)

                throttle_pred, stability_pred, phase_logits, phase_probabilities = model(
                    batch_x,
                    return_probabilities=True,
                )

                loss_throttle = throttle_loss_fn(throttle_pred, batch_throttle)
                loss_stability = stability_loss_fn(stability_pred, batch_stability)
                loss_phase = phase_loss_fn(phase_logits, batch_phase)
                loss = loss_throttle + loss_stability + 0.25 * loss_phase

                total_val_loss += loss.item() * batch_x.size(0)
                total_throttle_mae += torch.sum(torch.abs(throttle_pred - batch_throttle)).item()
                total_stability_mae += torch.sum(torch.abs(stability_pred - batch_stability)).item()
                correct_phase += (torch.argmax(phase_probabilities, dim=1) == batch_phase).sum().item()
                total += batch_x.size(0)

        avg_val_loss = total_val_loss / len(val_loader.dataset)
        throttle_mae = total_throttle_mae / total
        stability_mae = total_stability_mae / total
        phase_accuracy = correct_phase / total

        train_losses.append(avg_train_loss)
        val_losses.append(avg_val_loss)
        val_throttle_maes.append(throttle_mae)
        val_stability_maes.append(stability_mae)
        val_phase_accuracies.append(phase_accuracy)

        if epoch == 1 or epoch % 10 == 0:
            print(
                f"Epoch {epoch:03d} | "
                f"Train Loss: {avg_train_loss:.6f} | "
                f"Val Loss: {avg_val_loss:.6f} | "
                f"Throttle MAE: {throttle_mae:.6f} | "
                f"Stability MAE: {stability_mae:.6f} | "
                f"Phase Acc: {phase_accuracy:.4f}"
            )

    checkpoint_path = MODELS_DIR / "neural_rocket_controller.pt"
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "train_losses": train_losses,
            "val_losses": val_losses,
            "val_throttle_maes": val_throttle_maes,
            "val_stability_maes": val_stability_maes,
            "val_phase_accuracies": val_phase_accuracies,
            "state_features": list(dataset.raw_states.shape),
            "phase_labels": PHASE_LABELS,
            "parameter_report": report,
        },
        checkpoint_path,
    )

    plt.figure(figsize=(10, 6), facecolor="black")
    ax = plt.gca()
    ax.set_facecolor("black")
    plt.plot(train_losses, label="Train Loss")
    plt.plot(val_losses, label="Validation Loss")
    plt.title("Deep Neural Rocket Controller - Loss", color="white")
    plt.xlabel("Epoch", color="white")
    plt.ylabel("Loss", color="white")
    plt.tick_params(colors="white")
    plt.legend()
    for spine in ax.spines.values():
        spine.set_color("white")
    loss_path = FIGURES_DIR / "neural_controller_loss.png"
    plt.savefig(loss_path, dpi=300, facecolor="black", bbox_inches="tight")
    plt.close()

    plt.figure(figsize=(10, 6), facecolor="black")
    ax = plt.gca()
    ax.set_facecolor("black")
    plt.plot(val_throttle_maes, label="Throttle MAE")
    plt.plot(val_stability_maes, label="Stability MAE")
    plt.plot(val_phase_accuracies, label="Phase Accuracy")
    plt.title("Deep Neural Rocket Controller - Validation Metrics", color="white")
    plt.xlabel("Epoch", color="white")
    plt.ylabel("Metric", color="white")
    plt.tick_params(colors="white")
    plt.legend()
    for spine in ax.spines.values():
        spine.set_color("white")
    metrics_path = FIGURES_DIR / "neural_controller_metrics.png"
    plt.savefig(metrics_path, dpi=300, facecolor="black", bbox_inches="tight")
    plt.close()

    print(f"\nModel checkpoint saved to: {checkpoint_path}")
    print(f"Loss plot saved to: {loss_path}")
    print(f"Metrics plot saved to: {metrics_path}")
    print("\nDeep Neural Rocket Controller training finished successfully.")


if __name__ == "__main__":
    train()
