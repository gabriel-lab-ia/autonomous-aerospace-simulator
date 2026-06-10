# Autonomous Aerospace Simulator

<p align="center">
  <img width="100%" alt="Autonomous rocket landing platform" src="https://github.com/user-attachments/assets/33e5ff6a-94fd-49a0-a093-23e3aaeab410">
</p>

<p align="center">
  <a href="https://github.com/gabriel-lab-ia/autonomous-aerospace-simulator/actions/workflows/ci.yml">
    <img src="https://github.com/gabriel-lab-ia/autonomous-aerospace-simulator/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
  <img src="https://img.shields.io/badge/Python-3.11+-3776AB?logo=python&logoColor=white" alt="Python 3.11+">
  <img src="https://img.shields.io/badge/FastAPI-secure_API-009688?logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SQLAlchemy-SQL_telemetry-D71F00?logo=sqlalchemy&logoColor=white" alt="SQLAlchemy">
  <img src="https://img.shields.io/badge/SQLite-local_DB-003B57?logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/PostgreSQL-ready-4169E1?logo=postgresql&logoColor=white" alt="PostgreSQL ready">
  <img src="https://img.shields.io/badge/Pytest-tested-0A9EDC?logo=pytest&logoColor=white" alt="Pytest">
  <img src="https://img.shields.io/badge/License-MIT-green.svg" alt="MIT License">
</p>

A portfolio-grade aerospace simulation platform for rocket landing dynamics,
autonomous control experiments, secure API execution, and SQL-backed telemetry.

## Core Objective

Build an extensible simulator where increasingly capable controllers can be evaluated under explicit physical constraints.

The current implementation models deterministic vertical motion using gravity, mass, upward thrust, fuel consumption, and Euler integration. The state representation is 3D-ready, but rotational dynamics, aerodynamics, gimbal control, reinforcement learning, and deployment infrastructure are future work.

## Current Capabilities

- vertical rocket dynamics represented with 3D vectors
- gravity, variable mass, throttle, thrust, and fuel consumption
- fixed-throttle experiments
- landing outcome evaluation
- heuristic landing controllers V1 and V2
- classical PID landing-controller baseline
- optional experimental neural controller integrated through the controller contract
- shared-scenario controller trajectory benchmark with CSV/JSON metrics
- generated controller comparison report and dark comparative plots
- reusable YAML scenario construction and standardized telemetry
- CSV telemetry, 2D/3D PNG plots, and Markdown reports
- reproducible Python environment managed with `uv`
- automated pytest validation with GitHub Actions
- secure FastAPI service with SQL-backed simulation telemetry
- API key authentication with bounded request schemas
- SQLite local persistence and PostgreSQL-ready configuration

## Control Engineering System

The control layer is organized as an experimental engineering pipeline, not as
an isolated notebook or a claim of flight-ready autonomy:

```mermaid
flowchart LR
    CFG[YAML Scenario + PID Config] --> PHYSICS[Vertical Physics Simulation]
    PHYSICS --> CONTRACT["compute_throttle(state) Contract"]
    CONTRACT --> FIXED[Fixed Throttle]
    CONTRACT --> H1[Heuristic V1]
    CONTRACT --> H2[Heuristic V2]
    CONTRACT --> PID[PID Baseline]
    CONTRACT --> NEURAL[Optional Neural Controller]
    FIXED --> TELEMETRY[Standardized Telemetry]
    H1 --> TELEMETRY
    H2 --> TELEMETRY
    PID --> TELEMETRY
    NEURAL --> TELEMETRY
    TELEMETRY --> BENCHMARK[Shared-Scenario Benchmark]
    BENCHMARK --> METRICS[CSV + JSON Metrics]
    BENCHMARK --> REPORTS[Plots + Markdown Report]
    TELEMETRY --> PREPROCESS[Neural Data Preprocessing]
    PREPROCESS --> TRAIN[Supervised Imitation Training]
    BENCHMARK -. future work .-> RL[RL Environment Plan]
```

| Controller | Engineering status | Benchmark result |
| --- | --- | --- |
| Fixed throttle | Implemented open-loop baseline | Crashed at `11.4050 m/s` |
| Heuristic V1 | Implemented rule-based baseline | Still flying after `60 s` |
| Heuristic V2 | Implemented rule-based failure baseline | Runaway ascent to `13,974.0973 m` |
| PID | Implemented classical feedback baseline | Crashed at `3.4798 m/s`; improved but not safe |
| Neural supervised | Experimental, optional PyTorch | Did not demonstrate landing |
| Reinforcement learning | Future work only | Not executed |

The PID baseline materially reduces impact speed relative to fixed throttle,
but it does not satisfy the current safe-landing threshold. The neural
controller and RL plan remain experimental. These results apply only to the
simplified deterministic vertical simulator.

- [Controller Implementation Status](docs/results/controller_comparison.md)
- [Real Controller Trajectory Benchmark](docs/results/controller_trajectory_comparison.md)
- [RL Environment Plan](docs/rl_environment_plan.md)

## Technical Stack

