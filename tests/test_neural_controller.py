from __future__ import annotations

import numpy as np
import pytest

pytest.importorskip("torch")

import torch

from aerospace_sim.learning.neural_controller import (
    INPUT_DIM,
    PHASE_CLASSES,
    NeuralRocketControllerNet,
    RocketControlDataset,
    expert_throttle_policy,
    generate_synthetic_rocket_states,
    model_parameter_report,
    normalize_state_features,
    predict_throttle_from_state,
)


def test_neural_controller_forward_shapes_and_bounds() -> None:
    model = NeuralRocketControllerNet()
    batch = torch.zeros((8, INPUT_DIM), dtype=torch.float32)

    throttle, stability, phase_logits, phase_probabilities = model(
        batch,
        return_probabilities=True,
    )

    assert throttle.shape == (8, 1)
    assert stability.shape == (8, 1)
    assert phase_logits.shape == (8, PHASE_CLASSES)
    assert phase_probabilities.shape == (8, PHASE_CLASSES)
    assert torch.all(throttle >= 0.0)
    assert torch.all(throttle <= 1.0)
    assert torch.all(stability >= 0.0)
    assert torch.all(stability <= 1.0)
    assert torch.allclose(
        phase_probabilities.sum(dim=1),
        torch.ones(8),
        atol=1e-6,
    )


def test_synthetic_dataset_contract() -> None:
    dataset = RocketControlDataset(n_samples=128, seed=7)
    x, throttle, stability, phase = dataset[0]

    assert len(dataset) == 128
    assert x.shape == (INPUT_DIM,)
    assert throttle.shape == (1,)
    assert stability.shape == (1,)
    assert int(phase) in range(PHASE_CLASSES)
    assert torch.isfinite(x).all()
    assert 0.0 <= float(throttle.item()) <= 1.0
    assert 0.0 <= float(stability.item()) <= 1.0


def test_teacher_policy_increases_throttle_for_fast_low_descent() -> None:
    high_safe = np.zeros((1, INPUT_DIM), dtype=np.float32)
    high_safe[0, 2] = 900.0
    high_safe[0, 5] = -5.0
    high_safe[0, 12] = 800.0

    low_fast = np.zeros((1, INPUT_DIM), dtype=np.float32)
    low_fast[0, 2] = 80.0
    low_fast[0, 5] = -60.0
    low_fast[0, 12] = 800.0

    high_safe_throttle = expert_throttle_policy(high_safe)[0, 0]
    low_fast_throttle = expert_throttle_policy(low_fast)[0, 0]

    assert low_fast_throttle > high_safe_throttle
    assert 0.0 <= high_safe_throttle <= 1.0
    assert 0.0 <= low_fast_throttle <= 1.0


def test_feature_normalization_and_inference_contract() -> None:
    states = generate_synthetic_rocket_states(n_samples=4, seed=11)
    features = normalize_state_features(states)

    assert features.shape == (4, INPUT_DIM)
    assert np.isfinite(features).all()

    model = NeuralRocketControllerNet()
    throttle = predict_throttle_from_state(model, states[0])

    assert 0.0 <= throttle <= 1.0


def test_model_parameter_report_is_consistent() -> None:
    model = NeuralRocketControllerNet()
    report = model_parameter_report(model)

    assert report["total_parameters"] > 0
    assert report["trainable_parameters"] == report["total_parameters"]
