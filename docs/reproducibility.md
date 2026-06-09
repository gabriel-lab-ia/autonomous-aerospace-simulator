# Reproducibility

Run commands from the repository root with Python 3.11 and `uv`.

## Create The Environment

```bash
uv sync
```

The package is installed editable by `uv sync`, so commands can run through
`uv run` without activating the environment. Optional future-facing groups are
installed only when needed:

```bash
uv sync --group notebooks
uv sync --group ml
```

The explicit fallback for a manually managed environment is:

```bash
export PYTHONPATH=src
```

## Run Simulations

```bash
uv run python scripts/run_basic_simulation.py
uv run python scripts/compare_throttle_levels.py
uv run python scripts/run_landing_experiment.py
uv run python scripts/run_heuristic_landing.py
uv run python scripts/run_heuristic_landing_v2.py
```

## Regenerate Reports

These commands intentionally update curated files in `docs/results/`:

```bash
uv run python scripts/generate_throttle_report.py
uv run python scripts/generate_trajectory_report.py
uv run python scripts/generate_landing_report.py
uv run python scripts/generate_heuristic_landing_v2_report.py
uv run python scripts/generate_numerical_validation_report.py
```

Review the generated diff before committing results.

## Run Tests

```bash
uv run pytest -q
```

GitHub Actions runs the same locked test command for every push and pull request
to `main`.

## Results And Outputs

- `docs/results/` contains small, curated, reproducible CSVs, plots, and reports intended for GitHub.
- `outputs/` contains raw telemetry, temporary plots, logs, checkpoints, and other generated artifacts. It is ignored by Git.
- Model checkpoints and local databases are ignored by Git.

The simulations are currently deterministic and do not use randomness. A future stochastic environment must record seeds and configuration snapshots with each experiment.
