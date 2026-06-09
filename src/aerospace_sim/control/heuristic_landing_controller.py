from __future__ import annotations

from dataclasses import dataclass

from aerospace_sim.core.state import RocketState


@dataclass
class HeuristicLandingController:
    """Simple state-based landing controller.

    This controller adjusts throttle dynamically using altitude and vertical
    velocity. It is not a PID controller yet. It is a first autonomous control
    baseline for the landing task.
    """

    target_descent_rate_high_altitude: float = -18.0
    target_descent_rate_mid_altitude: float = -10.0
    target_descent_rate_low_altitude: float = -3.0

    def compute_throttle(self, state: RocketState) -> float:
        altitude = state.altitude
        vertical_velocity = state.velocity.z

        target_descent_rate = self._target_descent_rate(altitude)

        error = target_descent_rate - vertical_velocity

        base_throttle = self._base_throttle(altitude)

        correction = -0.035 * error

        throttle = base_throttle + correction

        if altitude < 10.0 and vertical_velocity < -4.0:
            throttle = 1.0

        if vertical_velocity > 3.0:
            throttle = 0.15

        return self._clamp(throttle)

    def _target_descent_rate(self, altitude: float) -> float:
        if altitude > 60.0:
            return self.target_descent_rate_high_altitude

        if altitude > 20.0:
            return self.target_descent_rate_mid_altitude

        return self.target_descent_rate_low_altitude

    def _base_throttle(self, altitude: float) -> float:
        if altitude > 60.0:
            return 0.45

        if altitude > 20.0:
            return 0.55

        return 0.70

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))