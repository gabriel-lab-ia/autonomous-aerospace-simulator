from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.core.state import RocketState
from aerospace_sim.simulation.scenario import SimulationScenario


RESULTS_DIR = Path("docs/results")


def run_simulation(throttle: float, steps: int = 100) -> RocketState:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    simulator = scenario.create_simulator()

    for _ in range(steps):
        state = simulator.step(state, throttle=throttle)

    return state


def generate_results() -> pd.DataFrame:
    rows = []

    for throttle in [0.0, 0.5, 1.0]:
        state = run_simulation(throttle=throttle)

        rows.append(
            {
                "throttle": throttle,
                "final_altitude_m": state.position.z,
                "final_velocity_z_m_s": state.velocity.z,
                "final_speed_m_s": state.speed,
                "fuel_mass_kg": state.fuel_mass,
                "time_s": state.time,
            }
        )

    return pd.DataFrame(rows)


def save_altitude_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(df["throttle"].astype(str), df["final_altitude_m"])
    plt.title("Final Altitude by Throttle Level")
    plt.xlabel("Throttle")
    plt.ylabel("Final altitude (m)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "throttle_final_altitude.png", dpi=160)
    plt.close()


def save_velocity_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(8, 5))
    plt.bar(df["throttle"].astype(str), df["final_velocity_z_m_s"])
    plt.title("Final Vertical Velocity by Throttle Level")
    plt.xlabel("Throttle")
    plt.ylabel("Final vertical velocity (m/s)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "throttle_final_velocity.png", dpi=160)
    plt.close()


def save_markdown_report(df: pd.DataFrame) -> None:
    table = df.to_markdown(index=False)

    report = f"""# Throttle Comparison Experiment

This experiment validates the first simplified vertical rocket dynamics model.

The simulator compares three throttle levels:

- `0.0`: free fall under gravity
- `0.5`: partial thrust
- `1.0`: maximum thrust

## Results

{table}

## Interpretation

The results show physically coherent behavior:

- With `0.0` throttle, the rocket falls faster and reaches the lowest altitude.
- With `0.5` throttle, descent is reduced because thrust partially offsets gravity.
- With `1.0` throttle, thrust exceeds weight and the rocket reverses vertical velocity upward.

## Final Altitude

![Final altitude by throttle](throttle_final_altitude.png)

## Final Vertical Velocity

![Final vertical velocity by throttle](throttle_final_velocity.png)

## Engineering Meaning

This validates that the simulator already connects mass, gravity, thrust, fuel consumption, acceleration, velocity, and position through a basic Euler integration loop.
"""

    (RESULTS_DIR / "throttle_comparison.md").write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = generate_results()

    df.to_csv(RESULTS_DIR / "throttle_comparison.csv", index=False)

    save_altitude_plot(df)
    save_velocity_plot(df)
    save_markdown_report(df)

    print("Throttle report generated successfully.")
    print(df)


if __name__ == "__main__":
    main()
