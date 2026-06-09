from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from aerospace_sim.control.heuristic_landing_controller import HeuristicLandingController
from aerospace_sim.core.state import RocketState
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.runner import ThrottleController, run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TelemetryRecord


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
    run = run_scenario(
        scenario,
        fixed_throttle=throttle,
        max_steps=steps,
        record_final_state=True,
    )

    return SimulationExecution(
        simulation_type="basic",
        status="completed",
        reason=None,
        initial_state=run.initial_state,
        final_state=run.final_state,
        telemetry=run.telemetry.records,
        metadata_json={
            "throttle": throttle,
            "steps": steps,
            "dt": dt,
            "scenario": scenario.to_dict(),
        },
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
    run = run_scenario(
        scenario,
        controller=controller,
        fixed_throttle=fixed_throttle,
        max_steps=max_steps,
        stop_on_ground=True,
        record_final_state=True,
    )
    evaluation = evaluate_landing(run.final_state)
    metadata: dict[str, Any] = {
        "max_steps": max_steps,
        "dt": dt,
        "terminal_reason": run.terminal_reason,
        "scenario": scenario.to_dict(),
    }
    if fixed_throttle is not None:
        metadata["throttle"] = fixed_throttle
    if controller is not None:
        metadata["controller"] = type(controller).__name__

    return SimulationExecution(
        simulation_type=simulation_type,
        status=evaluation.status.value,
        reason=evaluation.reason,
        initial_state=run.initial_state,
        final_state=run.final_state,
        telemetry=run.telemetry.records,
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
    return SimulationScenario.from_yaml().with_overrides(
        dt=dt,
        max_steps=max_steps,
        fuel_mass=initial_fuel_mass_kg,
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
    )
