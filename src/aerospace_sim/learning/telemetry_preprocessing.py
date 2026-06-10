from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


STATE_FEATURES = (
    "position_x_m",
    "position_y_m",
    "altitude_z_m",
    "velocity_x_mps",
    "velocity_y_mps",
    "vertical_velocity_z_mps",
    "roll_rad",
    "pitch_rad",
    "yaw_rad",
    "angular_velocity_x_radps",
    "angular_velocity_y_radps",
    "angular_velocity_z_radps",
    "fuel_mass_kg",
)


def trajectory_to_sensor_rows(trajectory: pd.DataFrame) -> pd.DataFrame:
    """Map simulator telemetry into the neural controller's sensor schema."""
    required = {
        "position_x_m",
        "position_y_m",
        "altitude_m",
        "velocity_z_m_s",
        "fuel_mass_kg",
        "throttle",
    }
    missing = required.difference(trajectory.columns)
    if missing:
        raise ValueError(f"Trajectory is missing required columns: {sorted(missing)}")

    rows = pd.DataFrame(0.0, index=trajectory.index, columns=STATE_FEATURES)
    rows["position_x_m"] = trajectory["position_x_m"]
    rows["position_y_m"] = trajectory["position_y_m"]
    rows["altitude_z_m"] = trajectory["altitude_m"]
    rows["vertical_velocity_z_mps"] = trajectory["velocity_z_m_s"]
    rows["fuel_mass_kg"] = trajectory["fuel_mass_kg"]
    rows["target_throttle"] = trajectory["throttle"].clip(0.0, 1.0)
    if "controller" in trajectory:
        rows["source_controller"] = trajectory["controller"]
    return rows


def prepare_training_table(
    trajectory_paths: list[Path],
    *,
    output_path: Path | None = None,
) -> pd.DataFrame:
    """Combine accessible simulated trajectories into a supervised table."""
    tables = [
        trajectory_to_sensor_rows(pd.read_csv(path)).assign(source_path=str(path))
        for path in trajectory_paths
    ]
    if not tables:
        raise ValueError("At least one trajectory path is required.")
    combined = pd.concat(tables, ignore_index=True)
    if output_path is not None:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        combined.to_csv(output_path, index=False)
    return combined


def table_state_matrix(table: pd.DataFrame) -> np.ndarray:
    """Return raw 13-dimensional state vectors from a prepared table."""
    missing = set(STATE_FEATURES).difference(table.columns)
    if missing:
        raise ValueError(f"Training table is missing state columns: {sorted(missing)}")
    return table.loc[:, STATE_FEATURES].to_numpy(dtype=np.float32)
