from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.environment.landing import LandingStatus, evaluate_landing


ZERO_VECTOR = Vector3(0.0, 0.0, 0.0)


def create_state(*, altitude: float, velocity_z: float) -> RocketState:
    return RocketState(
        position=Vector3(0.0, 0.0, altitude),
        velocity=Vector3(0.0, 0.0, velocity_z),
        orientation=ZERO_VECTOR,
        angular_velocity=ZERO_VECTOR,
        fuel_mass=10.0,
    )


def test_positive_altitude_is_still_flying() -> None:
    evaluation = evaluate_landing(create_state(altitude=1.0, velocity_z=0.0))

    assert evaluation.status is LandingStatus.STILL_FLYING


def test_slow_touchdown_is_landed() -> None:
    evaluation = evaluate_landing(create_state(altitude=0.0, velocity_z=-1.0))

    assert evaluation.status is LandingStatus.LANDED


def test_fast_touchdown_is_crashed() -> None:
    evaluation = evaluate_landing(create_state(altitude=0.0, velocity_z=-10.0))

    assert evaluation.status is LandingStatus.CRASHED
