from __future__ import annotations

from collections.abc import Iterable
from typing import Any

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from aerospace_sim.database.models import SimulationModel, TelemetryPointModel
from aerospace_sim.telemetry.recorder import TelemetryRecord


def create_simulation(
    db: Session,
    *,
    simulation_type: str,
    status: str,
    reason: str | None,
    initial_altitude_m: float,
    initial_vertical_velocity_m_s: float,
    initial_fuel_mass_kg: float,
    final_altitude_m: float,
    final_vertical_velocity_m_s: float,
    final_speed_m_s: float,
    final_fuel_mass_kg: float,
    final_time_s: float,
    metadata_json: dict[str, Any],
    telemetry: Iterable[TelemetryRecord],
) -> SimulationModel:
    simulation = SimulationModel(
        simulation_type=simulation_type,
        status=status,
        reason=reason,
        initial_altitude_m=initial_altitude_m,
        initial_vertical_velocity_m_s=initial_vertical_velocity_m_s,
        initial_fuel_mass_kg=initial_fuel_mass_kg,
        final_altitude_m=final_altitude_m,
        final_vertical_velocity_m_s=final_vertical_velocity_m_s,
        final_speed_m_s=final_speed_m_s,
        final_fuel_mass_kg=final_fuel_mass_kg,
        final_time_s=final_time_s,
        metadata_json=metadata_json,
    )
    db.add(simulation)
    db.flush()
    db.add_all(
        TelemetryPointModel(
            simulation_id=simulation.id,
            time_s=point.time_s,
            altitude_m=point.altitude_m,
            velocity_z_m_s=point.velocity_z_m_s,
            speed_m_s=point.speed_m_s,
            fuel_mass_kg=point.fuel_mass_kg,
            throttle=point.throttle,
        )
        for point in telemetry
    )
    db.commit()
    db.refresh(simulation)
    return simulation


def get_simulation(db: Session, simulation_id: int) -> SimulationModel | None:
    return db.get(SimulationModel, simulation_id)


def list_simulations(
    db: Session,
    *,
    limit: int,
    simulation_type: str | None = None,
    status: str | None = None,
) -> list[SimulationModel]:
    statement: Select[tuple[SimulationModel]] = select(SimulationModel)
    if simulation_type is not None:
        statement = statement.where(SimulationModel.simulation_type == simulation_type)
    if status is not None:
        statement = statement.where(SimulationModel.status == status)
    statement = statement.order_by(SimulationModel.created_at.desc()).limit(limit)
    return list(db.scalars(statement))


def list_telemetry(
    db: Session,
    *,
    simulation_id: int,
    limit: int,
    offset: int,
) -> list[TelemetryPointModel]:
    statement = (
        select(TelemetryPointModel)
        .where(TelemetryPointModel.simulation_id == simulation_id)
        .order_by(TelemetryPointModel.time_s, TelemetryPointModel.id)
        .limit(limit)
        .offset(offset)
    )
    return list(db.scalars(statement))
