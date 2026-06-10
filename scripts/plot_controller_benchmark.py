"""Regenerate the complete benchmark, including comparative plots."""

from aerospace_sim.evaluation.controller_benchmark import run_controller_benchmark


if __name__ == "__main__":
    run_controller_benchmark(generate_plots=True, generate_report=True)
