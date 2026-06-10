import json
from pathlib import Path

from aerospace_sim.evaluation.controller_benchmark import run_controller_benchmark
from aerospace_sim.simulation.scenario import SimulationScenario


def test_benchmark_generates_comparison_and_report(tmp_path: Path) -> None:
    output_dir = tmp_path / "outputs"
    curated_dir = tmp_path / "docs"
    scenario = SimulationScenario.from_yaml().with_overrides(max_steps=20)

    comparison = run_controller_benchmark(
        scenario=scenario,
        output_dir=output_dir,
        curated_dir=curated_dir,
        checkpoint_path=tmp_path / "missing.pt",
        generate_plots=False,
    )

    assert (output_dir / "controller_comparison.csv").exists()
    assert (output_dir / "controller_comparison.json").exists()
    assert (curated_dir / "controller_trajectory_comparison.md").exists()
    assert "pid" in comparison["controller"].values
    assert json.loads((output_dir / "controller_comparison.json").read_text())


def test_controller_comparison_document_marks_pid_implemented() -> None:
    comparison = Path("docs/results/controller_comparison.md").read_text()

    assert "| PID | Implemented | Yes | No | Yes |" in comparison
