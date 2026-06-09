# Software Architecture

## Main Layers

- configs: YAML configuration files
- core: shared data structures and config loading
- physics: gravity, thrust, fuel, integration, rotational dynamics
- vehicle: rocket, engine, gimbal, sensors
- environment: landing environment, wind, terrain, reward
- control: PID, neural controller, reinforcement learning agent
- models: PyTorch models and checkpoints
- training: training loops, evaluators, losses, replay buffers
- telemetry: metrics, logs, SQLite database
- visualization: 3D plots, animations, dashboards
- simulation: simulator, episodes, runner

## Simulation Loop

Configuration -> Environment -> Rocket -> Physics Engine -> Updated State -> Controller -> Action -> Physics Engine

## Engineering Rule

No physics, control, training, telemetry, or visualization code should be mixed in the same module.
Each layer must have one clear responsibility.
