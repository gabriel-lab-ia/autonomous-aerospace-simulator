# Reinforcement Learning Environment Plan

Reinforcement learning is not implemented or executed in the current project.
This document defines a future simulator-in-the-loop experiment without
claiming that an RL policy has learned to land.

## Proposed Interface

- Gymnasium-compatible environment wrapping `SimulationScenario`.
- Observation: normalized 13-dimensional `RocketState` plus previous throttle.
- Action: one bounded continuous throttle command in `[0, 1]`.
- Termination: ground contact, unrecoverable fuel exhaustion, or step limit.

## Proposed Reward And Error Penalties

```text
reward =
  - velocity_weight * abs(target_velocity - velocity_z)
  - altitude_weight * normalized_altitude
  - fuel_weight * fuel_used
  - saturation_weight * throttle_saturation
  - smoothness_weight * abs(throttle - previous_throttle)
  + safe_touchdown_bonus
  - crash_penalty
```

The weights must be versioned and evaluated against Fixed, Heuristic V1,
Heuristic V2, PID, and supervised neural baselines. Reward improvement alone
must not be reported as landing success.

## Safety Constraints

- Clamp every action before simulation.
- Reject non-finite observations and actions.
- Bound episode duration and initial-state ranges.
- Keep training isolated from any real actuator or flight interface.
- Report collision speed, saturation, fuel use, and trajectory metrics.

## Why RL Is Not Implemented Yet

The current vertical model lacks aerodynamics, rotation, actuator dynamics,
sensor noise, and precise ground-contact interpolation. Implementing an RL
agent before stabilizing these contracts would optimize a narrow model and
could produce misleading claims. The next milestone is a tested environment
wrapper and reward function, followed by reproducible baseline comparison.
