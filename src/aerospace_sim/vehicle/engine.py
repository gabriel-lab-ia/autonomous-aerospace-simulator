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
        throttle = max(0.0, min(1.0, throttle))
        thrust = self.max_thrust * throttle
        return Vector3(0.0, 0.0, thrust)

    def compute_fuel_consumption(self, throttle: float, dt: float) -> float:
        """Compute fuel consumed during a time step."""
        throttle = max(0.0, min(1.0, throttle))
        return self.fuel_burn_rate * throttle * dt
