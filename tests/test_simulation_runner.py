import pytest

from aerospace_sim.core.state import RocketState
from aerospace_sim.simulation.runner import run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario


class FullThrottleController:
    def compute_throttle(self, state: RocketState) -> float:
        return 1.0


def test_runner_records_initial_steps_and_optional_final_state() -> None:
    scenario = SimulationScenario.from_yaml().with_overrides(max_steps=5)

    run = run_scenario(
        scenario,
        fixed_throttle=0.5,
        record_final_state=True,
    )

    assert len(run.telemetry) == 6
    assert run.telemetry.records[0].time_s == 0.0
    assert run.telemetry.records[-1].time_s == run.final_state.time
    assert run.terminal_reason == "max_steps_reached"


def test_runner_stops_on_ground_and_supports_controller_contract() -> None:
    scenario = SimulationScenario.from_yaml().with_overrides(
        initial_altitude_m=0.1,
        initial_vertical_velocity_m_s=-10.0,
    )

    run = run_scenario(
        scenario,
        controller=FullThrottleController(),
        stop_on_ground=True,
    )

    assert run.final_state.altitude == 0.0
    assert run.terminal_reason == "ground_contact"
    assert run.telemetry.records[0].throttle == 1.0


def test_runner_requires_exactly_one_throttle_source() -> None:
    scenario = SimulationScenario.from_yaml()

    with pytest.raises(ValueError, match="exactly one"):
        run_scenario(scenario)

    with pytest.raises(ValueError, match="exactly one"):
        run_scenario(
            scenario,
            controller=FullThrottleController(),
            fixed_throttle=0.5,
        )
