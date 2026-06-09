from aerospace_sim.simulation.scenario import SimulationScenario
from aerospace_sim.telemetry.recorder import TELEMETRY_COLUMNS, TelemetryRecorder


def test_recorder_produces_consistent_dataframe_schema() -> None:
    scenario = SimulationScenario.from_yaml()
    state = scenario.create_initial_state()
    recorder = TelemetryRecorder()

    recorder.record(step=0, state=state, throttle=0.5)
    dataframe = recorder.to_dataframe()

    assert list(dataframe.columns) == list(TELEMETRY_COLUMNS)
    assert dataframe.iloc[0]["altitude_m"] == 100.0
    assert dataframe.iloc[0]["throttle"] == 0.5


def test_empty_recorder_preserves_schema_and_length() -> None:
    recorder = TelemetryRecorder()

    assert len(recorder) == 0
    assert recorder.records == ()
    assert list(recorder.to_dataframe().columns) == list(TELEMETRY_COLUMNS)
