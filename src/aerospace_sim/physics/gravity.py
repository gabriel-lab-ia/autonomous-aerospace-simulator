from __future__ import annotations

from aerospace_sim.core.vector3 import Vector3


EARTH_GRAVITY = Vector3(0.0, 0.0, -9.80665)


def gravity_acceleration() -> Vector3:
    """Return Earth gravitational acceleration vector in m/s²."""
    return EARTH_GRAVITY


def gravity_force(mass: float) -> Vector3:
    """Compute gravitational force for a body with the given mass."""
    return EARTH_GRAVITY * mass
