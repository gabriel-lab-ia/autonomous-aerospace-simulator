from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from aerospace_sim.core.config_loader import load_yaml_config
from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator
from aerospace_sim.vehicle.engine import RocketEngine


DEFAULT_CONFIG_PATH = Path("configs/default.yaml")
ZERO_VECTOR = Vector3(0.0, 0.0, 0.0)


@dataclass(frozen=True)
class SimulationScenario:
    """Validated parameters required by the current vertical simulation."""

    dt: float
    max_steps: int
    dry_mass: float
    fuel_mass: float
    max_thrust: float
    fuel_burn_rate: float
    initial_altitude_m: float
    initial_vertical_velocity_m_s: float

    @classmethod
    def from_yaml(cls, path: str | Path = DEFAULT_CONFIG_PATH) -> "SimulationScenario":
        return cls.from_dict(load_yaml_config(path))

    @classmethod
    def from_dict(cls, config: dict[str, Any]) -> "SimulationScenario":
        simulation = _required_mapping(config, "simulation")
        rocket = _required_mapping(config, "rocket")
        initial_state = _required_mapping(simulation, "initial_state")

        scenario = cls(
            dt=float(simulation["dt"]),
            max_steps=int(simulation["max_steps"]),
            dry_mass=float(rocket["dry_mass"]),
            fuel_mass=float(rocket["fuel_mass"]),
            max_thrust=float(rocket["max_thrust"]),
            fuel_burn_rate=float(rocket["fuel_burn_rate"]),
            initial_altitude_m=float(initial_state["altitude_m"]),
            initial_vertical_velocity_m_s=float(initial_state["vertical_velocity_m_s"]),
        )
        scenario.validate()
        return scenario

    def validate(self) -> None:
        if self.dt <= 0.0:
            raise ValueError("Simulation dt must be positive.")
        if self.max_steps <= 0:
            raise ValueError("Simulation max_steps must be positive.")
        if self.dry_mass <= 0.0:
            raise ValueError("Rocket dry_mass must be positive.")
        if self.fuel_mass < 0.0:
            raise ValueError("Rocket fuel_mass cannot be negative.")
        if self.max_thrust < 0.0:
            raise ValueError("Rocket max_thrust cannot be negative.")
        if self.fuel_burn_rate < 0.0:
            raise ValueError("Rocket fuel_burn_rate cannot be negative.")
        if self.initial_altitude_m < 0.0:
            raise ValueError("Initial altitude cannot be negative.")

    def create_initial_state(self) -> RocketState:
        return RocketState(
            position=Vector3(0.0, 0.0, self.initial_altitude_m),
            velocity=Vector3(0.0, 0.0, self.initial_vertical_velocity_m_s),
            orientation=ZERO_VECTOR,
            angular_velocity=ZERO_VECTOR,
            fuel_mass=self.fuel_mass,
        )

    def create_simulator(self) -> BasicRocketSimulator:
        return BasicRocketSimulator(
            engine=RocketEngine(
                max_thrust=self.max_thrust,
                fuel_burn_rate=self.fuel_burn_rate,
            ),
            dry_mass=self.dry_mass,
            dt=self.dt,
        )


def _required_mapping(config: dict[str, Any], key: str) -> dict[str, Any]:
    value = config.get(key)
    if not isinstance(value, dict):
        raise ValueError(f"Configuration section '{key}' must be a mapping.")
    return value
