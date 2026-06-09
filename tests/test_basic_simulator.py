from math import isclose

from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.physics.gravity import EARTH_GRAVITY
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator
from aerospace_sim.vehicle.engine import RocketEngine


ZERO_VECTOR = Vector3(0.0, 0.0, 0.0)


def create_state(*, altitude: float = 100.0, fuel_mass: float = 10.0) -> RocketState:
    return RocketState(
        position=Vector3(0.0, 0.0, altitude),
        velocity=ZERO_VECTOR,
        orientation=ZERO_VECTOR,
        angular_velocity=ZERO_VECTOR,
        fuel_mass=fuel_mass,
    )


def create_simulator(*, dt: float = 0.1) -> BasicRocketSimulator:
    return BasicRocketSimulator(
        engine=RocketEngine(max_thrust=20_000.0, fuel_burn_rate=2.0),
        dry_mass=1_000.0,
        dt=dt,
    )


def test_zero_throttle_reduces_altitude() -> None:
    result = create_simulator().step(create_state(), throttle=0.0)

    assert result.altitude < 100.0


def test_fuel_mass_never_becomes_negative() -> None:
    result = create_simulator(dt=1.0).step(
        create_state(fuel_mass=0.5),
        throttle=1.0,
    )

    assert isclose(result.fuel_mass, 0.0)


def test_zero_fuel_produces_no_thrust() -> None:
    simulator = create_simulator()
    result = simulator.step(create_state(fuel_mass=0.0), throttle=1.0)

    assert isclose(result.velocity.z, EARTH_GRAVITY.z * simulator.dt)


def test_altitude_is_clamped_at_ground_level() -> None:
    result = create_simulator(dt=1.0).step(
        create_state(altitude=0.1),
        throttle=0.0,
    )

    assert isclose(result.altitude, 0.0)


def test_negative_initial_fuel_is_clamped_to_zero() -> None:
    result = create_simulator().step(create_state(fuel_mass=-1.0), throttle=1.0)

    assert isclose(result.fuel_mass, 0.0)
