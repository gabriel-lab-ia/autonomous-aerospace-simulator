# Deep Neural Rocket Controller

This document describes the optional deep-learning layer added to the aerospace
simulator for rocket landing control experiments.

The implementation adapts the dense multi-head perceptron pattern from the
previous quantum-learning prototype into an aerospace-control setting.  Instead
of learning from quantum statevectors and entanglement scores, the network now
learns from rocket state/sensor telemetry and predicts bounded control signals.

## Scope

The current simulator is intentionally simplified and centered on vertical
rocket dynamics.  This neural controller should therefore be read as a
portfolio-grade supervised pretraining layer for control research, not as a
flight-certified or high-fidelity aerospace controller.

It prepares the project for future simulator-in-the-loop reinforcement learning
by creating a tested PyTorch module with clear state contracts, output heads,
training metrics, and reproducible artifacts.

## Input State / Sensor Vector

The network consumes the existing 13-dimensional simulator state vector:

| Index | Feature | Unit |
|---:|---|---|
| 0 | position_x_m | m |
| 1 | position_y_m | m |
| 2 | altitude_z_m | m |
| 3 | velocity_x_mps | m/s |
| 4 | velocity_y_mps | m/s |
| 5 | vertical_velocity_z_mps | m/s |
| 6 | roll_rad | rad |
| 7 | pitch_rad | rad |
| 8 | yaw_rad | rad |
| 9 | angular_velocity_x_radps | rad/s |
| 10 | angular_velocity_y_radps | rad/s |
| 11 | angular_velocity_z_radps | rad/s |
| 12 | fuel_mass_kg | kg |

Raw values are normalized with fixed engineering-scale constants before being
passed to the neural network.  This keeps altitude, velocity, attitude, angular
rate, and fuel mass in numerically comparable ranges.

## Model Architecture

The neural controller is implemented in
`src/aerospace_sim/learning/neural_controller.py`.

### Encoder

```text
Input: 13 aerospace state/sensor features
Linear(13 -> 512)
LayerNorm(512)
GELU
Dropout(0.05)
Linear(512 -> 512)
LayerNorm(512)
GELU
Dropout(0.05)
Linear(512 -> 256)
LayerNorm(256)
GELU
Linear(256 -> 256)
LayerNorm(256)
GELU
```

### Output Heads

The shared latent representation feeds three aerospace-control heads:

| Head | Output | Activation / Meaning |
|---|---|---|
| throttle_head | 1 value | `Sigmoid`, bounded throttle command in `[0, 1]` |
| stability_head | 1 value | `Sigmoid`, approximate control-quality score in `[0, 1]` |
| phase_head | 4 logits | descent phase classification |

The phase classes are:

1. `terminal_descent`
2. `powered_descent`
3. `approach`
4. `high_altitude`

## Training Strategy

The first training stage uses supervised pretraining on synthetic rocket
state/sensor samples.

The teacher policy is a deterministic landing heuristic:

- faster downward velocity increases throttle demand;
- lower altitude increases throttle demand;
- very low fuel reduces throttle aggressiveness;
- near-ground throttle is capped to avoid unrealistic runaway ascent behavior
  in the simplified vertical simulator.

The model optimizes a combined multi-task loss:

```text
loss = throttle_mse + stability_mse + 0.25 * phase_cross_entropy
```

This gives the model three useful skills:

1. continuous throttle imitation;
2. approximate control-quality estimation;
3. coarse descent-phase recognition from sensor state.

## Reproducible Training Command

Install the optional ML dependency group and run the training script:

```bash
uv sync --group ml
uv run python scripts/train_neural_controller.py
```

The script writes generated artifacts to ignored output folders:

```text
outputs/neural_controller/models/neural_rocket_controller.pt
outputs/neural_controller/figures/neural_controller_loss.png
outputs/neural_controller/figures/neural_controller_metrics.png
```

These files are intentionally kept out of Git unless a small curated report is
created later under `docs/results/`.

## Test Coverage

The neural-controller tests are stored in `tests/test_neural_controller.py`.
They validate:

- forward-pass tensor shapes;
- bounded throttle output in `[0, 1]`;
- bounded stability output in `[0, 1]`;
- softmax probability normalization for phase classification;
- synthetic dataset shape and value contracts;
- teacher-policy behavior under safer vs. riskier descent conditions;
- feature normalization;
- single-state inference contract;
- model parameter-count reporting.

The tests use `pytest.importorskip("torch")`, so the base CI can still run even
when the optional ML group is not installed.

## Relationship To The Original Quantum Prototype

The uploaded prototype trained a multi-head neural network on 4-qubit quantum
state features.  It used:

- dense encoder layers;
- `LayerNorm`;
- `GELU`;
- small `Dropout`;
- a classification head with softmax;
- a bounded regression head with sigmoid.

The aerospace version keeps this deep-learning structure but replaces the
problem domain:

| Quantum Prototype | Aerospace Controller |
|---|---|
| 4-qubit statevector features | 13D rocket state/sensor vector |
| separable vs. entangled class | descent phase class |
| entanglement score regression | stability/control-quality regression |
| quantum-state dataset generator | synthetic rocket telemetry generator |
| quantum interpretation | rocket landing control interpretation |

## Current Limitations

This is not yet reinforcement learning and not yet closed-loop neural control
inside the simulator runtime.  It is a supervised neural-controller layer that
can be used as a foundation for future work:

1. connect inference directly to the simulator control loop;
2. compare neural throttle against fixed, heuristic, and PID controllers;
3. generate curated result plots under `docs/results/`;
4. expose a Gymnasium-compatible environment;
5. evolve from supervised imitation to reinforcement learning.
