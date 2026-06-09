# Configuration And Telemetry Contracts

This document defines the reusable contracts that simulation scripts, API
routes, reports, and future controllers share.

## Active Scenario Configuration

`SimulationScenario.from_yaml()` reads the currently implemented vertical
simulation parameters from `configs/default.yaml`:

- timestep and maximum steps
- initial altitude and vertical velocity
- dry mass and fuel mass
- maximum thrust and fuel burn rate

`SimulationScenario.with_overrides()` derives a validated scenario without
repeating defaults or mutating the source configuration. API requests use this
method to override initial conditions and execution limits. Every persisted API
execution stores the resolved scenario snapshot in its SQL metadata.

The YAML file also reserves environment and training sections for future work.
Wind, landing-pad geometry, gimbal, seeds, and training values are not yet
consumed by the current vertical simulator.

## Shared Simulation Runner

`aerospace_sim.simulation.runner.run_scenario()` is the common execution
contract for scripts and API services. It accepts exactly one throttle source:

- `fixed_throttle` for open-loop experiments
- a controller implementing `compute_throttle(state)` for closed-loop control

The runner owns simulator construction, step limits, optional ground-contact
termination, and telemetry recording. A future `PIDLandingController` can
implement the same minimal controller protocol without changing experiment
or telemetry infrastructure.

## Telemetry Schema

`TelemetryRecorder` emits a stable ordered schema through `TELEMETRY_COLUMNS`:

| Column | Meaning |
|---|---|
| `step` | Discrete integration step |
| `time_s` | Simulation time |
| `altitude_m` | Vertical position |
| `position_x_m`, `position_y_m` | Reserved lateral position |
| `velocity_z_m_s` | Vertical velocity |
| `speed_m_s` | Velocity-vector norm |
| `fuel_mass_kg` | Remaining fuel |
| `throttle` | Command applied for the recorded step |

The same telemetry records feed pandas reports, curated CSVs, plots, API
responses, and SQL persistence.
