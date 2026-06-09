from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from aerospace_sim.control.heuristic_landing_controller import HeuristicLandingController
from aerospace_sim.core.state import RocketState
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TelemetryRecord, TelemetryRecorder


class ThrottleController(Protocol):
    def compute_throttle(self, state: RocketState) -> float: ...


@dataclass(frozen=True)
class SimulationExecution:
    simulation_type: str
    status: str
    reason: str | None
    initial_state: RocketState
    final_state: RocketState
    telemetry: tuple[TelemetryRecord, ...]
    metadata_json: dict[str, Any]


def run_basic_simulation(
    *,
    initial_altitude_m: float,
    initial_vertical_velocity_m_s: float,
    initial_fuel_mass_kg: float,
    throttle: float,
    steps: int,
    dt: float,
) -> SimulationExecution:
    scenario = _build_scenario(
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        max_steps=steps,
        dt=dt,
    )
    initial_state = scenario.create_initial_state()
    state = initial_state.copy()
    simulator = scenario.create_simulator()
    recorder = TelemetryRecorder()

    for step in range(steps):
        recorder.record(step, state, throttle)
        state = simulator.step(state, throttle)
    recorder.record(steps, state, throttle)

    return SimulationExecution(
        simulation_type="basic",
        status="completed",
        reason=None,
        initial_state=initial_state,
        final_state=state,
        telemetry=recorder.records,
        metadata_json={"throttle": throttle, "steps": steps, "dt": dt},
    )


def run_fixed_throttle_landing(
    *,
    initial_altitude_m: float,
    initial_vertical_velocity_m_s: float,
    initial_fuel_mass_kg: float,
    throttle: float,
    max_steps: int,
    dt: float,
) -> SimulationExecution:
    return _run_landing(
        simulation_type="landing",
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        max_steps=max_steps,
        dt=dt,
        controller=None,
        fixed_throttle=throttle,
    )


def run_heuristic_landing(
    *,
    initial_altitude_m: float,
    initial_vertical_velocity_m_s: float,
    initial_fuel_mass_kg: float,
    max_steps: int,
    dt: float,
) -> SimulationExecution:
    return _run_landing(
        simulation_type="heuristic_landing",
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        max_steps=max_steps,
        dt=dt,
        controller=HeuristicLandingController(),
        fixed_throttle=None,
    )


def _run_landing(
    *,
    simulation_type: str,
    initial_altitude_m: float,
    initial_vertical_velocity_m_s: float,
    initial_fuel_mass_kg: float,
    max_steps: int,
    dt: float,
    controller: ThrottleController | None,
    fixed_throttle: float | None,
) -> SimulationExecution:
    scenario = _build_scenario(
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        max_steps=max_steps,
        dt=dt,
    )
    initial_state = scenario.create_initial_state()
    state = initial_state.copy()
    simulator = scenario.create_simulator()
    recorder = TelemetryRecorder()
    throttle = fixed_throttle or 0.0

    for step in range(max_steps):
        throttle = controller.compute_throttle(state) if controller else throttle
        recorder.record(step, state, throttle)
        state = simulator.step(state, throttle)
        if state.altitude <= 0.0:
            break
    recorder.record(len(recorder.records), state, throttle)

    evaluation = evaluate_landing(state)
    metadata: dict[str, Any] = {"max_steps": max_steps, "dt": dt}
    if fixed_throttle is not None:
        metadata["throttle"] = fixed_throttle
    if controller is not None:
        metadata["controller"] = type(controller).__name__

    return SimulationExecution(
        simulation_type=simulation_type,
        status=evaluation.status.value,
        reason=evaluation.reason,
        initial_state=initial_state,
        final_state=state,
        telemetry=recorder.records,
        metadata_json=metadata,
    )


def _build_scenario(
    *,
    initial_altitude_m: float,
    initial_vertical_velocity_m_s: float,
    initial_fuel_mass_kg: float,
    max_steps: int,
    dt: float,
) -> SimulationScenario:
    defaults = SimulationScenario.from_yaml()
    scenario = SimulationScenario(
        dt=dt,
        max_steps=max_steps,
        dry_mass=defaults.dry_mass,
        fuel_mass=initial_fuel_mass_kg,
        max_thrust=defaults.max_thrust,
        fuel_burn_rate=defaults.fuel_burn_rate,
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
    )
    scenario.validate()
    return scenario
