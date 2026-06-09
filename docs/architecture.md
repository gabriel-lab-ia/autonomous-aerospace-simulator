# Software Architecture

## Implemented Layers

- configs: YAML configuration files
- core: shared data structures and config loading
- physics: constant Earth gravity
- vehicle: simplified throttle-controlled rocket engine
- environment: landing outcome evaluation
- control: heuristic landing controllers
- simulation: Euler-integrated basic rocket simulator

## Planned Layers

- physics: aerodynamics and rotational dynamics
- vehicle: gimbal and sensors
- environment: wind, terrain, rewards, and RL environment interface
- control: PID, neural controllers, and reinforcement learning agents
- models: PyTorch models and checkpoints
- training: training loops, evaluators, losses, and replay buffers
- telemetry: reusable metrics, logs, and database integration
- visualization: reusable plots, 3D animations, and dashboards

## Simulation Loop

Initial State -> Controller or Fixed Throttle -> Engine and Gravity -> Simulator Step -> Updated State -> Evaluation and Telemetry

## Engineering Rule

Physics, control, training, telemetry, and visualization should remain independently testable. Current scripts still coordinate telemetry and plots; these responsibilities can move into reusable modules as their interfaces stabilize.
