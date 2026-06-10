import pandas as pd

from aerospace_sim.learning.telemetry_preprocessing import (
    STATE_FEATURES,
    table_state_matrix,
    trajectory_to_sensor_rows,
)


def test_trajectory_preprocessing_builds_neural_sensor_vector() -> None:
    trajectory = pd.DataFrame(
        {
            "position_x_m": [0.0],
            "position_y_m": [0.0],
            "altitude_m": [100.0],
            "velocity_z_m_s": [-10.0],
            "fuel_mass_kg": [800.0],
            "throttle": [0.55],
        }
    )

    table = trajectory_to_sensor_rows(trajectory)
    matrix = table_state_matrix(table)

    assert matrix.shape == (1, len(STATE_FEATURES))
    assert table.loc[0, "target_throttle"] == 0.55
