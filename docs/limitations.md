# Current Simulator Limitations

The current simulator is a deterministic educational baseline, not a high-fidelity flight dynamics model.

## Physical Model

- Motion is essentially vertical and one-dimensional, although position and velocity use `Vector3`.
- Orientation and angular velocity are stored in `RocketState` but are not integrated.
- Thrust always points upward along the positive z-axis.
- There is no aerodynamic drag, atmospheric model, lift, wind, terrain, or real gimbal actuation.
- Gravity is constant and does not vary with altitude.
- Ground contact clamps altitude to zero after a step; the exact collision time is not interpolated.
- Euler integration introduces numerical error and has not been compared with higher-order integrators.

## Control And Learning

- Fixed-throttle and heuristic controllers are implemented.
- No PID controller is implemented yet.
- No neural controller or reinforcement learning environment is implemented yet.
- Heuristic V1 and V2 are useful failure baselines, not successful landing solutions.

## Platform And Operations

- The current vertical scenario is centralized in YAML; controller-specific tuning remains in controller classes.
- Telemetry uses a reusable dataframe-backed recorder and CSV files; there is no telemetry database yet.
- There is no API, web service, Docker image, Kubernetes deployment, or automated training pipeline.
- The repository does not currently claim flightworthiness or real-world control suitability.

These limitations are intentional milestones. They make each future physics, control, and MLOps improvement measurable against a small, understandable baseline.
