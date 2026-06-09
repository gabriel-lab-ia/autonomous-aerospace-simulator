from __future__ import annotations

from pathlib import Path

from matplotlib.axes import Axes
from matplotlib.figure import Figure


BACKGROUND = "#000000"
FOREGROUND = "#E6EDF3"
GRID = "#30363D"
SPINE = "#6E7681"
COLORS = ("#00E5FF", "#FFB000", "#FF4D8D", "#7CFF6B", "#B388FF")


def style_axis(axis: Axes, *, grid: bool = True) -> None:
    """Apply the shared dark report style to a Matplotlib axis."""
    figure = axis.figure
    figure.patch.set_facecolor(BACKGROUND)
    axis.set_facecolor(BACKGROUND)
    axis.tick_params(colors=FOREGROUND)
    axis.xaxis.label.set_color(FOREGROUND)
    axis.yaxis.label.set_color(FOREGROUND)
    axis.title.set_color(FOREGROUND)

    for spine in axis.spines.values():
        spine.set_color(SPINE)

    if grid:
        axis.grid(True, color=GRID, alpha=0.65, linewidth=0.7)

    legend = axis.get_legend()
    if legend is not None:
        legend.get_frame().set_facecolor(BACKGROUND)
        legend.get_frame().set_edgecolor(SPINE)
        for text in legend.get_texts():
            text.set_color(FOREGROUND)
        legend.get_title().set_color(FOREGROUND)


def style_3d_axis(axis: Axes) -> None:
    """Apply the dark style to a 3D axis, including panes and grid lines."""
    style_axis(axis)
    axis.zaxis.label.set_color(FOREGROUND)
    axis.zaxis.set_tick_params(colors=FOREGROUND)

    for pane_axis in (axis.xaxis, axis.yaxis, axis.zaxis):
        pane_axis.pane.set_facecolor(BACKGROUND)
        pane_axis.pane.set_edgecolor(SPINE)
        pane_axis._axinfo["grid"]["color"] = GRID


def save_dark_figure(figure: Figure, output_path: str | Path) -> None:
    """Save a report figure while preserving its black background."""
    figure.tight_layout()
    figure.savefig(
        output_path,
        dpi=160,
        bbox_inches="tight",
        facecolor=figure.get_facecolor(),
    )
