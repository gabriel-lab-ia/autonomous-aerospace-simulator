from __future__ import annotations

import argparse
import json
from pathlib import Path

import matplotlib.pyplot as plt
import torch
from torch import nn
from torch.utils.data import DataLoader, random_split

from aerospace_sim.learning.neural_controller import (
    NeuralRocketControllerNet,
    RocketControlDataset,
    model_parameter_report,
)


OUTPUT_DIR = Path("outputs/neural_controller")
CHECKPOINT_PATH = OUTPUT_DIR / "neural_controller.pt"
SUMMARY_PATH = OUTPUT_DIR / "training_summary.json"
LOSS_PLOT_PATH = OUTPUT_DIR / "loss_curves.png"
THROTTLE_PLOT_PATH = OUTPUT_DIR / "throttle_predictions.png"


def evaluate(
    model: NeuralRocketControllerNet,
    loader: DataLoader,
    device: torch.device,
) -> dict[str, float]:
    model.eval()
    total_loss = total_throttle_error = total_stability_error = correct = count = 0.0
    mse = nn.MSELoss(reduction="sum")
    cross_entropy = nn.CrossEntropyLoss(reduction="sum")
    with torch.no_grad():
        for states, throttle, stability, phase in loader:
            states, throttle = states.to(device), throttle.to(device)
            stability, phase = stability.to(device), phase.to(device)
            throttle_prediction, stability_prediction, phase_logits = model(states)
            total_loss += (
                mse(throttle_prediction, throttle)
                + mse(stability_prediction, stability)
                + 0.25 * cross_entropy(phase_logits, phase)
            ).item()
            total_throttle_error += torch.abs(throttle_prediction - throttle).sum().item()
            total_stability_error += torch.abs(stability_prediction - stability).sum().item()
            correct += (phase_logits.argmax(dim=1) == phase).sum().item()
            count += states.shape[0]
    return {
        "loss": total_loss / count,
        "throttle_mae": total_throttle_error / count,
        "stability_mae": total_stability_error / count,
        "phase_accuracy": correct / count,
    }


def save_plots(
    train_losses: list[float],
    validation_losses: list[float],
    model: NeuralRocketControllerNet,
    validation_loader: DataLoader,
    device: torch.device,
) -> None:
    figure, axis = plt.subplots()
    axis.plot(train_losses, label="train")
    axis.plot(validation_losses, label="validation")
    axis.set(xlabel="epoch", ylabel="multi-task loss", title="Neural controller training")
    axis.legend()
    figure.tight_layout()
    figure.savefig(LOSS_PLOT_PATH, dpi=160)
    plt.close(figure)

    states, throttle, _, _ = next(iter(validation_loader))
    with torch.no_grad():
        predicted, _, _ = model(states.to(device))
        predicted = predicted.cpu().numpy()
    figure, axis = plt.subplots()
    axis.scatter(throttle.numpy(), predicted, alpha=0.5)
    axis.plot([0, 1], [0, 1], linestyle="--", color="black")
    axis.set(xlabel="synthetic target throttle", ylabel="predicted throttle")
    figure.tight_layout()
    figure.savefig(THROTTLE_PLOT_PATH, dpi=160)
    plt.close(figure)


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the supervised neural controller.")
    parser.add_argument("--epochs", type=int, default=6)
    parser.add_argument("--samples", type=int, default=4096)
    parser.add_argument("--batch-size", type=int, default=256)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    if args.epochs <= 0 or args.samples < 10 or args.batch_size <= 0:
        parser.error("epochs and batch-size must be positive; samples must be at least 10")

    torch.manual_seed(args.seed)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    dataset = RocketControlDataset(n_samples=args.samples, seed=args.seed)
    split = int(args.samples * 0.8)
    train_dataset, validation_dataset = random_split(
        dataset,
        [split, args.samples - split],
        generator=torch.Generator().manual_seed(args.seed),
    )
    train_loader = DataLoader(train_dataset, batch_size=args.batch_size, shuffle=True)
    validation_loader = DataLoader(validation_dataset, batch_size=args.batch_size)

    model = NeuralRocketControllerNet().to(device)
    optimizer = torch.optim.Adam(model.parameters(), lr=3e-4)
    mse = nn.MSELoss()
    cross_entropy = nn.CrossEntropyLoss()
    train_losses: list[float] = []
    validation_losses: list[float] = []

    for epoch in range(args.epochs):
        model.train()
        epoch_loss = 0.0
        for batch in train_loader:
            batch = tuple(value.to(device) for value in batch)
            throttle_prediction, stability_prediction, phase_logits = model(batch[0])
            loss = (
                mse(throttle_prediction, batch[1])
                + mse(stability_prediction, batch[2])
                + 0.25 * cross_entropy(phase_logits, batch[3])
            )
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()
            epoch_loss += loss.item() * batch[0].shape[0]
        train_losses.append(epoch_loss / len(train_dataset))
        validation = evaluate(model, validation_loader, device)
        validation_losses.append(validation["loss"])
        print(
            f"epoch {epoch + 1}/{args.epochs}: train={train_losses[-1]:.6f} "
            f"validation={validation_losses[-1]:.6f}"
        )

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    final_metrics = evaluate(model, validation_loader, device)
    parameter_report = model_parameter_report(model)
    metadata = {
        "training_kind": "supervised pretraining on synthetic telemetry",
        "samples": args.samples,
        "epochs": args.epochs,
        "seed": args.seed,
    }
    torch.save({"model_state_dict": model.state_dict(), "metadata": metadata}, CHECKPOINT_PATH)
    save_plots(train_losses, validation_losses, model, validation_loader, device)
    summary = {
        "device": str(device),
        "epochs": args.epochs,
        "samples": args.samples,
        "train_samples": len(train_dataset),
        "validation_samples": len(validation_dataset),
        "final_train_loss": train_losses[-1],
        "final_validation_loss": final_metrics["loss"],
        "final_throttle_mae": final_metrics["throttle_mae"],
        "final_stability_mae": final_metrics["stability_mae"],
        "final_phase_accuracy": final_metrics["phase_accuracy"],
        "checkpoint_path": str(CHECKPOINT_PATH),
        "plot_paths": [str(LOSS_PLOT_PATH), str(THROTTLE_PLOT_PATH)],
        **parameter_report,
        **metadata,
    }
    SUMMARY_PATH.write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
