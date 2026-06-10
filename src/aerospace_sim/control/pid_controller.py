from __future__ import annotations

from dataclasses import dataclass, field
from math import sqrt
from pathlib import Path
from typing import Any

from aerospace_sim.core.config_loader import load_yaml_config
from aerospace_sim.core.state import RocketState


@dataclass
class PIDLandingController:
    """Classical PID baseline for the simplified vertical landing task.

    The controlled variable is vertical velocity. A braking-profile target
    approaches ``target_vertical_velocity_m_s`` near the ground and permits a
    faster descent at altitude. Hover throttle is used as feed-forward so the
    PID terms primarily correct velocity error.
    """

    target_altitude_m: float = 0.0
    target_vertical_velocity_m_s: float = -2.0
    kp: float = 0.045
    ki: float = 0.002
    kd: float = 0.012
    dt: float = 0.02
    throttle_min: float = 0.0
    throttle_max: float = 1.0
    integral_limit: float = 20.0
    dry_mass_kg: float = 1200.0
    max_thrust_n: float = 35000.0
    gravity_m_s2: float = 9.80665
    max_descent_rate_m_s: float = 18.0
    braking_acceleration_m_s2: float = 1.2
    integral_error: float = field(default=0.0, init=False)
    previous_error: float | None = field(default=None, init=False)

    def __post_init__(self) -> None:
        if self.dt <= 0.0:
            raise ValueError("PID dt must be positive.")
        if self.throttle_min > self.throttle_max:
            raise ValueError("throttle_min cannot exceed throttle_max.")
        if self.integral_limit < 0.0:
            raise ValueError("integral_limit cannot be negative.")
        if self.max_thrust_n <= 0.0:
            raise ValueError("max_thrust_n must be positive.")

    @classmethod
    def from_yaml(
        cls,
        path: str | Path = "configs/pid.yaml",
        **overrides: Any,
    ) -> "PIDLandingController":
        """Build a PID controller from the versioned YAML configuration."""
        config = load_yaml_config(path).get("pid")
        if not isinstance(config, dict):
            raise ValueError("PID configuration must contain a 'pid' mapping.")
        parameters = {key: value for key, value in config.items() if key != "note"}
        parameters.update(overrides)
        return cls(**parameters)

    def compute_throttle(self, state: RocketState) -> float:
        """Return a bounded throttle command and update PID state."""
        target_velocity = self._target_velocity(state.altitude)
        error = target_velocity - state.velocity.z
        derivative = (
            0.0
            if self.previous_error is None
            else (error - self.previous_error) / self.dt
        )
        candidate_integral = self._clamp_integral(
            self.integral_error + error * self.dt
        )

        hover_throttle = (
            (self.dry_mass_kg + max(0.0, state.fuel_mass)) * self.gravity_m_s2
        ) / self.max_thrust_n
        unsaturated = (
            hover_throttle
            + self.kp * error
            + self.ki * candidate_integral
            + self.kd * derivative
        )
        throttle = self._clamp_throttle(unsaturated)

        # Conditional integration prevents saturation from increasing windup.
        drives_back_from_saturation = (
            unsaturated > self.throttle_max and error < 0.0
        ) or (unsaturated < self.throttle_min and error > 0.0)
        if throttle == unsaturated or drives_back_from_saturation:
            self.integral_error = candidate_integral

        self.previous_error = error
        return throttle

    def reset(self) -> None:
        """Reset accumulated state before reusing the controller."""
        self.integral_error = 0.0
        self.previous_error = None

    def _target_velocity(self, altitude_m: float) -> float:
        altitude_error = max(0.0, altitude_m - self.target_altitude_m)
        braking_rate = sqrt(2.0 * self.braking_acceleration_m_s2 * altitude_error)
        descent_rate = min(
            self.max_descent_rate_m_s,
            max(abs(self.target_vertical_velocity_m_s), braking_rate),
        )
        return -descent_rate

    def _clamp_integral(self, value: float) -> float:
        return max(-self.integral_limit, min(self.integral_limit, value))

    def _clamp_throttle(self, value: float) -> float:
        return max(self.throttle_min, min(self.throttle_max, value))
