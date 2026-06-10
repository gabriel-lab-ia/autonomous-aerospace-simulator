"""Optional machine-learning modules for aerospace control experiments."""

from aerospace_sim.learning.neural_controller import (
    INPUT_DIM,
    PHASE_CLASSES,
    PHASE_LABELS,
    STATE_FEATURES,
    NeuralControllerConfig,
    NeuralRocketControllerNet,
    RocketControlDataset,
    descent_phase_labels,
    expert_throttle_policy,
    generate_synthetic_rocket_states,
    model_parameter_report,
    normalize_state_features,
    predict_throttle_from_state,
    stability_score,
)

__all__ = [
    "INPUT_DIM",
    "PHASE_CLASSES",
    "PHASE_LABELS",
    "STATE_FEATURES",
    "NeuralControllerConfig",
    "NeuralRocketControllerNet",
    "RocketControlDataset",
    "descent_phase_labels",
    "expert_throttle_policy",
    "generate_synthetic_rocket_states",
    "model_parameter_report",
    "normalize_state_features",
    "predict_throttle_from_state",
    "stability_score",
]
