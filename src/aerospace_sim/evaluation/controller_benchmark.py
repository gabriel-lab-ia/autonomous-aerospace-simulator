from __future__ import annotations

import json
import shutil
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.control.heuristic_landing_controller import (
    HeuristicLandingController as HeuristicLandingControllerV1,
)
from aerospace_sim.control.heuristic_landing_controller_v2 import (
    HeuristicLandingController as HeuristicLandingControllerV2,
)
from aerospace_sim.control.pid_controller import PIDLandingController
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.runner import ThrottleController, run_scenario
from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.visualization.dark_style import COLORS, save_dark_figure, style_axis


OUTPUT_DIR = Path("outputs/controller_benchmark")
CURATED_DIR = Path("docs/results")
CHECKPOINT_PATH = Path("outputs/neural_controller/neural_controller.pt")
SATURATION_EPSILON = 0.01


@dataclass(frozen=True)
class ControllerMetrics:
    controller: str
    final_altitude_m: float | None
    final_vertical_velocity_m_s: float | None
    final_fuel_mass_kg: float | None
    min_altitude_m: float | None
    max_altitude_m: float | None
    flight_time_s: float | None
    landing_status: str
    touchdown_speed_m_s: float | None
    throttle_mean: float | None
    throttle_max: float | None
    throttle_saturation_fraction: float | None
    controller_notes: str


def _controller_factories(
    scenario: SimulationScenario,
    checkpoint_path: Path,
) -> list[tuple[str, Callable[[], ThrottleController] | None, float | None, str]]:
    controllers: list[
        tuple[str, Callable[[], ThrottleController] | None, float | None, str]
    ] = [
        ("fixed_throttle", None, 0.55, "Open-loop fixed throttle baseline."),
        (
            "heuristic_v1",
            HeuristicLandingControllerV1,
            None,
            "Manual rule-based baseline V1.",
        ),
        (
            "heuristic_v2",
            HeuristicLandingControllerV2,
            None,
            "Manual rule-based baseline V2 with known ascent failure mode.",
        ),
        (
            "pid",
            lambda: PIDLandingController.from_yaml(
                dt=scenario.dt,
                dry_mass_kg=scenario.dry_mass,
                max_thrust_n=scenario.max_thrust,
            ),
            None,
            "Classical feedback baseline; gains are not optimized.",
        ),
    ]
    try:
        from aerospace_sim.control.neural_controller import NeuralController

        if checkpoint_path.exists():
            controllers.append(
                (
                    "neural_supervised",
                    lambda: NeuralController(checkpoint_path=checkpoint_path),
                    None,
                    "Experimental supervised controller using the available checkpoint.",
                )
            )
        else:
            def make_reproducible_untrained_neural() -> ThrottleController:
                import torch

                torch.manual_seed(42)
                return NeuralController(allow_untrained=True)

            controllers.append(
                (
                    "neural_untrained",
                    make_reproducible_untrained_neural,
                    None,
                    "Experimental untrained network; included only as a failure baseline.",
                )
            )
    except ImportError:
        controllers.append(
            (
                "neural_optional_unavailable",
                None,
                None,
                "Not executed because the optional PyTorch dependency is unavailable.",
            )
        )
    return controllers


def _metrics_from_run(name: str, notes: str, run) -> tuple[ControllerMetrics, pd.DataFrame]:
    telemetry = run.telemetry.to_dataframe()
    evaluation = evaluate_landing(run.final_state)
    touchdown_speed = (
        abs(run.final_state.velocity.z) if run.terminal_reason == "ground_contact" else None
    )
    saturated = (
        (telemetry["throttle"] <= SATURATION_EPSILON)
        | (telemetry["throttle"] >= 1.0 - SATURATION_EPSILON)
    )
    metrics = ControllerMetrics(
        controller=name,
        final_altitude_m=float(run.final_state.altitude),
        final_vertical_velocity_m_s=float(run.final_state.velocity.z),
        final_fuel_mass_kg=float(run.final_state.fuel_mass),
        min_altitude_m=float(telemetry["altitude_m"].min()),
        max_altitude_m=float(telemetry["altitude_m"].max()),
        flight_time_s=float(run.final_state.time),
        landing_status=evaluation.status.value,
        touchdown_speed_m_s=touchdown_speed,
        throttle_mean=float(telemetry["throttle"].mean()),
        throttle_max=float(telemetry["throttle"].max()),
        throttle_saturation_fraction=float(saturated.mean()),
        controller_notes=notes,
    )
    telemetry.insert(0, "controller", name)
    return metrics, telemetry


