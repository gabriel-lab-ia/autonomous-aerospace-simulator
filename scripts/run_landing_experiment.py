import pandas as pd

from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator
from aerospace_sim.vehicle.engine import RocketEngine


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