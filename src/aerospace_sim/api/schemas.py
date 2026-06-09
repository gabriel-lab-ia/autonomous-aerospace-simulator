from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class BasicSimulationRequest(BaseModel):
    initial_altitude_m: float = Field(default=100.0, ge=0.0, le=10_000_000.0)
    initial_vertical_velocity_m_s: float = Field(default=-10.0, ge=-100_000.0, le=100_000.0)
    initial_fuel_mass_kg: float = Field(default=800.0, ge=0.0, le=10_000_000.0)
    throttle: float = Field(default=0.5, ge=0.0, le=1.0)
    steps: int = Field(default=100, ge=1, le=100_000)
    dt: float = Field(default=0.02, gt=0.0, le=1.0)


class LandingSimulationRequest(BaseModel):
    initial_altitude_m: float = Field(default=100.0, ge=0.0, le=10_000_000.0)
    initial_vertical_velocity_m_s: float = Field(default=-10.0, ge=-100_000.0, le=100_000.0)
    initial_fuel_mass_kg: float = Field(default=800.0, ge=0.0, le=10_000_000.0)
    throttle: float = Field(default=0.5, ge=0.0, le=1.0)
    max_steps: int = Field(default=3000, ge=1, le=100_000)
    dt: float = Field(default=0.02, gt=0.0, le=1.0)


class HeuristicLandingSimulationRequest(BaseModel):
    initial_altitude_m: float = Field(default=100.0, ge=0.0, le=10_000_000.0)
    initial_vertical_velocity_m_s: float = Field(default=-10.0, ge=-100_000.0, le=100_000.0)
    initial_fuel_mass_kg: float = Field(default=800.0, ge=0.0, le=10_000_000.0)
    max_steps: int = Field(default=3000, ge=1, le=100_000)
    dt: float = Field(default=0.02, gt=0.0, le=1.0)


class HealthResponse(BaseModel):
    status: str
    service: str
    database: str


class SimulationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    simulation_type: str
    status: str
    reason: str | None
    initial_altitude_m: float
    initial_vertical_velocity_m_s: float
    initial_fuel_mass_kg: float
    final_altitude_m: float | None
    final_vertical_velocity_m_s: float | None
    final_speed_m_s: float | None
    final_fuel_mass_kg: float | None
    final_time_s: float | None
    created_at: datetime
    metadata_json: dict[str, Any] | None


class TelemetryPointResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    simulation_id: int
    time_s: float
    altitude_m: float
    velocity_z_m_s: float
    speed_m_s: float
    fuel_mass_kg: float
    throttle: float | None
