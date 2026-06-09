# Secure API And SQL Telemetry Layer

## Overview

The FastAPI service exposes deterministic simulator execution through validated
HTTP endpoints and stores simulation metadata plus telemetry in SQL.

```mermaid
flowchart LR
    CLIENT[API Client] --> AUTH[X-API-Key Authentication]
    AUTH --> ROUTES[FastAPI Routes]
    ROUTES --> EXEC[Simulation Execution Service]
    EXEC --> PHYS[Existing Physics and Controllers]
    EXEC --> CRUD[SQLAlchemy CRUD]
    CRUD --> DB[(SQLite or PostgreSQL)]
```

The API reuses the existing simulator modules. HTTP routes do not reimplement
physics, and existing command-line scripts continue to operate independently.

## Environment Variables

Copy `.env.example` to a local `.env` and replace the development key:

```env
AEROSPACE_API_KEY=change-me-local-dev-key
DATABASE_URL=sqlite:///./data/aerospace_sim.db
```

- `AEROSPACE_API_KEY` is required for simulation and telemetry endpoints.
- `DATABASE_URL` defaults to `sqlite:///./data/aerospace_sim.db`.
- `.env`, `data/`, and database files are ignored by Git.
- Never use the example API key in a deployed environment.

## Run Locally

```bash
uv sync --group dev
cp .env.example .env
uv run python scripts/run_api.py
```

The application initializes database tables during startup. SQLite creates the
local `data/` directory automatically.

Interactive OpenAPI documentation is available at:

```text
http://127.0.0.1:8000/docs
```

## Authentication

`GET /health` is public. All `/simulations` and `/telemetry` endpoints require:

```text
X-API-Key: <AEROSPACE_API_KEY>
```

Missing keys return `401`, invalid keys return `403`, and a server without
`AEROSPACE_API_KEY` configured returns `503`. Keys are never returned or logged
by application code.

## API Examples

Public health check:

```bash
curl http://127.0.0.1:8000/health
```

Basic fixed-step simulation:

```bash
curl -X POST http://127.0.0.1:8000/simulations/basic \
  -H "X-API-Key: change-me-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{
    "initial_altitude_m": 100.0,
    "initial_vertical_velocity_m_s": -10.0,
    "initial_fuel_mass_kg": 800.0,
    "throttle": 0.5,
    "steps": 100,
    "dt": 0.02
  }'
```

Fixed-throttle landing:

```bash
curl -X POST http://127.0.0.1:8000/simulations/landing \
  -H "X-API-Key: change-me-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"throttle": 0.5, "max_steps": 3000, "dt": 0.02}'
```

Heuristic closed-loop landing:

```bash
curl -X POST http://127.0.0.1:8000/simulations/heuristic-landing \
  -H "X-API-Key: change-me-local-dev-key" \
  -H "Content-Type: application/json" \
  -d '{"max_steps": 3000, "dt": 0.02}'
```

List recent simulations:

```bash
curl "http://127.0.0.1:8000/simulations?limit=20&simulation_type=landing" \
  -H "X-API-Key: change-me-local-dev-key"
```

Get one simulation:

```bash
curl http://127.0.0.1:8000/simulations/1 \
  -H "X-API-Key: change-me-local-dev-key"
```

Get paginated telemetry:

```bash
curl "http://127.0.0.1:8000/telemetry/1?limit=1000&offset=0" \
  -H "X-API-Key: change-me-local-dev-key"
```

## Persistence Design

The `simulations` table stores experiment identity, parameters, outcome, final
state, timestamps, and extensible JSON metadata. The `telemetry_points` table
stores time-series measurements with a foreign key to its simulation.

Deleting a simulation cascades to its telemetry through both the ORM
relationship and database foreign key. SQLite foreign keys are enabled for each
connection.

SQLite is appropriate for deterministic local development. The SQLAlchemy
models, sessions, JSON column, and `DATABASE_URL` configuration keep the design
ready for PostgreSQL when concurrent writes, larger telemetry volumes, or
centralized experiment tracking become necessary.

To use PostgreSQL, install the optional driver group and provide a PostgreSQL
connection URL:

```bash
uv sync --group dev --group postgres
export DATABASE_URL='postgresql+psycopg://user:password@localhost/aerospace_sim'
uv run python scripts/run_api.py
```

Persisted telemetry supports MLOps use cases such as controller comparison,
dataset creation, regression analysis, experiment lineage, and later model
evaluation dashboards.

## Validation And Tests

```bash
uv run pytest -q
```

API integration tests use a temporary SQLite database and verify public health,
API key enforcement, request validation, simulation persistence, telemetry
queries, and missing-resource responses.
