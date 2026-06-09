from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.core.state import RocketState
from aerospace_sim.vehicle.engine import RocketEngine
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator


def create_initial_state() -> RocketState:
    return RocketState(
        position=Vector3(0.0, 0.0, 100.0),
        velocity=Vector3(0.0, 0.0, -10.0),
        orientation=Vector3(0.0, 0.0, 0.0),
        angular_velocity=Vector3(0.0, 0.0, 0.0),
        fuel_mass=800.0,
    )


def run_simulation(throttle: float, steps: int = 100) -> RocketState:
    state = create_initial_state()

    engine = RocketEngine(
        max_thrust=35000.0,
        fuel_burn_rate=2.5,
    )

    simulator = BasicRocketSimulator(
        engine=engine,
        dry_mass=1200.0,
        dt=0.02,
    )

    for _ in range(steps):
        state = simulator.step(state, throttle=throttle)

    return state


def main() -> None:
    throttle_levels = [0.0, 0.5, 1.0]

    print("Throttle comparison experiment")
    print("-" * 80)
    print(f"{'Throttle':>10} | {'Altitude (m)':>14} | {'Velocity Z (m/s)':>18} | {'Fuel (kg)':>10}")
    print("-" * 80)

    for throttle in throttle_levels:
        state = run_simulation(throttle=throttle)

        print(
            f"{throttle:>10.2f} | "
            f"{state.position.z:>14.4f} | "
            f"{state.velocity.z:>18.4f} | "
            f"{state.fuel_mass:>10.4f}"
        )


if __name__ == "__main__":
    main()