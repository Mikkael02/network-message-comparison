import pytest

from app.experiments.models import (
    ExperimentTransport,
    SerializationExperimentConfig,
    SerializationOperation,
)
from app.experiments.serialization import run_serialization_experiment


def test_run_serialization_experiment_returns_measurements(monkeypatch):
    from app.experiments import serialization as serialization_module

    fake_measurement = {
        "transport": "http",
        "operation": "set_value",
        "encoding": "json",
        "request_size_bytes": 100,
        "response_size_bytes": 80,
        "request_serialize_us": [1.0, 2.0],
        "request_deserialize_us": [0.5, 0.7],
        "response_serialize_us": [1.1, 1.3],
        "response_deserialize_us": [0.6, 0.8],
        "request_serialize_summary": {
            "count": 2,
            "min_us": 1.0,
            "max_us": 2.0,
            "avg_us": 1.5,
            "median_us": 1.5,
        },
        "request_deserialize_summary": {
            "count": 2,
            "min_us": 0.5,
            "max_us": 0.7,
            "avg_us": 0.6,
            "median_us": 0.6,
        },
        "response_serialize_summary": {
            "count": 2,
            "min_us": 1.1,
            "max_us": 1.3,
            "avg_us": 1.2,
            "median_us": 1.2,
        },
        "response_deserialize_summary": {
            "count": 2,
            "min_us": 0.6,
            "max_us": 0.8,
            "avg_us": 0.7,
            "median_us": 0.7,
        },
    }

    monkeypatch.setattr(
        serialization_module,
        "run_single_measurement",
        lambda transport, operation, config: {
            **fake_measurement,
            "transport": transport.value,
            "operation": operation.value,
            "encoding": "json" if transport != ExperimentTransport.GRPC else "protobuf",
        },
    )

    config = SerializationExperimentConfig(
        transports=[ExperimentTransport.HTTP, ExperimentTransport.GRPC],
        operations=[SerializationOperation.SET_VALUE],
        iterations=2,
    )

    result = run_serialization_experiment(config)

    assert result["iterations"] == 2
    assert result["transports"] == ["http", "grpc"]
    assert result["operations"] == ["set_value"]
    assert len(result["measurements"]) == 2


def test_serialization_config_rejects_duplicate_operations():
    with pytest.raises(Exception):
        SerializationExperimentConfig(
            operations=[
                SerializationOperation.SET_VALUE,
                SerializationOperation.SET_VALUE,
            ]
        )