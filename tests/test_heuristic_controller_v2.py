from math import isclose

from aerospace_sim.control.heuristic_landing_controller_v2 import HeuristicLandingController
from aerospace_sim.simulation.scenario import SimulationScenario


def test_hover_throttle_uses_injected_vehicle_parameters() -> None:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    controller = HeuristicLandingController(
        dry_mass=scenario.dry_mass,
        max_thrust=scenario.max_thrust,
    )

    expected = ((scenario.dry_mass + scenario.fuel_mass) * 9.80665) / scenario.max_thrust

    assert isclose(controller._estimated_hover_throttle(state), expected)
