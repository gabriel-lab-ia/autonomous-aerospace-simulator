from math import isclose

from aerospace_sim.core.vector3 import Vector3


def test_vector_addition() -> None:
    assert Vector3(1.0, 2.0, 3.0) + Vector3(4.0, 5.0, 6.0) == Vector3(5.0, 7.0, 9.0)


def test_vector_subtraction() -> None:
    assert Vector3(4.0, 5.0, 6.0) - Vector3(1.0, 2.0, 3.0) == Vector3(3.0, 3.0, 3.0)


def test_vector_scalar_multiplication() -> None:
    assert Vector3(1.0, -2.0, 3.0) * 2.0 == Vector3(2.0, -4.0, 6.0)


def test_vector_norm() -> None:
    assert isclose(Vector3(3.0, 4.0, 0.0).norm(), 5.0)


def test_normalizing_zero_vector_returns_zero_vector() -> None:
    assert Vector3(0.0, 0.0, 0.0).normalized() == Vector3(0.0, 0.0, 0.0)
