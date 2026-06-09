import pandas as pd

from aerospace_sim.control.heuristic_landing_controller import HeuristicLandingController
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


def run_controlled_landing(max_steps: int = 3000) -> tuple[RocketState, pd.DataFrame]:
    state = create_initial_state()
    simulator = create_simulator()
    controller = HeuristicLandingController()

    rows = []

    for step in range(max_steps):
        throttle = controller.compute_throttle(state)

        rows.append(
            {
                "step": step,
                "time_s": state.time,
                "altitude_m": state.altitude,
                "velocity_z_m_s": state.velocity.z,
                "speed_m_s": state.speed,
                "fuel_mass_kg": state.fuel_mass,
                "throttle": throttle,
            }
        )

        state = simulator.step(state, throttle=throttle)

        if state.altitude <= 0.0:
            break

    return state, pd.DataFrame(rows)


def main() -> None:
    final_state, telemetry = run_controlled_landing()
    evaluation = evaluate_landing(final_state)

    print("Heuristic landing experiment")
    print("-" * 80)
    print(f"Status: {evaluation.status.value}")
    print(f"Reason: {evaluation.reason}")
    print(f"Final altitude: {evaluation.final_altitude_m:.4f} m")
    print(f"Final vertical velocity: {evaluation.final_velocity_z_m_s:.4f} m/s")
    print(f"Final speed: {evaluation.final_speed_m_s:.4f} m/s")
    print(f"Final time: {evaluation.final_time_s:.4f} s")
    print(f"Final fuel mass: {evaluation.final_fuel_mass_kg:.4f} kg")
    print()
    print("Last telemetry rows:")
    print(telemetry.tail(10).to_string(index=False))


if __name__ == "__main__":
    main()