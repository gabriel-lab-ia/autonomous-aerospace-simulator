from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.visualization.dark_style import (
    BACKGROUND,
    FOREGROUND,
    save_dark_figure,
    style_3d_axis,
)


def save_trajectory_phase_space_3d(
    telemetry: pd.DataFrame,
    output_path: str | Path,
    title: str,
    group_column: str | None = None,
) -> None:
    """Plot time, altitude, and vertical velocity as a 3D phase-space curve."""
    figure = plt.figure(figsize=(10, 7))
    axis = figure.add_subplot(111, projection="3d")

    groups = (
        telemetry.groupby(group_column)
        if group_column is not None
        else [("trajectory", telemetry)]
    )

    for label, group in groups:
        axis.plot(
            group["time_s"],
            group["altitude_m"],
            group["velocity_z_m_s"],
            label=str(label),
        )

    axis.set_title(title)
    axis.set_xlabel("Time (s)")
    axis.set_ylabel("Altitude (m)")
    axis.set_zlabel("Vertical velocity (m/s)")
    if group_column is not None:
        axis.legend(title=group_column)
    style_3d_axis(axis)
    save_dark_figure(figure, output_path)
    plt.close(figure)


def save_control_state_3d(
    telemetry: pd.DataFrame,
    output_path: str | Path,
    title: str,
) -> None:
    """Plot altitude, vertical velocity, and throttle as controller state space."""
    figure = plt.figure(figsize=(10, 7))
    axis = figure.add_subplot(111, projection="3d")
    points = axis.scatter(
        telemetry["altitude_m"],
        telemetry["velocity_z_m_s"],
        telemetry["throttle"],
        c=telemetry["time_s"],
        cmap="viridis",
        s=8,
    )
    axis.set_title(title)
    axis.set_xlabel("Altitude (m)")
    axis.set_ylabel("Vertical velocity (m/s)")
    axis.set_zlabel("Throttle")
    colorbar = figure.colorbar(points, ax=axis, label="Time (s)", shrink=0.7)
    colorbar.ax.set_facecolor(BACKGROUND)
    colorbar.ax.tick_params(colors=FOREGROUND)
    colorbar.set_label("Time (s)", color=FOREGROUND)
    style_3d_axis(axis)
    save_dark_figure(figure, output_path)
    plt.close(figure)


def save_landing_summary_3d(
    results: pd.DataFrame,
    output_path: str | Path,
    title: str,
) -> None:
    """Plot throttle, final velocity, and final altitude for landing attempts."""
    figure = plt.figure(figsize=(10, 7))
    axis = figure.add_subplot(111, projection="3d")
    points = axis.scatter(
        results["throttle"],
        results["final_velocity_z_m_s"],
        results["final_altitude_m"],
        c=results["final_time_s"],
        cmap="plasma",
        s=80,
    )
    axis.set_title(title)
    axis.set_xlabel("Throttle")
    axis.set_ylabel("Final vertical velocity (m/s)")
    axis.set_zlabel("Final altitude (m)")
    colorbar = figure.colorbar(points, ax=axis, label="Final time (s)", shrink=0.7)
    colorbar.ax.set_facecolor(BACKGROUND)
    colorbar.ax.tick_params(colors=FOREGROUND)
    colorbar.set_label("Final time (s)", color=FOREGROUND)
    style_3d_axis(axis)
    save_dark_figure(figure, output_path)
    plt.close(figure)
