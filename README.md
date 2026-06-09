# Autonomous Aerospace Simulator

A simplified aerospace simulation project for studying rocket landing dynamics and autonomous control.

## Core Objective

Build an extensible simulator where increasingly capable controllers can be evaluated under explicit physical constraints.

The current implementation models deterministic vertical motion using gravity, mass, upward thrust, fuel consumption, and Euler integration. The state representation is 3D-ready, but rotational dynamics, aerodynamics, gimbal control, PID, reinforcement learning, and deployment infrastructure are future work.

## Current Capabilities

- vertical rocket dynamics represented with 3D vectors
- gravity, variable mass, throttle, thrust, and fuel consumption
- fixed-throttle experiments
- landing outcome evaluation
- heuristic landing controllers V1 and V2
- CSV telemetry, PNG plots, and Markdown reports
- reproducible Python environment managed with `uv`

## Technical Stack

- Python 3.11
- NumPy
- Matplotlib
- Pandas
- YAML configs

PyTorch, CUDA-oriented training, SQLite telemetry, and deployment services are planned capabilities and are not integrated into the current simulation loop.

## Quick Start

```bash
uv sync
source .venv/bin/activate
python scripts/run_basic_simulation.py
pytest -q
```

Until the package is installed editable, scripts can also be run explicitly with:

```bash
PYTHONPATH=src python scripts/run_basic_simulation.py
```

See [Reproducibility](docs/reproducibility.md) for all experiment and report-generation commands.

## State Vector

- position: x, y, z
- velocity: vx, vy, vz
- orientation: roll, pitch, yaw
- angular velocity: angular_vx, angular_vy, angular_vz
- fuel mass

## Action Vector

- throttle
- gimbal_x
- gimbal_y

## Roadmap

1. Strengthen physics contracts and automated tests
2. Consolidate scenario configuration and telemetry
3. Implement and benchmark a classical PID controller
4. Add a neural controller baseline
5. Expose the landing task as a reinforcement learning environment
6. Add telemetry database and 3D visualization
7. Add FastAPI, Docker, and Kubernetes deployment layers

## Current Limitations

The simulator is intentionally minimal and should not be treated as a high-fidelity aerospace model. It currently has no real rotational dynamics, aerodynamics, wind, gimbal actuation, or precise collision-time interpolation.

See [Current Simulator Limitations](docs/limitations.md) for the complete scope and engineering implications.

## Initial Results

The first physics validation experiment compares three throttle levels: `0.0`, `0.5`, and `1.0`.

The results show coherent vertical dynamics:

- With zero throttle, the rocket accelerates downward under gravity.
- With half throttle, descent is reduced.
- With full throttle, thrust exceeds weight and vertical velocity becomes positive.

Detailed report:

- [Throttle Comparison Report](docs/results/throttle_comparison.md)
- [Software Engineering Flow](docs/diagrams/software_engineering_flow.md)
- [Physics and Control Loop](docs/diagrams/physics_control_loop.md)

## Results Preview

### Final Altitude by Throttle Level

![Final altitude by throttle](docs/results/throttle_final_altitude.png)

### Final Vertical Velocity by Throttle Level

![Final vertical velocity by throttle](docs/results/throttle_final_velocity.png)

## Trajectory Time-Series Report

The simulator also records full time-series trajectories for altitude, vertical velocity, and fuel mass.

- [Trajectory Report](docs/results/trajectory_report.md)
- [Trajectory Time-Series CSV](docs/results/trajectory_timeseries.csv)

### Altitude Over Time

![Altitude over time](docs/results/trajectory_altitude_over_time.png)

### Vertical Velocity Over Time

![Vertical velocity over time](docs/results/trajectory_velocity_over_time.png)

### Fuel Mass Over Time

![Fuel mass over time](docs/results/trajectory_fuel_over_time.png)

## Landing Evaluation

The simulator now evaluates fixed-throttle landing attempts as `landed`, `crashed`, or `still_flying`.

This experiment shows that fixed throttle cannot solve the landing task by itself: low throttle crashes, while high throttle causes the rocket to keep flying upward.

- [Landing Evaluation Report](docs/results/landing_experiment.md)

### Landing Status by Throttle

![Landing status by throttle](docs/results/landing_status_by_throttle.png)

### Final Vertical Velocity by Throttle

![Landing velocity by throttle](docs/results/landing_velocity_by_throttle.png)

## Heuristic Landing Controller V2

The second heuristic landing controller was tested as a dynamic state-based control policy.

The result shows a runaway ascent failure mode: the controller becomes too aggressive, keeps throttle near maximum, and drives the rocket far above the landing zone.

This failed-control experiment is documented because it motivates the next step: PID control and smoother throttle regulation.

- [Heuristic Controller V2 Report](docs/results/heuristic_v2_report.md)
- [Heuristic Controller V2 Telemetry](docs/results/heuristic_v2_telemetry.csv)

### Heuristic V2 Altitude Over Time

![Heuristic V2 altitude](docs/results/heuristic_v2_altitude_over_time.png)

### Heuristic V2 Throttle Over Time

![Heuristic V2 throttle](docs/results/heuristic_v2_throttle_over_time.png)

## Results Policy

Curated, small, reproducible reports and plots are versioned in `docs/results/` so GitHub visitors can inspect the project without running it first. Raw telemetry, checkpoints, databases, and temporary experiment outputs belong in `outputs/`, which is ignored by Git.
