import pandas as pd

from aerospace_sim.control.heuristic_landing_controller_v2 import HeuristicLandingController
from aerospace_sim.core.state import RocketState
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TelemetryRecorder


def run_controlled_landing(max_steps: int | None = None) -> tuple[RocketState, pd.DataFrame]:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    simulator = scenario.create_simulator()
    controller = HeuristicLandingController(
        dry_mass=scenario.dry_mass,
        max_thrust=scenario.max_thrust,
    )
    recorder = TelemetryRecorder()

    for step in range(max_steps or scenario.max_steps):
        throttle = controller.compute_throttle(state)

        recorder.record(step, state, throttle)

        state = simulator.step(state, throttle=throttle)

        if state.altitude <= 0.0:
            break

    return state, recorder.to_dataframe()


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
