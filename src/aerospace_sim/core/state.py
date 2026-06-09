from __future__ import annotations

from dataclasses import dataclass
import numpy as np

from aerospace_sim.core.vector3 import Vector3


@dataclass
class RocketState:
    """Full dynamic state of the rocket at one simulation step."""

    position: Vector3
    velocity: Vector3
    orientation: Vector3
    angular_velocity: Vector3
    fuel_mass: float
    time: float = 0.0

    def to_vector(self) -> np.ndarray:
        """Convert state into a numerical vector for ML/control systems."""
        return np.array(
            [
                self.position.x,
                self.position.y,
                self.position.z,
                self.velocity.x,
                self.velocity.y,
                self.velocity.z,
                self.orientation.x,
                self.orientation.y,
                self.orientation.z,
                self.angular_velocity.x,
                self.angular_velocity.y,
                self.angular_velocity.z,
                self.fuel_mass,
            ],
            dtype=np.float64,
        )

    @property
    def altitude(self) -> float:
        return self.position.z

    @property
    def speed(self) -> float:
        return self.velocity.norm()

    def copy(self) -> "RocketState":
        return RocketState(
            position=self.position,
            velocity=self.velocity,
            orientation=self.orientation,
            angular_velocity=self.angular_velocity,
            fuel_mass=float(self.fuel_mass),
            time=float(self.time),
        )
