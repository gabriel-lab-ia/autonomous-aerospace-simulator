from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from sqlalchemy import DateTime, Float, ForeignKey, Index, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from aerospace_sim.database.connection import Base


class SimulationModel(Base):
    __tablename__ = "simulations"
    __table_args__ = (
        Index("ix_simulations_type_status", "simulation_type", "status"),
        Index("ix_simulations_created_at", "created_at"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_type: Mapped[str] = mapped_column(String(64), index=True)
    status: Mapped[str] = mapped_column(String(64), index=True)
    reason: Mapped[str | None] = mapped_column(String(512), nullable=True)
    initial_altitude_m: Mapped[float] = mapped_column(Float)
    initial_vertical_velocity_m_s: Mapped[float] = mapped_column(Float)
    initial_fuel_mass_kg: Mapped[float] = mapped_column(Float)
    final_altitude_m: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_vertical_velocity_m_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_speed_m_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_fuel_mass_kg: Mapped[float | None] = mapped_column(Float, nullable=True)
    final_time_s: Mapped[float | None] = mapped_column(Float, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)

    telemetry_points: Mapped[list["TelemetryPointModel"]] = relationship(
        back_populates="simulation",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class TelemetryPointModel(Base):
    __tablename__ = "telemetry_points"
    __table_args__ = (Index("ix_telemetry_simulation_time", "simulation_id", "time_s"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    simulation_id: Mapped[int] = mapped_column(
        ForeignKey("simulations.id", ondelete="CASCADE"),
        index=True,
    )
    time_s: Mapped[float] = mapped_column(Float)
    altitude_m: Mapped[float] = mapped_column(Float)
    velocity_z_m_s: Mapped[float] = mapped_column(Float)
    speed_m_s: Mapped[float] = mapped_column(Float)
    fuel_mass_kg: Mapped[float] = mapped_column(Float)
    throttle: Mapped[float | None] = mapped_column(Float, nullable=True)

    simulation: Mapped[SimulationModel] = relationship(back_populates="telemetry_points")
