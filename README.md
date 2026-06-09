# Autonomous Aerospace Simulator

A 3D computational aerospace simulation project focused on autonomous rocket landing, control systems, deep learning, reinforcement learning, telemetry, and GPU-accelerated training.

## Core Objective

Build a simplified but extensible 3D rocket landing simulator where autonomous controllers learn to stabilize and land a reusable rocket under physical constraints.

## Technical Stack

- Python 3.11
- NumPy
- SciPy
- PyTorch + CUDA
- Matplotlib
- Pandas
- YAML configs
- SQLite telemetry
- Jupyter notebooks

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

1. Project foundation
2. Physics engine
3. Classical PID control
4. Neural controller
5. Reinforcement learning
6. 3D visualization
7. FastAPI, Docker, and Kubernetes layer

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