from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from aerospace_sim.core.state import RocketState
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TelemetryRecorder


class ThrottleController(Protocol):
    """Minimal controller contract shared by heuristic and future PID control."""

    def compute_throttle(self, state: RocketState) -> float: ...


@dataclass(frozen=True)
class SimulationRun:
    initial_state: RocketState
    final_state: RocketState
    telemetry: TelemetryRecorder
    terminal_reason: str


def run_scenario(
    scenario: SimulationScenario,
    *,
    controller: ThrottleController | None = None,
    fixed_throttle: float | None = None,
    max_steps: int | None = None,
    stop_on_ground: bool = False,
    record_final_state: bool = False,
) -> SimulationRun:
    """Execute a configured scenario with one explicit throttle source."""
    if (controller is None) == (fixed_throttle is None):
        raise ValueError("Provide exactly one of controller or fixed_throttle.")

    step_limit = max_steps if max_steps is not None else scenario.max_steps
    if step_limit <= 0:
        raise ValueError("Simulation max_steps must be positive.")

    initial_state = scenario.create_initial_state()
    state = initial_state.copy()
    simulator = scenario.create_simulator()
    recorder = TelemetryRecorder()
    throttle = fixed_throttle if fixed_throttle is not None else 0.0
    terminal_reason = "max_steps_reached"

    for step in range(step_limit):
        if controller is not None:
            throttle = controller.compute_throttle(state)

        recorder.record(step, state, throttle)
        state = simulator.step(state, throttle)

        if stop_on_ground and state.altitude <= 0.0:
            terminal_reason = "ground_contact"
            break

    if record_final_state:
        recorder.record(len(recorder), state, throttle)

    return SimulationRun(
        initial_state=initial_state,
        final_state=state,
        telemetry=recorder,
        terminal_reason=terminal_reason,
    )
