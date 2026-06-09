# Reproducibility

Run commands from the repository root with Python 3.11 and `uv`.

## Create The Environment

```bash
uv sync
source .venv/bin/activate
```

After editable package installation is validated, scripts should import `aerospace_sim` directly. Until then, the explicit fallback is:

```bash
export PYTHONPATH=src
```

## Run Simulations

```bash
python scripts/run_basic_simulation.py
python scripts/compare_throttle_levels.py
python scripts/run_landing_experiment.py
python scripts/run_heuristic_landing.py
python scripts/run_heuristic_landing_v2.py
```

## Regenerate Reports

These commands intentionally update curated files in `docs/results/`:

```bash
python scripts/generate_throttle_report.py
python scripts/generate_trajectory_report.py
python scripts/generate_landing_report.py
python scripts/generate_heuristic_landing_v2_report.py
```

Review the generated diff before committing results.

## Run Tests

```bash
pytest -q
```

## Results And Outputs

- `docs/results/` contains small, curated, reproducible CSVs, plots, and reports intended for GitHub.
- `outputs/` contains raw telemetry, temporary plots, logs, checkpoints, and other generated artifacts. It is ignored by Git.
- Model checkpoints and local databases are ignored by Git.

The simulations are currently deterministic and do not use randomness. A future stochastic environment must record seeds and configuration snapshots with each experiment.
