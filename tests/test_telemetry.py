from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TelemetryRecorder


def test_recorder_produces_consistent_dataframe_schema() -> None:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    recorder = TelemetryRecorder()

    recorder.record(step=0, state=state, throttle=0.5)
    dataframe = recorder.to_dataframe()

    assert list(dataframe.columns) == [
        "step",
        "time_s",
        "altitude_m",
        "position_x_m",
        "position_y_m",
        "velocity_z_m_s",
        "speed_m_s",
        "fuel_mass_kg",
        "throttle",
    ]
    assert dataframe.iloc[0]["altitude_m"] == 100.0
    assert dataframe.iloc[0]["throttle"] == 0.5
