from pathlib import Path

from aerospace_sim.learning.telemetry_preprocessing import prepare_training_table


TRAJECTORY_DIR = Path("outputs/controller_benchmark/trajectories")
OUTPUT_PATH = Path("outputs/neural_controller/preprocessed_controller_telemetry.csv")


if __name__ == "__main__":
    sources = sorted(TRAJECTORY_DIR.glob("*.csv"))
    table = prepare_training_table(sources, output_path=OUTPUT_PATH)
    print(f"prepared {len(table)} simulated telemetry rows at {OUTPUT_PATH}")
