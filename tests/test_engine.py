from math import isclose

from aerospace_sim.vehicle.engine import RocketEngine


def test_throttle_is_clamped_between_zero_and_one() -> None:
    engine = RocketEngine(max_thrust=100.0, fuel_burn_rate=2.0)

    assert isclose(engine.compute_thrust(-1.0).z, 0.0)
    assert isclose(engine.compute_thrust(2.0).z, 100.0)


def test_fuel_consumption_is_proportional_to_throttle() -> None:
    engine = RocketEngine(max_thrust=100.0, fuel_burn_rate=2.0)

    assert isclose(engine.compute_fuel_consumption(throttle=0.5, dt=4.0), 4.0)


def test_zero_throttle_consumes_no_fuel() -> None:
    engine = RocketEngine(max_thrust=100.0, fuel_burn_rate=2.0)

    assert isclose(engine.compute_fuel_consumption(throttle=0.0, dt=4.0), 0.0)


def test_fuel_consumption_is_limited_to_available_fuel() -> None:
    engine = RocketEngine(max_thrust=100.0, fuel_burn_rate=2.0)

    fuel_used = engine.compute_fuel_consumption(
        throttle=1.0,
        dt=1.0,
        available_fuel=0.5,
    )

    assert isclose(fuel_used, 0.5)
