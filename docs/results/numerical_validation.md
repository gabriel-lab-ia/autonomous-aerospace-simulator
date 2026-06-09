# Numerical Validation Matrices

This report exposes the numerical contracts used by the automated tests and
simulation experiments. Values are generated from `configs/default.yaml`.

## Initial State Vector

`RocketState.to_vector()` produces a 13 x 1 numerical vector for future control
and machine-learning interfaces.

|   index | state                    |   value |
|--------:|:-------------------------|--------:|
|       0 | position_x_m             |       0 |
|       1 | position_y_m             |       0 |
|       2 | altitude_m               |     100 |
|       3 | velocity_x_m_s           |       0 |
|       4 | velocity_y_m_s           |       0 |
|       5 | velocity_z_m_s           |     -10 |
|       6 | roll_rad                 |       0 |
|       7 | pitch_rad                |       0 |
|       8 | yaw_rad                  |       0 |
|       9 | angular_velocity_x_rad_s |       0 |
|      10 | angular_velocity_y_rad_s |       0 |
|      11 | angular_velocity_z_rad_s |       0 |
|      12 | fuel_mass_kg             |     800 |

## One-Step Transition Matrix

Each row applies one simulator step (`dt = 0.02 s`) from the same initial state.
The matrix demonstrates how throttle changes acceleration and fuel consumption
while gravity remains active.

|   throttle |   initial_altitude_m |   initial_velocity_z_m_s |   next_altitude_m |   next_velocity_z_m_s |   next_fuel_mass_kg |
|-----------:|---------------------:|-------------------------:|------------------:|----------------------:|--------------------:|
|        0   |                  100 |                      -10 |           99.7961 |             -10.1961  |             800     |
|        0.5 |                  100 |                      -10 |           99.7996 |             -10.0211  |             799.975 |
|        1   |                  100 |                      -10 |           99.8031 |              -9.84613 |             799.95  |

## Technical Interpretation

- `throttle = 0.0`: velocity becomes more negative because only gravity acts.
- `throttle = 0.5`: partial thrust reduces the downward acceleration.
- `throttle = 1.0`: full thrust produces upward acceleration, but one step is
  not long enough to reverse the initial downward velocity.
- Fuel consumption is proportional to throttle and is bounded by available fuel.
- Automated tests separately verify vector operations, gravity direction,
  throttle clamping, fuel exhaustion, ground clamping, scenario validation,
  telemetry schema, and landing classification.
