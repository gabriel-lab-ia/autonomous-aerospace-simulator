from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.core.state import RocketState
from aerospace_sim.vehicle.engine import RocketEngine
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator


def main() -> None:
    state = RocketState(
        position=Vector3(0.0, 0.0, 100.0),
        velocity=Vector3(0.0, 0.0, -10.0),
        orientation=Vector3(0.0, 0.0, 0.0),
        angular_velocity=Vector3(0.0, 0.0, 0.0),
        fuel_mass=800.0,
    )

    engine = RocketEngine(
        max_thrust=35000.0,
        fuel_burn_rate=2.5,
    )

    simulator = BasicRocketSimulator(
        engine=engine,
        dry_mass=1200.0,
        dt=0.02,
    )

    steps = 100
    throttle = 0.5

    print("Running basic rocket simulation...")
    print(f"Initial altitude: {state.altitude:.4f} m")
    print(f"Initial speed: {state.speed:.4f} m/s")
    print()

    for _ in range(steps):
        state = simulator.step(state, throttle=throttle)

    print("Simulation finished.")
    print(f"Final position: {state.position}")
    print(f"Final velocity: {state.velocity}")
    print(f"Final altitude: {state.altitude:.4f} m")
    print(f"Final speed: {state.speed:.4f} m/s")
    print(f"Fuel mass: {state.fuel_mass:.4f} kg")
    print(f"Time: {state.time:.4f} s")


if __name__ == "__main__":
    main()