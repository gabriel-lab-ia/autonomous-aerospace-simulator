import importlib
from pathlib import Path

import pytest

from aerospace_sim.simulation.scenario import SimulationScenario


def test_optional_neural_controller_module_imports_without_importing_torch() -> None:
    module = importlib.import_module("aerospace_sim.control.neural_controller")

    assert hasattr(module, "NeuralController")


def test_neural_controller_returns_bounded_throttle_for_valid_state() -> None:
    pytest.importorskip("torch")
    from aerospace_sim.control.neural_controller import NeuralController

    controller = NeuralController(allow_untrained=True)
    state = SimulationScenario.from_yaml().create_initial_state()

    assert 0.0 <= controller.compute_throttle(state) <= 1.0


def test_parameter_report_matches_documented_value() -> None:
    pytest.importorskip("torch")
    from aerospace_sim.learning.neural_controller import (
        NeuralRocketControllerNet,
        model_parameter_report,
    )

    report = model_parameter_report(NeuralRocketControllerNet())

    assert report["trainable_parameters"] == 586_630
    assert "| Total trainable parameters | 586,630 |" in Path("README.md").read_text()
