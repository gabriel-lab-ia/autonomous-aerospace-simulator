from aerospace_sim.control.pid_controller import PIDLandingController
from aerospace_sim.simulation.scenario import SimulationScenario


def test_pid_returns_bounded_throttle_for_default_state() -> None:
    controller = PIDLandingController.from_yaml()
    state = SimulationScenario.from_yaml().create_initial_state()

    assert 0.0 <= controller.compute_throttle(state) <= 1.0


def test_pid_integral_respects_anti_windup_limit() -> None:
    controller = PIDLandingController(ki=1.0, integral_limit=0.25)
    state = SimulationScenario.from_yaml().create_initial_state()

    for _ in range(1000):
        controller.compute_throttle(state)

    assert abs(controller.integral_error) <= controller.integral_limit
