from app.experiments.models import (
    ExperimentTransport,
    RealtimeFetchExperimentConfig,
)
from app.experiments.realtime import run_realtime_fetch_experiment


def test_run_realtime_fetch_experiment_uses_selected_transport_runners(monkeypatch):
    from app.experiments import realtime as realtime_module

    fake_http_result = [
        {
            "transport": "http",
            "scenario": "non_empty_fetch",
            "latencies_ms": [1.0, 2.0],
            "event_counts": [3, 3],
            "summary": {
                "count": 2,
                "min_ms": 1.0,
                "max_ms": 2.0,
                "avg_ms": 1.5,
                "median_ms": 1.5,
            },
            "expected_event_count": 3,
        },
        {
            "transport": "http",
            "scenario": "empty_fetch",
            "latencies_ms": [0.5, 0.7],
            "event_counts": [0, 0],
            "summary": {
                "count": 2,
                "min_ms": 0.5,
                "max_ms": 0.7,
                "avg_ms": 0.6,
                "median_ms": 0.6,
            },
            "expected_event_count": 0,
        },
    ]

    fake_grpc_result = [
        {
            "transport": "grpc",
            "scenario": "non_empty_fetch",
            "latencies_ms": [0.8, 0.9],
            "event_counts": [3, 3],
            "summary": {
                "count": 2,
                "min_ms": 0.8,
                "max_ms": 0.9,
                "avg_ms": 0.85,
                "median_ms": 0.85,
            },
            "expected_event_count": 3,
        },
        {
            "transport": "grpc",
            "scenario": "empty_fetch",
            "latencies_ms": [0.2, 0.3],
            "event_counts": [0, 0],
            "summary": {
                "count": 2,
                "min_ms": 0.2,
                "max_ms": 0.3,
                "avg_ms": 0.25,
                "median_ms": 0.25,
            },
            "expected_event_count": 0,
        },
    ]

    monkeypatch.setattr(
        realtime_module,
        "_run_http_realtime_measurements",
        lambda config: fake_http_result,
    )
    monkeypatch.setattr(
        realtime_module,
        "_run_grpc_realtime_measurements",
        lambda config: fake_grpc_result,
    )

    config = RealtimeFetchExperimentConfig(
        transports=[ExperimentTransport.HTTP, ExperimentTransport.GRPC],
        iterations=2,
    )

    result = run_realtime_fetch_experiment(config)

    assert result["iterations"] == 2
    assert result["transports"] == ["http", "grpc"]
    assert len(result["measurements"]) == 4


def test_realtime_fetch_config_rejects_duplicate_transports():
    try:
        RealtimeFetchExperimentConfig(
            transports=[ExperimentTransport.HTTP, ExperimentTransport.HTTP]
        )
        assert False, "Expected validation error for duplicate transports"
    except Exception:
        assert True