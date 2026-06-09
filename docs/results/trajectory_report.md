# Trajectory Time-Series Experiment

This experiment records the full simulated trajectory over time for three throttle levels: `0.0`, `0.5`, and `1.0`.

Unlike the initial throttle comparison, this report tracks the evolution of:

- altitude
- vertical velocity
- total speed
- fuel mass
- simulation time

## Final-State Summary

|   throttle |   final_time_s |   final_altitude_m |   final_velocity_z_m_s |   final_speed_m_s |   final_fuel_mass_kg |
|-----------:|---------------:|-------------------:|-----------------------:|------------------:|---------------------:|
|        0   |              2 |            60.1906 |              -29.6133  |          29.6133  |                800   |
|        0.5 |              2 |            77.8729 |              -12.1025  |          12.1025  |                797.5 |
|        1   |              2 |            95.5698 |                5.43008 |           5.43008 |                795   |

## Altitude Over Time

![Altitude over time](trajectory_altitude_over_time.png)

## Vertical Velocity Over Time

![Vertical velocity over time](trajectory_velocity_over_time.png)

## Fuel Mass Over Time

![Fuel mass over time](trajectory_fuel_over_time.png)

## 3D Phase Space

![Trajectory phase space](trajectory_phase_space_3d.png)

This 3D plot uses time, altitude, and vertical velocity. It visualizes the current
vertical dynamics without implying lateral motion that the simulator does not yet model.

## Engineering Interpretation

The trajectory curves validate the simulator as a time-dependent dynamical system.

- With `0.0` throttle, the rocket continues accelerating downward under gravity.
- With `0.5` throttle, thrust partially offsets gravity and reduces descent rate.
- With `1.0` throttle, thrust exceeds weight and reverses vertical velocity upward.

This confirms that the current simulation loop connects force, mass, acceleration, velocity, position, fuel consumption, and time through Euler integration.