- Python 3.11
- NumPy
- Matplotlib
- Pandas
- YAML configs
- FastAPI and Pydantic
- SQLAlchemy with SQLite and optional PostgreSQL
- Pytest and GitHub Actions

PyTorch is an optional dependency used for supervised neural-controller
pretraining and experimental inference. Container-orchestration deployment
services remain planned.

## Secure API And SQL Telemetry Layer

The project includes a FastAPI service with API key authentication and a
SQLAlchemy-backed telemetry store. SQLite supports local development by
default, while `DATABASE_URL` keeps the persistence layer ready for PostgreSQL.

```bash
uv sync --group dev
cp .env.example .env
uv run python scripts/run_api.py
```

- Public health endpoint: `GET /health`
- Protected simulation execution: `POST /simulations/*`
- Protected metadata and telemetry queries: `GET /simulations` and `GET /telemetry/{id}`
- [API architecture, security, and curl examples](docs/api.md)

## Engineering Architecture

The project keeps scenario construction, physical integration, control,
telemetry, visualization, and reporting independently testable.

```mermaid
flowchart LR
    CFG[YAML Scenario] --> STATE[Initial State]
    CFG --> SIM[Simulator]
    STATE --> CTRL[Fixed / Heuristic / PID / Neural Controller]
    CTRL --> ACTION[Throttle]
    ACTION --> SIM
    SIM --> NEXT[Next State]
    NEXT --> TELEMETRY[Telemetry]
    NEXT --> EVAL[Landing Evaluation]
    TELEMETRY --> BENCHMARK[Controller Benchmark]
    BENCHMARK --> RESULTS[CSV + JSON + Plots + Reports]
```

- [Current Architecture](docs/diagrams/current_architecture.md)
- [Verification Pipeline](docs/diagrams/verification_pipeline.md)
- [Configuration And Telemetry Contracts](docs/configuration_and_telemetry.md)

## Quick Start

```bash
uv sync --locked --group dev
uv run pytest -q
uv run python scripts/benchmark_controllers.py
```

`uv sync` installs the package editable. For a manually managed environment,
scripts can also be run explicitly with:

```bash
PYTHONPATH=src python scripts/run_basic_simulation.py
```

See [Reproducibility](docs/reproducibility.md) for all experiment and report-generation commands.

## Reproduce The Controller Benchmark

All executed controllers use the same initial scenario whenever possible:
altitude `100 m`, vertical velocity `-10 m/s`, time step `0.02 s`, and a
maximum duration of `60 s`.

```bash
uv sync --locked --group dev
uv run python scripts/benchmark_controllers.py
```

Generated raw artifacts:

```text
outputs/controller_benchmark/controller_comparison.csv
outputs/controller_benchmark/controller_comparison.json
outputs/controller_benchmark/trajectories/<controller_name>.csv
outputs/controller_benchmark/figures/*.png
```

Small curated plots and the generated report are versioned under
`docs/results/`.

### Real Shared-Scenario Results

| Controller | Status | Final altitude (m) | Final vertical velocity (m/s) | Fuel remaining (kg) | Mean throttle |
| --- | --- | ---: | ---: | ---: | ---: |
| Fixed throttle | crashed | `0.0000` | `-11.4050` | `787.1850` | `0.5500` |
| Heuristic V1 | still flying | `263.6417` | `3.0571` | `715.8963` | `0.5608` |
| Heuristic V2 | still flying | `13,974.0973` | `489.5257` | `650.4656` | `0.9969` |
| PID | crashed | `0.0000` | `-3.4798` | `784.9199` | `0.5949` |
| Neural supervised | still flying | `1,739.5862` | `115.0260` | `700.6346` | `0.6625` |

![Controller altitude comparison](docs/results/controller_altitude_comparison.png)

![Controller velocity comparison](docs/results/controller_velocity_comparison.png)

The benchmark is a software/control regression experiment. It is not
high-fidelity aerospace validation.

## State Vector

- position: x, y, z
- velocity: vx, vy, vz
- orientation: roll, pitch, yaw
- angular velocity: angular_vx, angular_vy, angular_vz
- fuel mass

## Action Vector

- throttle

Gimbal commands are reserved for a future rotational-dynamics model.

## Roadmap

1. Tune and stress-test the implemented PID baseline
2. Train neural imitation baselines from PID and benchmark trajectories
3. Add a tested Gymnasium-compatible RL environment and reward penalties
4. Expand controller benchmarking across initial-state scenarios
5. Add precise ground-contact interpolation and stronger physics validation
6. Add a Dockerfile and Docker Compose stack with API and PostgreSQL
7. Build a telemetry visualization dashboard
8. Prepare a future Kubernetes deployment

## Current Limitations

The simulator is intentionally minimal and should not be treated as a high-fidelity aerospace model. It currently has no real rotational dynamics, aerodynamics, wind, gimbal actuation, or precise collision-time interpolation.

See [Current Simulator Limitations](docs/limitations.md) for the complete scope and engineering implications.

## Deep Neural Rocket Controller

