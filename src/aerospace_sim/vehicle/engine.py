from __future__ import annotations

from dataclasses import dataclass

from aerospace_sim.core.vector3 import Vector3


@dataclass
class RocketEngine:
    """Simplified rocket engine model with throttle control."""

    max_thrust: float
    fuel_burn_rate: float

    def compute_thrust(self, throttle: float) -> Vector3:
        """Compute thrust force vector pointing upward."""
        throttle = self.clamp_throttle(throttle)
        thrust = self.max_thrust * throttle
        return Vector3(0.0, 0.0, thrust)

    def compute_fuel_consumption(
        self,
        throttle: float,
        dt: float,
        available_fuel: float | None = None,
    ) -> float:
        """Compute fuel consumed during a time step."""
        throttle = self.clamp_throttle(throttle)
        planned_consumption = self.fuel_burn_rate * throttle * dt

        if available_fuel is None:
            return planned_consumption

        return min(planned_consumption, max(0.0, available_fuel))

    @staticmethod
    def clamp_throttle(throttle: float) -> float:
        """Clamp a throttle command to the engine's valid operating range."""
        return max(0.0, min(1.0, throttle))