def run_controller_benchmark(
    *,
    scenario: SimulationScenario | None = None,
    output_dir: Path = OUTPUT_DIR,
    curated_dir: Path = CURATED_DIR,
    checkpoint_path: Path = CHECKPOINT_PATH,
    generate_plots: bool = True,
    generate_report: bool = True,
) -> pd.DataFrame:
    """Run controllers on one scenario and write reproducible benchmark artifacts."""
    scenario = scenario or SimulationScenario.from_yaml()
    trajectory_dir = output_dir / "trajectories"
    figure_dir = output_dir / "figures"
    trajectory_dir.mkdir(parents=True, exist_ok=True)
    figure_dir.mkdir(parents=True, exist_ok=True)
    curated_dir.mkdir(parents=True, exist_ok=True)

    metrics: list[ControllerMetrics] = []
    trajectories: dict[str, pd.DataFrame] = {}
    for name, factory, fixed_throttle, notes in _controller_factories(
        scenario, checkpoint_path
    ):
        if factory is None and fixed_throttle is None:
            metrics.append(
                ControllerMetrics(
                    controller=name,
                    final_altitude_m=None,
                    final_vertical_velocity_m_s=None,
                    final_fuel_mass_kg=None,
                    min_altitude_m=None,
                    max_altitude_m=None,
                    flight_time_s=None,
                    landing_status="failed",
                    touchdown_speed_m_s=None,
                    throttle_mean=None,
                    throttle_max=None,
                    throttle_saturation_fraction=None,
                    controller_notes=notes,
                )
            )
            continue
        try:
            controller = factory() if factory else None
            run = run_scenario(
                scenario,
                controller=controller,
                fixed_throttle=fixed_throttle,
                stop_on_ground=True,
                record_final_state=True,
            )
        except (ImportError, OSError, RuntimeError, ValueError) as exc:
            metrics.append(
                ControllerMetrics(
                    controller=name,
                    final_altitude_m=None,
                    final_vertical_velocity_m_s=None,
                    final_fuel_mass_kg=None,
                    min_altitude_m=None,
                    max_altitude_m=None,
                    flight_time_s=None,
                    landing_status="failed",
                    touchdown_speed_m_s=None,
                    throttle_mean=None,
                    throttle_max=None,
                    throttle_saturation_fraction=None,
                    controller_notes=f"{notes} Execution failed: {exc}",
                )
            )
            continue
        controller_metrics, telemetry = _metrics_from_run(name, notes, run)
        metrics.append(controller_metrics)
        trajectories[name] = telemetry
        telemetry.to_csv(trajectory_dir / f"{name}.csv", index=False)

    comparison = pd.DataFrame(asdict(item) for item in metrics)
    comparison.to_csv(output_dir / "controller_comparison.csv", index=False)
    (output_dir / "controller_comparison.json").write_text(
        json.dumps([asdict(item) for item in metrics], indent=2) + "\n",
        encoding="utf-8",
    )

    if generate_plots:
        _save_plots(trajectories, figure_dir, curated_dir)
    if generate_report:
        _save_report(comparison, scenario, curated_dir)
    return comparison


def _save_plots(
    trajectories: dict[str, pd.DataFrame],
    figure_dir: Path,
    curated_dir: Path,
) -> None:
    plots = {
        "altitude": ("altitude_m", "Altitude (m)"),
        "velocity": ("velocity_z_m_s", "Vertical velocity (m/s)"),
        "throttle": ("throttle", "Throttle"),
        "fuel": ("fuel_mass_kg", "Fuel mass (kg)"),
    }
    for plot_name, (column, ylabel) in plots.items():
        figure, axis = plt.subplots(figsize=(9, 5))
        for index, (name, telemetry) in enumerate(trajectories.items()):
            axis.plot(
                telemetry["time_s"],
                telemetry[column],
                label=name,
                color=COLORS[index % len(COLORS)],
                linewidth=1.5,
            )
        axis.set(xlabel="Time (s)", ylabel=ylabel, title=f"Controller {plot_name} comparison")
        axis.legend()
        style_axis(axis)
        output_path = figure_dir / f"controller_{plot_name}_comparison.png"
        save_dark_figure(figure, output_path)
        plt.close(figure)
        shutil.copyfile(output_path, curated_dir / output_path.name)


def _save_report(
    comparison: pd.DataFrame,
    scenario: SimulationScenario,
    curated_dir: Path,
) -> None:
    table_columns = list(ControllerMetrics.__dataclass_fields__)
    table = comparison[table_columns].to_markdown(index=False, floatfmt=".4f")
    report = f"""# Controller Trajectory Comparison

This benchmark compares controller behavior inside the current simplified
vertical simulator. These results are useful for software and control-system
regression testing, but they do not represent high-fidelity aerospace validation.

## Scenario

- Initial altitude: `{scenario.initial_altitude_m:.1f} m`
- Initial vertical velocity: `{scenario.initial_vertical_velocity_m_s:.1f} m/s`
- Time step: `{scenario.dt:.3f} s`
- Maximum simulated time: `{scenario.dt * scenario.max_steps:.1f} s`
- Ground contact stops each trajectory

## Real Benchmark Metrics

{table}

## Comparative Plots

![Altitude comparison](controller_altitude_comparison.png)

![Vertical velocity comparison](controller_velocity_comparison.png)

![Throttle comparison](controller_throttle_comparison.png)

![Fuel comparison](controller_fuel_comparison.png)

## Interpretation

- Fixed throttle is an open-loop baseline.
- Heuristic V1 and V2 are manually designed rule-based controllers.
- PID is a classical feedback baseline with untuned gains.
- Neural control is experimental and supervised. It uses a local checkpoint
  when available; otherwise a deterministic untrained network is explicitly labeled.
- Reinforcement learning is future work and was not executed in this benchmark.
- A `landed` classification only satisfies the simplified simulator threshold.
  It is not evidence of real aerospace landing capability.

## Artifacts

- `outputs/controller_benchmark/controller_comparison.csv`
- `outputs/controller_benchmark/controller_comparison.json`
- `outputs/controller_benchmark/trajectories/<controller_name>.csv`

## Limitations

The simulator omits aerodynamics, rotation, wind, actuator dynamics, sensor
noise, ground-contact interpolation, and real flight data. Metrics therefore
measure behavior only within this deterministic vertical model.
"""
    (curated_dir / "controller_trajectory_comparison.md").write_text(
        report, encoding="utf-8"
    )