The optional neural layer provides supervised neural-controller pretraining on
synthetic or simulator-derived telemetry and experimental inference through the
real simulator loop. This is a foundation for future simulator-in-the-loop
reinforcement learning, not high-fidelity aerospace validation.

### Parameter Metrics

| Metric | Value |
| --- | ---: |
| Total trainable parameters | 586,630 |

### Simulator-Telemetry Training Pipeline

The neural training path can extract accessible data from the benchmark
trajectories, transform it into the existing 13-dimensional sensor/state
schema, normalize the features, and run supervised imitation training:

```bash
uv sync --locked --group dev --group ml
uv run python scripts/benchmark_controllers.py
uv run python scripts/prepare_neural_training_data.py
uv run python scripts/train_neural_controller.py \
  --dataset outputs/neural_controller/preprocessed_controller_telemetry.csv
```

This pipeline was smoke-tested with `7,500` simulated telemetry rows. It uses
simulator-derived data, not real aerospace flight data. PyTorch remains
optional: the base CI environment runs without the ML group.

- [Deep Neural Controller Documentation](docs/neural_controller.md)
- [Neural Controller Training Report](docs/results/neural_controller_training_report.md)
- [Controller Comparison](docs/results/controller_comparison.md)
- [Controller Trajectory Comparison](docs/results/controller_trajectory_comparison.md)
- [RL Environment Plan](docs/rl_environment_plan.md)

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

## Numerical Validation Matrices

The automated tests validate the contracts behind the numerical state and
transition matrices. The generated report explains every value and can be
regenerated from the default YAML scenario.

### Initial State Vector (13 x 1)

| Index range | Components | Default values |
|---|---|---|
| 0-2 | position `(x, y, z)` m | `(0, 0, 100)` |
| 3-5 | velocity `(vx, vy, vz)` m/s | `(0, 0, -10)` |
| 6-8 | orientation `(roll, pitch, yaw)` rad | `(0, 0, 0)` |
| 9-11 | angular velocity `(x, y, z)` rad/s | `(0, 0, 0)` |
| 12 | fuel mass kg | `800` |

### One-Step Transition Matrix (`dt = 0.02 s`)

| Throttle | Next altitude (m) | Next vertical velocity (m/s) | Next fuel mass (kg) |
|---:|---:|---:|---:|
| 0.0 | 99.796077 | -10.196133 | 800.000 |
| 0.5 | 99.799577 | -10.021133 | 799.975 |
| 1.0 | 99.803077 | -9.846133 | 799.950 |

The rows share the same initial state. Increasing throttle raises net
acceleration and fuel consumption; gravity remains active in every row.

- [Complete Numerical Validation Report](docs/results/numerical_validation.md)
- [Initial State Vector CSV](docs/results/initial_state_vector.csv)
- [One-Step Transition Matrix CSV](docs/results/one_step_transition_matrix.csv)

## Results Preview

All curated report plots use a reproducible high-contrast dark visual style
implemented in `aerospace_sim.visualization`.

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

### Fixed-Throttle 3D Phase Space

![Fixed-throttle 3D phase space](docs/results/trajectory_phase_space_3d.png)

This R3 visualization uses time, altitude, and vertical velocity. It does not
claim lateral motion that the current vertical model does not simulate.

## Landing Evaluation

The simulator now evaluates fixed-throttle landing attempts as `landed`, `crashed`, or `still_flying`.

This experiment shows that fixed throttle cannot solve the landing task by itself: low throttle crashes, while high throttle causes the rocket to keep flying upward.

- [Landing Evaluation Report](docs/results/landing_experiment.md)

### Landing Status by Throttle

![Landing status by throttle](docs/results/landing_status_by_throttle.png)

### Final Vertical Velocity by Throttle

![Landing velocity by throttle](docs/results/landing_velocity_by_throttle.png)

### Fixed-Throttle 3D Landing Outcomes

![Fixed-throttle 3D landing outcomes](docs/results/landing_summary_3d.png)

## Heuristic Landing Controller V2

The second heuristic landing controller was tested as a dynamic state-based control policy.

The result shows a runaway ascent failure mode: the controller becomes too aggressive, keeps throttle near maximum, and drives the rocket far above the landing zone.

This failed-control experiment is documented because it motivates PID tuning
and smoother throttle regulation.

- [Heuristic Controller V2 Report](docs/results/heuristic_v2_report.md)
- [Heuristic Controller V2 Telemetry](docs/results/heuristic_v2_telemetry.csv)

### Heuristic V2 Altitude Over Time

![Heuristic V2 altitude](docs/results/heuristic_v2_altitude_over_time.png)

### Heuristic V2 Throttle Over Time

![Heuristic V2 throttle](docs/results/heuristic_v2_throttle_over_time.png)

### Heuristic V2 3D Controller State

![Heuristic V2 3D controller state](docs/results/heuristic_v2_control_state_3d.png)

## Results Policy

Curated, small, reproducible reports and plots are versioned in `docs/results/` so GitHub visitors can inspect the project without running it first. Raw telemetry, checkpoints, databases, and temporary experiment outputs belong in `outputs/`, which is ignored by Git.
