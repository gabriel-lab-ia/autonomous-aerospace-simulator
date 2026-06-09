import pandas as pd

from aerospace_sim.core.state import RocketState
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario


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


def main() -> None:
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

    df = pd.DataFrame(rows)

    print("Landing experiment")
    print("-" * 100)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
