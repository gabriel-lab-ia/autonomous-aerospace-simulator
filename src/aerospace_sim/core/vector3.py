from __future__ import annotations

from dataclasses import dataclass
import numpy as np


@dataclass(frozen=True)
class Vector3:
    """Simple immutable 3D vector used across the simulator."""

    x: float
    y: float
    z: float

    def to_numpy(self) -> np.ndarray:
        return np.array([self.x, self.y, self.z], dtype=np.float64)

    @classmethod
    def from_iterable(cls, values) -> "Vector3":
        x, y, z = values
        return cls(float(x), float(y), float(z))

    def norm(self) -> float:
        return float(np.linalg.norm(self.to_numpy()))

    def normalized(self) -> "Vector3":
        length = self.norm()

        if length == 0.0:
            return Vector3(0.0, 0.0, 0.0)

        arr = self.to_numpy() / length
        return Vector3.from_iterable(arr)

    def __add__(self, other: "Vector3") -> "Vector3":
        return Vector3(
            self.x + other.x,
            self.y + other.y,
            self.z + other.z,
        )

    def __sub__(self, other: "Vector3") -> "Vector3":
        return Vector3(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )

    def __mul__(self, scalar: float) -> "Vector3":
        return Vector3(
            self.x * scalar,
            self.y * scalar,
            self.z * scalar,
        )
