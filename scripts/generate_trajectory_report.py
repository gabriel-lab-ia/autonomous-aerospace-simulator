from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator
from aerospace_sim.vehicle.engine import RocketEngine


RESULTS_DIR = Path("docs/results")


def create_initial_state() -> RocketState:
    return RocketState(
        position=Vector3(0.0, 0.0, 100.0),
        velocity=Vector3(0.0, 0.0, -10.0),
        orientation=Vector3(0.0, 0.0, 0.0),
        angular_velocity=Vector3(0.0, 0.0, 0.0),
        fuel_mass=800.0,
    )


def create_simulator() -> BasicRocketSimulator:
    engine = RocketEngine(
        max_thrust=35000.0,
        fuel_burn_rate=2.5,
    )

    return BasicRocketSimulator(
        engine=engine,
        dry_mass=1200.0,
        dt=0.02,
    )


def run_trajectory(throttle: float, steps: int = 100) -> list[dict[str, float]]:
    state = create_initial_state()
    simulator = create_simulator()

    rows = []

    for step in range(steps + 1):
        rows.append(
            {
                "throttle": throttle,
                "step": step,
                "time_s": state.time,
                "altitude_m": state.position.z,
                "position_x_m": state.position.x,
                "position_y_m": state.position.y,
                "velocity_z_m_s": state.velocity.z,
                "speed_m_s": state.speed,
                "fuel_mass_kg": state.fuel_mass,
            }
        )

        if step < steps:
            state = simulator.step(state, throttle=throttle)

    return rows


def generate_trajectory_dataframe() -> pd.DataFrame:
    rows = []

    for throttle in [0.0, 0.5, 1.0]:
        rows.extend(run_trajectory(throttle=throttle, steps=100))

    return pd.DataFrame(rows)


def save_altitude_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))

    for throttle, group in df.groupby("throttle"):
        plt.plot(
            group["time_s"],
            group["altitude_m"],
            label=f"throttle={throttle}",
        )

    plt.title("Altitude Over Time by Throttle Level")
    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (m)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "trajectory_altitude_over_time.png", dpi=160)
    plt.close()


def save_velocity_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))

    for throttle, group in df.groupby("throttle"):
        plt.plot(
            group["time_s"],
            group["velocity_z_m_s"],
            label=f"throttle={throttle}",
        )

    plt.title("Vertical Velocity Over Time by Throttle Level")
    plt.xlabel("Time (s)")
    plt.ylabel("Vertical velocity (m/s)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "trajectory_velocity_over_time.png", dpi=160)
    plt.close()


def save_fuel_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))

    for throttle, group in df.groupby("throttle"):
        plt.plot(
            group["time_s"],
            group["fuel_mass_kg"],
            label=f"throttle={throttle}",
        )

    plt.title("Fuel Mass Over Time by Throttle Level")
    plt.xlabel("Time (s)")
    plt.ylabel("Fuel mass (kg)")
    plt.legend()
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "trajectory_fuel_over_time.png", dpi=160)
    plt.close()


def build_summary_table(df: pd.DataFrame) -> pd.DataFrame:
    summary_rows = []

    for throttle, group in df.groupby("throttle"):
        final = group.iloc[-1]

        summary_rows.append(
            {
                "throttle": throttle,
                "final_time_s": final["time_s"],
                "final_altitude_m": final["altitude_m"],
                "final_velocity_z_m_s": final["velocity_z_m_s"],
                "final_speed_m_s": final["speed_m_s"],
                "final_fuel_mass_kg": final["fuel_mass_kg"],
            }
        )

    return pd.DataFrame(summary_rows)


def save_markdown_report(summary: pd.DataFrame) -> None:
    table = summary.to_markdown(index=False)

    report = f"""# Trajectory Time-Series Experiment

This experiment records the full simulated trajectory over time for three throttle levels: `0.0`, `0.5`, and `1.0`.

Unlike the initial throttle comparison, this report tracks the evolution of:

- altitude
- vertical velocity
- total speed
- fuel mass
- simulation time

## Final-State Summary

{table}

## Altitude Over Time

![Altitude over time](trajectory_altitude_over_time.png)

## Vertical Velocity Over Time

![Vertical velocity over time](trajectory_velocity_over_time.png)

## Fuel Mass Over Time

![Fuel mass over time](trajectory_fuel_over_time.png)

## Engineering Interpretation

The trajectory curves validate the simulator as a time-dependent dynamical system.

- With `0.0` throttle, the rocket continues accelerating downward under gravity.
- With `0.5` throttle, thrust partially offsets gravity and reduces descent rate.
- With `1.0` throttle, thrust exceeds weight and reverses vertical velocity upward.

This confirms that the current simulation loop connects force, mass, acceleration, velocity, position, fuel consumption, and time through Euler integration.
"""

    (RESULTS_DIR / "trajectory_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = generate_trajectory_dataframe()
    summary = build_summary_table(df)

    df.to_csv(RESULTS_DIR / "trajectory_timeseries.csv", index=False)
    summary.to_csv(RESULTS_DIR / "trajectory_summary.csv", index=False)

    save_altitude_plot(df)
    save_velocity_plot(df)
    save_fuel_plot(df)
    save_markdown_report(summary)

    print("Trajectory report generated successfully.")
    print(summary)


if __name__ == "__main__":
    main()