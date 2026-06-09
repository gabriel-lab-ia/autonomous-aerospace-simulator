from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.visualization.dark_style import COLORS, save_dark_figure, style_axis
from aerospace_sim.visualization.phase_space import save_trajectory_phase_space_3d


RESULTS_DIR = Path("docs/results")


def run_trajectory(throttle: float, steps: int = 100) -> list[dict[str, float]]:
    scenario = SimulationScenario.from_yaml()
    run = run_scenario(
        scenario,
        fixed_throttle=throttle,
        max_steps=steps,
        record_final_state=True,
    )
    return run.telemetry.to_dataframe().to_dict(orient="records")


def generate_trajectory_dataframe() -> pd.DataFrame:
    rows = []

    for throttle in [0.0, 0.5, 1.0]:
        rows.extend(run_trajectory(throttle=throttle, steps=100))

    return pd.DataFrame(rows)


def save_altitude_plot(df: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(9, 5))

    for color, (throttle, group) in zip(COLORS, df.groupby("throttle")):
        axis.plot(
            group["time_s"],
            group["altitude_m"],
            label=f"throttle={throttle}",
            color=color,
        )

    axis.set_title("Altitude Over Time by Throttle Level")
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Altitude (m)")
    axis.legend()
    style_axis(axis)
    save_dark_figure(figure, RESULTS_DIR / "trajectory_altitude_over_time.png")
    plt.close(figure)


def save_velocity_plot(df: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(9, 5))

    for color, (throttle, group) in zip(COLORS, df.groupby("throttle")):
        axis.plot(
            group["time_s"],
            group["velocity_z_m_s"],
            label=f"throttle={throttle}",
            color=color,
        )

    axis.set_title("Vertical Velocity Over Time by Throttle Level")
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Vertical velocity (m/s)")
    axis.legend()
    style_axis(axis)
    save_dark_figure(figure, RESULTS_DIR / "trajectory_velocity_over_time.png")
    plt.close(figure)


def save_fuel_plot(df: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(9, 5))

    for color, (throttle, group) in zip(COLORS, df.groupby("throttle")):
        axis.plot(
            group["time_s"],
            group["fuel_mass_kg"],
            label=f"throttle={throttle}",
            color=color,
        )

    axis.set_title("Fuel Mass Over Time by Throttle Level")
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Fuel mass (kg)")
    axis.legend()
    style_axis(axis)
    save_dark_figure(figure, RESULTS_DIR / "trajectory_fuel_over_time.png")
    plt.close(figure)


def save_phase_space_plot(df: pd.DataFrame) -> None:
    save_trajectory_phase_space_3d(
        df,
        RESULTS_DIR / "trajectory_phase_space_3d.png",
        "Fixed-Throttle Trajectories in 3D Phase Space",
        group_column="throttle",
    )


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

## 3D Phase Space

![Trajectory phase space](trajectory_phase_space_3d.png)

This 3D plot uses time, altitude, and vertical velocity. It visualizes the current
vertical dynamics without implying lateral motion that the simulator does not yet model.

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
    save_phase_space_plot(df)
    save_markdown_report(summary)

    print("Trajectory report generated successfully.")
    print(summary)


if __name__ == "__main__":
    main()
