from pathlib import Path

import pytest

from aerospace_sim.simulation.scenario import SimulationScenario


def test_default_scenario_builds_expected_state_and_simulator() -> None:
    scenario = SimulationScenario.from_yaml(Path("configs/default.yaml"))
    state = scenario.create_initial_state()
    simulator = scenario.create_simulator()

    assert state.altitude == 100.0
    assert state.velocity.z == -10.0
    assert state.fuel_mass == 800.0
    assert simulator.dt == 0.02
    assert simulator.dry_mass == 1200.0
    assert simulator.engine.max_thrust == 35000.0


def test_scenario_rejects_non_positive_dt() -> None:
    config = {
        "simulation": {
            "dt": 0.0,
            "max_steps": 10,
            "initial_state": {"altitude_m": 100.0, "vertical_velocity_m_s": -10.0},
        },
        "rocket": {
            "dry_mass": 1200.0,
            "fuel_mass": 800.0,
            "max_thrust": 35000.0,
            "fuel_burn_rate": 2.5,
        },
    }

    with pytest.raises(ValueError, match="dt must be positive"):
        SimulationScenario.from_dict(config)


def test_scenario_overrides_are_validated_and_serializable() -> None:
    defaults = SimulationScenario.from_yaml()

    scenario = defaults.with_overrides(
        dt=0.1,
        max_steps=25,
        initial_altitude_m=250.0,
    )

    assert scenario.dt == 0.1
    assert scenario.max_steps == 25
    assert scenario.initial_altitude_m == 250.0
    assert scenario.dry_mass == defaults.dry_mass
    assert scenario.to_dict()["max_thrust"] == defaults.max_thrust

    with pytest.raises(ValueError, match="max_steps must be positive"):
        defaults.with_overrides(max_steps=0)
