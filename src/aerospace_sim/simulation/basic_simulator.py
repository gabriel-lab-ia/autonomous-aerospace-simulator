from __future__ import annotations

from dataclasses import dataclass

from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.physics.gravity import gravity_force
from aerospace_sim.vehicle.engine import RocketEngine


@dataclass
class BasicRocketSimulator:
    """Minimal 3D rocket simulator using Euler integration."""

    engine: RocketEngine
    dry_mass: float
    dt: float

    def total_mass(self, state: RocketState) -> float:
        return self.dry_mass + max(0.0, state.fuel_mass)

    def step(self, state: RocketState, throttle: float) -> RocketState:
        mass = self.total_mass(state)

        planned_fuel_use = self.engine.compute_fuel_consumption(throttle, self.dt)
        fuel_used = self.engine.compute_fuel_consumption(
            throttle,
            self.dt,
            available_fuel=state.fuel_mass,
        )

        burn_fraction = fuel_used / planned_fuel_use if planned_fuel_use > 0.0 else 0.0
        effective_throttle = self.engine.clamp_throttle(throttle) * burn_fraction

        thrust = self.engine.compute_thrust(effective_throttle)
        weight = gravity_force(mass)

        net_force = thrust + weight
        acceleration = net_force * (1.0 / mass)

        new_velocity = state.velocity + acceleration * self.dt
        new_position = state.position + new_velocity * self.dt

        new_fuel_mass = max(0.0, state.fuel_mass - fuel_used)

        if new_position.z < 0.0:
            new_position = Vector3(new_position.x, new_position.y, 0.0)

        return RocketState(
            position=new_position,
            velocity=new_velocity,
            orientation=state.orientation,
            angular_velocity=state.angular_velocity,
            fuel_mass=new_fuel_mass,
            time=state.time + self.dt,
        )
