from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from aerospace_sim.control.heuristic_landing_controller_v2 import HeuristicLandingController
from aerospace_sim.core.state import RocketState
from aerospace_sim.core.vector3 import Vector3
from aerospace_sim.environment.landing import evaluate_landing
from aerospace_sim.simulation.basic_simulator import BasicRocketSimulator
from aerospace_sim.vehicle.engine import RocketEngine


RESULTS_DIR = Path("docs/results")


def create_initial_state() -> RocketState:
    return RocketState(
        position=Vector3(0.0, 0.0, 100.0),
        velocity=Vector3(0.0, 0.0, -10.0),
        orientation=Vector3(0.0, 0.0, 0.0),
        angular_velocity=Vector3(0.0, 0.0, 0.0),
        fuel_mass=800.0,
    )


def create_simulator() -> BasicRocketSimulator:
    engine = RocketEngine(
        max_thrust=35000.0,
        fuel_burn_rate=2.5,
    )

    return BasicRocketSimulator(
        engine=engine,
        dry_mass=1200.0,
        dt=0.02,
    )


def run_experiment(max_steps: int = 3000) -> tuple[RocketState, pd.DataFrame]:
    state = create_initial_state()
    simulator = create_simulator()
    controller = HeuristicLandingController()

    rows = []

    for step in range(max_steps):
        throttle = controller.compute_throttle(state)

        rows.append(
            {
                "step": step,
                "time_s": state.time,
                "altitude_m": state.altitude,
                "velocity_z_m_s": state.velocity.z,
                "speed_m_s": state.speed,
                "fuel_mass_kg": state.fuel_mass,
                "throttle": throttle,
            }
        )

        state = simulator.step(state, throttle=throttle)

        if state.altitude <= 0.0:
            break

    return state, pd.DataFrame(rows)


def save_altitude_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(df["time_s"], df["altitude_m"])
    plt.title("Heuristic Controller V2 - Altitude Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Altitude (m)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "heuristic_v2_altitude_over_time.png", dpi=160)
    plt.close()


def save_velocity_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(df["time_s"], df["velocity_z_m_s"])
    plt.title("Heuristic Controller V2 - Vertical Velocity Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Vertical velocity (m/s)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "heuristic_v2_velocity_over_time.png", dpi=160)
    plt.close()


def save_throttle_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(df["time_s"], df["throttle"])
    plt.title("Heuristic Controller V2 - Throttle Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Throttle")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "heuristic_v2_throttle_over_time.png", dpi=160)
    plt.close()


def save_fuel_plot(df: pd.DataFrame) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(df["time_s"], df["fuel_mass_kg"])
    plt.title("Heuristic Controller V2 - Fuel Mass Over Time")
    plt.xlabel("Time (s)")
    plt.ylabel("Fuel mass (kg)")
    plt.tight_layout()
    plt.savefig(RESULTS_DIR / "heuristic_v2_fuel_over_time.png", dpi=160)
    plt.close()


def save_report(evaluation, telemetry: pd.DataFrame) -> None:
    summary = pd.DataFrame(
        [
            {
                "status": evaluation.status.value,
                "final_altitude_m": evaluation.final_altitude_m,
                "final_velocity_z_m_s": evaluation.final_velocity_z_m_s,
                "final_speed_m_s": evaluation.final_speed_m_s,
                "final_time_s": evaluation.final_time_s,
                "final_fuel_mass_kg": evaluation.final_fuel_mass_kg,
            }
        ]
    )

    summary.to_csv(RESULTS_DIR / "heuristic_v2_summary.csv", index=False)

    table = summary.to_markdown(index=False)

    report = f"""# Heuristic Landing Controller V2 Experiment

This experiment evaluates the second heuristic landing controller.

The controller is dynamic: it reads the rocket state at each simulation step and adjusts throttle based on altitude and vertical velocity.

## Final Result

{table}

## Plots

### Altitude Over Time

![Altitude over time](heuristic_v2_altitude_over_time.png)

### Vertical Velocity Over Time

![Vertical velocity over time](heuristic_v2_velocity_over_time.png)

### Throttle Over Time

![Throttle over time](heuristic_v2_throttle_over_time.png)

### Fuel Mass Over Time

![Fuel mass over time](heuristic_v2_fuel_over_time.png)

## Engineering Interpretation

The V2 heuristic controller does not land the rocket.

Instead, it becomes too aggressive and keeps throttle near maximum for too long. This causes a runaway ascent: the rocket keeps accelerating upward and ends the simulation far above the landing zone.

This is an important failed-control result.

It shows that avoiding crash is not enough. A valid landing controller must also regulate ascent, descent rate, and throttle smoothness near the landing zone.

## Next Step

The next engineering step is to move from heuristic control to a more stable controller:

- tune the heuristic controller with softer throttle corrections
- introduce a PID controller
- penalize upward velocity and excessive altitude gain
- eventually train a reinforcement learning policy using the simulator telemetry
"""

    (RESULTS_DIR / "heuristic_v2_report.md").write_text(report, encoding="utf-8")


def main() -> None:
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    final_state, telemetry = run_experiment()
    evaluation = evaluate_landing(final_state)

    telemetry.to_csv(RESULTS_DIR / "heuristic_v2_telemetry.csv", index=False)

    save_altitude_plot(telemetry)
    save_velocity_plot(telemetry)
    save_throttle_plot(telemetry)
    save_fuel_plot(telemetry)
    save_report(evaluation, telemetry)

    print("Heuristic V2 report generated successfully.")
    print(f"Status: {evaluation.status.value}")
    print(f"Final altitude: {evaluation.final_altitude_m:.4f} m")
    print(f"Final vertical velocity: {evaluation.final_velocity_z_m_s:.4f} m/s")
    print(f"Final fuel mass: {evaluation.final_fuel_mass_kg:.4f} kg")


if __name__ == "__main__":
    main()