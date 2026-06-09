from __future__ import annotations

from dataclasses import asdict, dataclass

import pandas as pd

from aerospace_sim.core.state import RocketState


@dataclass(frozen=True)
class TelemetryRecord:
    step: int
    time_s: float
    altitude_m: float
    position_x_m: float
    position_y_m: float
    velocity_z_m_s: float
    speed_m_s: float
    fuel_mass_kg: float
    throttle: float

    @classmethod
    def from_state(cls, step: int, state: RocketState, throttle: float) -> "TelemetryRecord":
        return cls(
            step=step,
            time_s=state.time,
            altitude_m=state.altitude,
            position_x_m=state.position.x,
            position_y_m=state.position.y,
            velocity_z_m_s=state.velocity.z,
            speed_m_s=state.speed,
            fuel_mass_kg=state.fuel_mass,
            throttle=throttle,
        )

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


class TelemetryRecorder:
    """Collect a consistent telemetry schema for simulation experiments."""

    def __init__(self) -> None:
        self._records: list[TelemetryRecord] = []

    def record(self, step: int, state: RocketState, throttle: float) -> None:
        self._records.append(TelemetryRecord.from_state(step, state, throttle))

    def to_dataframe(self) -> pd.DataFrame:
        return pd.DataFrame(record.to_dict() for record in self._records)
