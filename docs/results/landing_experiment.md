# Landing Evaluation Experiment

This experiment evaluates whether fixed throttle values can land the rocket safely.

The simulation classifies each run as:

- `landed`: touchdown occurred within safe velocity limits
- `crashed`: touchdown occurred with excessive velocity
- `still_flying`: the rocket did not reach the ground before the maximum simulation time

## Results

|   throttle | status       | reason                                           | terminal_reason   |   final_altitude_m |   final_velocity_z_m_s |   final_speed_m_s |   final_time_s |   final_fuel_mass_kg |
|-----------:|:-------------|:-------------------------------------------------|:------------------|-------------------:|-----------------------:|------------------:|---------------:|---------------------:|
|       0    | crashed      | Touchdown velocity exceeded safe landing limits. | ground_contact    |               0    |               -45.5001 |           45.5001 |           3.62 |              800     |
|       0.25 | crashed      | Touchdown velocity exceeded safe landing limits. | ground_contact    |               0    |               -34.4286 |           34.4286 |           4.5  |              797.187 |
|       0.5  | crashed      | Touchdown velocity exceeded safe landing limits. | ground_contact    |               0    |               -17.5271 |           17.5271 |           7.26 |              790.925 |
|       0.75 | still_flying | Rocket has not reached the ground yet.           | max_steps_reached |            5930.89 |               212.109  |          212.109  |          60    |              687.5   |
|       1    | still_flying | Rocket has not reached the ground yet.           | max_steps_reached |           14171.1  |               493.048  |          493.048  |          60    |              650     |

## Landing Status by Throttle

![Landing status by throttle](landing_status_by_throttle.png)

## Final Vertical Velocity by Throttle

![Final vertical velocity by throttle](landing_velocity_by_throttle.png)

## Engineering Interpretation

The experiment shows that fixed throttle is not sufficient for reliable landing.

- Low throttle values result in crashes because thrust is not enough to slow descent.
- High throttle values keep the rocket flying upward instead of landing.
- A safe landing requires dynamic control, not constant thrust.

This motivates the next engineering step: implementing a controller that adjusts throttle based on altitude and vertical velocity.
