# Throttle Comparison Experiment

This experiment validates the first simplified vertical rocket dynamics model.

The simulator compares three throttle levels:

- `0.0`: free fall under gravity
- `0.5`: partial thrust
- `1.0`: maximum thrust

## Results

|   throttle |   final_altitude_m |   final_velocity_z_m_s |   final_speed_m_s |   fuel_mass_kg |   time_s |
|-----------:|-------------------:|-----------------------:|------------------:|---------------:|---------:|
|        0   |            60.1906 |              -29.6133  |          29.6133  |          800   |        2 |
|        0.5 |            77.8729 |              -12.1025  |          12.1025  |          797.5 |        2 |
|        1   |            95.5698 |                5.43008 |           5.43008 |          795   |        2 |

## Interpretation

The results show physically coherent behavior:

- With `0.0` throttle, the rocket falls faster and reaches the lowest altitude.
- With `0.5` throttle, descent is reduced because thrust partially offsets gravity.
- With `1.0` throttle, thrust exceeds weight and the rocket reverses vertical velocity upward.

## Final Altitude

![Final altitude by throttle](throttle_final_altitude.png)

## Final Vertical Velocity

![Final vertical velocity by throttle](throttle_final_velocity.png)

## Engineering Meaning

This validates that the simulator already connects mass, gravity, thrust, fuel consumption, acceleration, velocity, and position through a basic Euler integration loop.
