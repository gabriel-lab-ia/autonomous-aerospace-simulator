from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.control.heuristic_landing_controller_v2 import HeuristicLandingController
from aerospace_sim.core.state import RocketState
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TelemetryRecorder
from aerospace_sim.visualization.dark_style import COLORS, save_dark_figure, style_axis
from aerospace_sim.visualization.phase_space import (
    save_control_state_3d,
    save_trajectory_phase_space_3d,
)


RESULTS_DIR = Path("docs/results")


def run_experiment(max_steps: int | None = None) -> tuple[RocketState, pd.DataFrame]:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    simulator = scenario.create_simulator()
    controller = HeuristicLandingController(
        dry_mass=scenario.dry_mass,
        max_thrust=scenario.max_thrust,
    )
    recorder = TelemetryRecorder()

    for step in range(max_steps or scenario.max_steps):
        throttle = controller.compute_throttle(state)

        recorder.record(step, state, throttle)

        state = simulator.step(state, throttle=throttle)

        if state.altitude <= 0.0:
            break

    return state, recorder.to_dataframe()


def save_altitude_plot(df: pd.DataFrame) -> None:
    save_time_series_plot(
        df,
        column="altitude_m",
        title="Heuristic Controller V2 - Altitude Over Time",
        ylabel="Altitude (m)",
        output_name="heuristic_v2_altitude_over_time.png",
        color=COLORS[0],
    )


def save_velocity_plot(df: pd.DataFrame) -> None:
    save_time_series_plot(
        df,
        column="velocity_z_m_s",
        title="Heuristic Controller V2 - Vertical Velocity Over Time",
        ylabel="Vertical velocity (m/s)",
        output_name="heuristic_v2_velocity_over_time.png",
        color=COLORS[1],
    )


def save_throttle_plot(df: pd.DataFrame) -> None:
    save_time_series_plot(
        df,
        column="throttle",
        title="Heuristic Controller V2 - Throttle Over Time",
        ylabel="Throttle",
        output_name="heuristic_v2_throttle_over_time.png",
        color=COLORS[2],
    )


def save_fuel_plot(df: pd.DataFrame) -> None:
    save_time_series_plot(
        df,
        column="fuel_mass_kg",
        title="Heuristic Controller V2 - Fuel Mass Over Time",
        ylabel="Fuel mass (kg)",
        output_name="heuristic_v2_fuel_over_time.png",
        color=COLORS[3],
    )


def save_time_series_plot(
    df: pd.DataFrame,
    *,
    column: str,
    title: str,
    ylabel: str,
    output_name: str,
    color: str,
) -> None:
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.plot(df["time_s"], df[column], color=color)
    axis.set_title(title)
    axis.set_xlabel("Time (s)")
    axis.set_ylabel(ylabel)
    style_axis(axis)
    save_dark_figure(figure, RESULTS_DIR / output_name)
    plt.close(figure)


def save_3d_plots(df: pd.DataFrame) -> None:
    save_trajectory_phase_space_3d(
        df,
        RESULTS_DIR / "heuristic_v2_phase_space_3d.png",
        "Heuristic V2 Trajectory in 3D Phase Space",
    )
    save_control_state_3d(
        df,
        RESULTS_DIR / "heuristic_v2_control_state_3d.png",
        "Heuristic V2 Controller State Space",
    )


def save_report(evaluation, telemetry: pd.DataFrame) -> None:
    summary = pd.DataFrame(
        [
            {
                "status": evaluation.status.value,
                "final_altitude_m": evaluation.final_altitude_m,
                "final_velocity_z_m_s": evaluation.final_velocity_z_m_s,
                "final_speed_m_s": evaluation.final_speed_m_s,
                "final_time_s": evaluation.final_time_s,
                "final_fuel_mass_kg": evaluation.final_fuel_mass_kg,
            }
        ]
    )

    summary.to_csv(RESULTS_DIR / "heuristic_v2_summary.csv", index=False)

    table = summary.to_markdown(index=False)

    report = f"""# Heuristic Landing Controller V2 Experiment

This experiment evaluates the second heuristic landing controller.

The controller is dynamic: it reads the rocket state at each simulation step and adjusts throttle based on altitude and vertical velocity.

## Final Result

{table}

## Plots

### Altitude Over Time

![Altitude over time](heuristic_v2_altitude_over_time.png)

### Vertical Velocity Over Time

![Vertical velocity over time](heuristic_v2_velocity_over_time.png)

### Throttle Over Time

![Throttle over time](heuristic_v2_throttle_over_time.png)

### Fuel Mass Over Time

![Fuel mass over time](heuristic_v2_fuel_over_time.png)

### 3D Trajectory Phase Space

![3D trajectory phase space](heuristic_v2_phase_space_3d.png)

### 3D Controller State Space

![3D controller state space](heuristic_v2_control_state_3d.png)

## Engineering Interpretation

The V2 heuristic controller does not land the rocket.

Instead, it becomes too aggressive and keeps throttle near maximum for too long. This causes a runaway ascent: the rocket keeps accelerating upward and ends the simulation far above the landing zone.

This is an important failed-control result.

It shows that avoiding crash is not enough. A valid landing controller must also regulate ascent, descent rate, and throttle smoothness near the landing zone.

## Next Step

The next engineering step is to move from heuristic control to a more stable controller:

- tune the heuristic controller with softer throttle corrections
- introduce a PID controller
- penalize upward velocity and excessive altitude gain
- eventually train a reinforcement learning policy using the simulator telemetry
"""

    (RESULTS_DIR / "heuristic_v2_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    final_state, telemetry = run_experiment()
    evaluation = evaluate_landing(final_state)

    telemetry.to_csv(RESULTS_DIR / "heuristic_v2_telemetry.csv", index=False)

    save_altitude_plot(telemetry)
    save_velocity_plot(telemetry)
    save_throttle_plot(telemetry)
    save_fuel_plot(telemetry)
    save_3d_plots(telemetry)
    save_report(evaluation, telemetry)

    print("Heuristic V2 report generated successfully.")
    print(f"Status: {evaluation.status.value}")
    print(f"Final altitude: {evaluation.final_altitude_m:.4f} m")
    print(f"Final vertical velocity: {evaluation.final_velocity_z_m_s:.4f} m/s")
    print(f"Final fuel mass: {evaluation.final_fuel_mass_kg:.4f} kg")


if __name__ == "__main__":
    main()
