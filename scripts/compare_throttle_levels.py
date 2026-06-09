from aerospace_sim.core.state import RocketState
from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario


def run_simulation(throttle: float, steps: int = 100) -> RocketState:
    scenario = SimulationScenario.from_yaml()
    return run_scenario(
        scenario,
        fixed_throttle=throttle,
        max_steps=steps,
    ).final_state


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
