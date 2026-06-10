from __future__ import annotations

import argparse
from pathlib import Path

from aerospace_sim.control.neural_controller import NeuralController
from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario


OUTPUT_PATH = Path("outputs/neural_controller/neural_simulation_telemetry.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run experimental neural control.")
    parser.add_argument("--checkpoint", type=Path)
    parser.add_argument(
        "--allow-untrained",
        action="store_true",
        help="Explicitly allow random weights for integration experiments.",
    )
    parser.add_argument("--max-steps", type=int, default=500)
    args = parser.parse_args()

    controller = NeuralController(
        checkpoint_path=args.checkpoint,
        allow_untrained=args.allow_untrained,
    )
    if not controller.is_trained:
        print("WARNING: using an untrained random model; control quality is not expected.")

    scenario = SimulationScenario.from_yaml()
    run = run_scenario(
        scenario,
        controller=controller,
        max_steps=args.max_steps,
        stop_on_ground=True,
        record_final_state=True,
    )
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    run.telemetry.to_dataframe().to_csv(OUTPUT_PATH, index=False)
    print(f"checkpoint: {args.checkpoint or 'none (untrained experimental mode)'}")
    print(f"terminal reason: {run.terminal_reason}")
    print(f"final altitude: {run.final_state.altitude:.3f} m")
    print(f"final vertical velocity: {run.final_state.velocity.z:.3f} m/s")
    print(f"telemetry: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
