from math import isclose

from aerospace_sim.physics.gravity import EARTH_GRAVITY, gravity_force


def test_gravity_force_points_toward_negative_z() -> None:
    force = gravity_force(10.0)

    assert isclose(force.x, 0.0)
    assert isclose(force.y, 0.0)
    assert force.z < 0.0


def test_gravity_force_is_proportional_to_mass() -> None:
    mass = 10.0

    assert isclose(gravity_force(mass).z, EARTH_GRAVITY.z * mass)
