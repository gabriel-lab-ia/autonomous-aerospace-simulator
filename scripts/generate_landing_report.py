from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.core.state import RocketState
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.visualization.dark_style import COLORS, save_dark_figure, style_axis
from aerospace_sim.visualization.phase_space import save_landing_summary_3d


RESULTS_DIR = Path("docs/results")


def run_until_terminal(
    throttle: float,
    max_steps: int | None = None,
) -> tuple[RocketState, str]:
    scenario = SimulationScenario.from_yaml()
    run = run_scenario(
        scenario,
        fixed_throttle=throttle,
        max_steps=max_steps,
        stop_on_ground=True,
    )
    return run.final_state, run.terminal_reason


def generate_landing_dataframe() -> pd.DataFrame:
    rows = []

    for throttle in [0.0, 0.25, 0.5, 0.75, 1.0]:
        final_state, terminal_reason = run_until_terminal(throttle=throttle)
        evaluation = evaluate_landing(final_state)

        rows.append(
            {
                "throttle": throttle,
                "status": evaluation.status.value,
                "reason": evaluation.reason,
                "terminal_reason": terminal_reason,
                "final_altitude_m": evaluation.final_altitude_m,
                "final_velocity_z_m_s": evaluation.final_velocity_z_m_s,
                "final_speed_m_s": evaluation.final_speed_m_s,
                "final_time_s": evaluation.final_time_s,
                "final_fuel_mass_kg": evaluation.final_fuel_mass_kg,
            }
        )

    return pd.DataFrame(rows)


def save_status_plot(df: pd.DataFrame) -> None:
    status_map = {
        "crashed": 0,
        "landed": 1,
        "still_flying": 2,
    }

    plot_df = df.copy()
    plot_df["status_code"] = plot_df["status"].map(status_map)

    figure, axis = plt.subplots(figsize=(9, 5))
    axis.bar(
        plot_df["throttle"].astype(str),
        plot_df["status_code"],
        color=COLORS,
    )
    axis.set_title("Landing Status by Fixed Throttle Level")
    axis.set_xlabel("Throttle")
    axis.set_ylabel("Status code")
    axis.set_yticks(
        [0, 1, 2],
        ["crashed", "landed", "still_flying"],
    )
    style_axis(axis, grid=False)
    save_dark_figure(figure, RESULTS_DIR / "landing_status_by_throttle.png")
    plt.close(figure)


def save_velocity_plot(df: pd.DataFrame) -> None:
    figure, axis = plt.subplots(figsize=(9, 5))
    axis.bar(df["throttle"].astype(str), df["final_velocity_z_m_s"], color=COLORS)
    axis.axhline(y=-2.0, color="#FF4D8D", linestyle="--", linewidth=1)
    axis.axhline(y=2.0, color="#7CFF6B", linestyle="--", linewidth=1)
    axis.set_title("Final Vertical Velocity by Fixed Throttle Level")
    axis.set_xlabel("Throttle")
    axis.set_ylabel("Final vertical velocity (m/s)")
    style_axis(axis, grid=False)
    save_dark_figure(figure, RESULTS_DIR / "landing_velocity_by_throttle.png")
    plt.close(figure)


def save_3d_summary_plot(df: pd.DataFrame) -> None:
    save_landing_summary_3d(
        df,
        RESULTS_DIR / "landing_summary_3d.png",
        "Fixed-Throttle Landing Outcomes in 3D",
    )


def save_markdown_report(df: pd.DataFrame) -> None:
    table = df.to_markdown(index=False)

    report = f"""# Landing Evaluation Experiment

This experiment evaluates whether fixed throttle values can land the rocket safely.

The simulation classifies each run as:

- `landed`: touchdown occurred within safe velocity limits
- `crashed`: touchdown occurred with excessive velocity
- `still_flying`: the rocket did not reach the ground before the maximum simulation time

## Results

{table}

## Landing Status by Throttle

![Landing status by throttle](landing_status_by_throttle.png)

## Final Vertical Velocity by Throttle

![Final vertical velocity by throttle](landing_velocity_by_throttle.png)

## 3D Landing Outcome Space

![3D landing outcome space](landing_summary_3d.png)

This R3 summary combines throttle, final vertical velocity, and final altitude.
Color represents final simulation time.

## Engineering Interpretation

The experiment shows that fixed throttle is not sufficient for reliable landing.

- Low throttle values result in crashes because thrust is not enough to slow descent.
- High throttle values keep the rocket flying upward instead of landing.
- A safe landing requires dynamic control, not constant thrust.

This motivates the next engineering step: implementing a controller that adjusts throttle based on altitude and vertical velocity.
"""

    (RESULTS_DIR / "landing_experiment.md").write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    df = generate_landing_dataframe()

    df.to_csv(RESULTS_DIR / "landing_experiment.csv", index=False)

    save_status_plot(df)
    save_velocity_plot(df)
    save_3d_summary_plot(df)
    save_markdown_report(df)

    print("Landing report generated successfully.")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
