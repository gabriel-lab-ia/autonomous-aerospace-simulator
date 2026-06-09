from pathlib import Path

import pandas as pd

from aerospace_sim.simulation.scenario import SimulationScenario


RESULTS_DIR = Path("docs/results")


def build_state_vector_table() -> pd.DataFrame:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    labels = [
        "position_x_m",
        "position_y_m",
        "altitude_m",
        "velocity_x_m_s",
        "velocity_y_m_s",
        "velocity_z_m_s",
        "roll_rad",
        "pitch_rad",
        "yaw_rad",
        "angular_velocity_x_rad_s",
        "angular_velocity_y_rad_s",
        "angular_velocity_z_rad_s",
        "fuel_mass_kg",
    ]
    return pd.DataFrame({"index": range(13), "state": labels, "value": state.to_vector()})


def build_one_step_transition_table() -> pd.DataFrame:
    scenario = SimulationScenario.from_yaml()
    rows = []

    for throttle in [0.0, 0.5, 1.0]:
        initial_state = scenario.create_initial_state()
        final_state = scenario.create_simulator().step(initial_state, throttle)
        rows.append(
            {
                "throttle": throttle,
                "initial_altitude_m": initial_state.altitude,
                "initial_velocity_z_m_s": initial_state.velocity.z,
                "next_altitude_m": final_state.altitude,
                "next_velocity_z_m_s": final_state.velocity.z,
                "next_fuel_mass_kg": final_state.fuel_mass,
            }
        )

    return pd.DataFrame(rows)


def save_report(state_vector: pd.DataFrame, transition: pd.DataFrame) -> None:
    report = f"""# Numerical Validation Matrices

This report exposes the numerical contracts used by the automated tests and
simulation experiments. Values are generated from `configs/default.yaml`.

## Initial State Vector

`RocketState.to_vector()` produces a 13 x 1 numerical vector for future control
and machine-learning interfaces.

{state_vector.to_markdown(index=False)}

## One-Step Transition Matrix

Each row applies one simulator step (`dt = 0.02 s`) from the same initial state.
The matrix demonstrates how throttle changes acceleration and fuel consumption
while gravity remains active.

{transition.to_markdown(index=False)}

## Technical Interpretation

- `throttle = 0.0`: velocity becomes more negative because only gravity acts.
- `throttle = 0.5`: partial thrust reduces the downward acceleration.
- `throttle = 1.0`: full thrust produces upward acceleration, but one step is
  not long enough to reverse the initial downward velocity.
- Fuel consumption is proportional to throttle and is bounded by available fuel.
- Automated tests separately verify vector operations, gravity direction,
  throttle clamping, fuel exhaustion, ground clamping, scenario validation,
  telemetry schema, and landing classification.
"""
    (RESULTS_DIR / "numerical_validation.md").write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    state_vector = build_state_vector_table()
    transition = build_one_step_transition_table()
    state_vector.to_csv(RESULTS_DIR / "initial_state_vector.csv", index=False)
    transition.to_csv(RESULTS_DIR / "one_step_transition_matrix.csv", index=False)
    save_report(state_vector, transition)
    print("Numerical validation report generated successfully.")


if __name__ == "__main__":
    main()
