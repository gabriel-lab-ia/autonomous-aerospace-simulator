"""Optional machine-learning modules for aerospace control experiments.

The package initializer intentionally avoids importing PyTorch. Import concrete
ML implementations from ``aerospace_sim.learning.neural_controller`` only when
the optional ``ml`` dependency group is installed.
"""

from importlib import import_module
from typing import Any


__all__ = [
    "INPUT_DIM",
    "PHASE_CLASSES",
    "PHASE_LABELS",
    "STATE_FEATURES",
    "NeuralControllerConfig",
    "NeuralRocketControllerNet",
    "RocketControlDataset",
    "TelemetryControlDataset",
    "descent_phase_labels",
    "expert_throttle_policy",
    "generate_synthetic_rocket_states",
    "model_parameter_report",
    "normalize_state_features",
    "predict_throttle_from_state",
    "stability_score",
]


def __getattr__(name: str) -> Any:
    """Load PyTorch-backed exports only when a caller explicitly requests one."""
    if name not in __all__:
        raise AttributeError(f"module {__name__!r} has no attribute {name!r}")
    neural_controller = import_module("aerospace_sim.learning.neural_controller")
    return getattr(neural_controller, name)


def __dir__() -> list[str]:
    return sorted((*globals(), *__all__))
