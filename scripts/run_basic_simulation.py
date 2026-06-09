from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario


def main() -> None:
    scenario = SimulationScenario.from_yaml()
    initial_state = scenario.create_initial_state()

    steps = 100
    throttle = 0.5

    print("Running basic rocket simulation...")
    print(f"Initial altitude: {initial_state.altitude:.4f} m")
    print(f"Initial speed: {initial_state.speed:.4f} m/s")
    print()

    run = run_scenario(scenario, fixed_throttle=throttle, max_steps=steps)
    state = run.final_state

    print("Simulation finished.")
    print(f"Final position: {state.position}")
    print(f"Final velocity: {state.velocity}")
    print(f"Final altitude: {state.altitude:.4f} m")
    print(f"Final speed: {state.speed:.4f} m/s")
    print(f"Fuel mass: {state.fuel_mass:.4f} kg")
    print(f"Time: {state.time:.4f} s")


if __name__ == "__main__":
    main()
