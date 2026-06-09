from __future__ import annotations

from dataclasses import dataclass

from aerospace_sim.core.state import RocketState


@dataclass
class HeuristicLandingController:
    """Simple state-based landing controller.

    This controller adjusts throttle dynamically using altitude and vertical
    velocity. It is a first autonomous control baseline before PID/RL.
    """

    high_altitude_target_vz: float = -18.0
    mid_altitude_target_vz: float = -8.0
    low_altitude_target_vz: float = -1.5

    kp: float = 0.045
    dry_mass: float = 1200.0
    max_thrust: float = 35000.0
    gravity_m_s2: float = 9.80665

    def compute_throttle(self, state: RocketState) -> float:
        altitude = state.altitude
        vertical_velocity = state.velocity.z

        target_vz = self._target_vertical_velocity(altitude)
        hover_throttle = self._estimated_hover_throttle(state)

        error = target_vz - vertical_velocity

        throttle = hover_throttle - self.kp * error

        if altitude < 15.0 and vertical_velocity < -4.0:
            throttle = 1.0

        if altitude < 5.0 and vertical_velocity < -2.5:
            throttle = 1.0

        if vertical_velocity > 1.5:
            throttle *= 0.55

        return self._clamp(throttle)

    def _target_vertical_velocity(self, altitude: float) -> float:
        if altitude > 60.0:
            return self.high_altitude_target_vz

        if altitude > 20.0:
            return self.mid_altitude_target_vz

        return self.low_altitude_target_vz

    def _estimated_hover_throttle(self, state: RocketState) -> float:
        total_mass = self.dry_mass + state.fuel_mass
        hover_throttle = (total_mass * self.gravity_m_s2) / self.max_thrust

        return self._clamp(hover_throttle)

    @staticmethod
    def _clamp(value: float) -> float:
        return max(0.0, min(1.0, value))
