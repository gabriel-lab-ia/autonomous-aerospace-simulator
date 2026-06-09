from aerospace_sim.simulation.scenario import SimulationScenario


def main() -> None:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    simulator = scenario.create_simulator()

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
