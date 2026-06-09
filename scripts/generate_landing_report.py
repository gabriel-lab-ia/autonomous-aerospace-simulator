from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.environment.landing import evaluate_landing
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


def run_until_terminal(
    throttle: float,
    max_steps: int = 3000,
) -> tuple[RocketState, str]:
    state = create_initial_state()
    simulator = create_simulator()

    for _ in range(max_steps):
        state = simulator.step(state, throttle=throttle)

        if state.altitude <= 0.0:
            return state, "ground_contact"

    return state, "max_steps_reached"


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

    plt.figure(figsize=(9, 5))
    plt.bar(plot_df["throttle"].astype(str), plot_df["status_code"])
    plt.title("Landing Status by Fixed Throttle Level")
    plt.xlabel("Throttle")
    plt.ylabel("Status code")
    plt.yticks(
        [0, 1, 2],
        ["crashed", "landed", "still_flying"],
    )
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "landing_status_by_throttle.png", dpi=160)
    plt.close()


def save_velocity_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.bar(df["throttle"].astype(str), df["final_velocity_z_m_s"])
    plt.axhline(y=-2.0, linestyle="--", linewidth=1)
    plt.axhline(y=2.0, linestyle="--", linewidth=1)
    plt.title("Final Vertical Velocity by Fixed Throttle Level")
    plt.xlabel("Throttle")
    plt.ylabel("Final vertical velocity (m/s)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "landing_velocity_by_throttle.png", dpi=160)
    plt.close()


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
    save_markdown_report(df)

    print("Landing report generated successfully.")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
    