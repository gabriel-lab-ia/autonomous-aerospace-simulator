# Contributing

Contributions should keep the simulator understandable, reproducible, and independently testable.

## Development Setup

```bash
uv sync
source .venv/bin/activate
pytest -q
```

See `docs/reproducibility.md` for experiment and report-generation commands.

## Change Guidelines

- Keep physics, control, telemetry, visualization, and training responsibilities separate.
- Add or update tests when changing physical behavior or landing evaluation.
- Document assumptions, units, and known limitations.
- Keep generated raw outputs in `outputs/`.
- Commit only small, curated, reproducible artifacts to `docs/results/`.
- Review generated result diffs before committing them.
- Do not include secrets, local environments, checkpoints, databases, or editor settings.

## Pull Requests

Describe the engineering motivation, changed behavior, validation commands, and remaining limitations. Prefer focused pull requests with one clear purpose.
