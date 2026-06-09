# Software Architecture

## Implemented Layers

- configs: YAML configuration files
- core: shared data structures and config loading
- physics: constant Earth gravity
- vehicle: simplified throttle-controlled rocket engine
- environment: landing outcome evaluation
- control: heuristic landing controllers
- simulation: Euler-integrated basic rocket simulator
- telemetry: reusable, dataframe-backed telemetry recorder
- visualization: reusable 3D phase-space and controller-state plots
- api: authenticated FastAPI routes and validated request/response schemas
- database: SQLAlchemy persistence for simulation metadata and telemetry

## Planned Layers

- physics: aerodynamics and rotational dynamics
- vehicle: gimbal and sensors
- environment: wind, terrain, rewards, and RL environment interface
- control: PID, neural controllers, and reinforcement learning agents
- models: PyTorch models and checkpoints
- training: training loops, evaluators, losses, and replay buffers
- telemetry: persistent metrics, logs, and database integration
- visualization: 3D animations and dashboards

## Simulation Loop

API or Script -> YAML Scenario -> Initial State -> Controller or Fixed Throttle -> Simulator Step -> Evaluation and Telemetry -> SQL or Curated Results

## Engineering Rule

Physics, control, scenario construction, telemetry, and visualization remain independently testable. Scripts coordinate experiments and report generation through these reusable library contracts.
