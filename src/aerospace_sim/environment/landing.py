from __future__ import annotations

from dataclasses import dataclass
from enum import Enum

from aerospace_sim.core.state import RocketState


class LandingStatus(str, Enum):
    LANDED = "landed"
    CRASHED = "crashed"
    STILL_FLYING = "still_flying"


@dataclass(frozen=True)
class LandingEvaluation:
    status: LandingStatus
    reason: str
    final_altitude_m: float
    final_velocity_z_m_s: float
    final_speed_m_s: float
    final_time_s: float
    final_fuel_mass_kg: float


def evaluate_landing(
    state: RocketState,
    safe_vertical_velocity: float = 2.0,
    safe_total_speed: float = 3.0,
    ground_tolerance: float = 1e-6,
) -> LandingEvaluation:
    """Classify the final rocket state as landed, crashed, or still flying."""

    if state.altitude > ground_tolerance:
        return LandingEvaluation(
            status=LandingStatus.STILL_FLYING,
            reason="Rocket has not reached the ground yet.",
            final_altitude_m=state.altitude,
            final_velocity_z_m_s=state.velocity.z,
            final_speed_m_s=state.speed,
            final_time_s=state.time,
            final_fuel_mass_kg=state.fuel_mass,
        )

    if abs(state.velocity.z) <= safe_vertical_velocity and state.speed <= safe_total_speed:
        return LandingEvaluation(
            status=LandingStatus.LANDED,
            reason="Touchdown velocity is within safe landing limits.",
            final_altitude_m=state.altitude,
            final_velocity_z_m_s=state.velocity.z,
            final_speed_m_s=state.speed,
            final_time_s=state.time,
            final_fuel_mass_kg=state.fuel_mass,
        )

    return LandingEvaluation(
        status=LandingStatus.CRASHED,
        reason="Touchdown velocity exceeded safe landing limits.",
        final_altitude_m=state.altitude,
        final_velocity_z_m_s=state.velocity.z,
        final_speed_m_s=state.speed,
        final_time_s=state.time,
        final_fuel_mass_kg=state.fuel_mass,
    )