from pathlib import Path

from app.experiments.models import (
    ExperimentTransport,
    RequestResponseExperimentConfig,
)
from app.experiments.request_response import (
    run_request_response_experiment,
    save_request_response_experiment_results,
)


class FakeClient:
    def __init__(self) -> None:
        self.closed = False

    def send(self, payload: dict) -> dict:
        operation = payload["payload"]["operation"]
        resource_id = payload["payload"]["resource_id"]

        if operation == "set_value":
            return {
                "status": "success",
                "message_id": "fake-message-id",
                "operation": "set_value",
                "resource_id": resource_id,
                "result": {
                    "action": "value_updated",
                    "stored_value": payload["payload"]["value"],
                },
            }

        return {
            "status": "success",
            "message_id": "fake-message-id",
            "operation": "get_value",
            "resource_id": resource_id,
            "result": {
                "action": "value_returned",
                "current_value": 77,
            },
        }

    def close(self) -> None:
        self.closed = True


def test_run_request_response_experiment_returns_measurements(monkeypatch):
    from app.experiments import request_response as rr_module

    monkeypatch.setitem(
        rr_module.CLIENT_FACTORIES,
        ExperimentTransport.HTTP,
        lambda config: FakeClient(),
    )
    monkeypatch.setitem(
        rr_module.CLIENT_FACTORIES,
        ExperimentTransport.WS,
        lambda config: FakeClient(),
    )

    config = RequestResponseExperimentConfig(
        transports=[ExperimentTransport.HTTP, ExperimentTransport.WS],
        iterations=3,
    )

    result = run_request_response_experiment(config)

    assert result["iterations"] == 3
    assert result["transports"] == ["http", "ws"]
    assert len(result["measurements"]) == 2

    for measurement in result["measurements"]:
        assert measurement["set_value"]["summary"]["count"] == 3
        assert measurement["get_value"]["summary"]["count"] == 3


def test_save_request_response_experiment_results_writes_file(tmp_path: Path):
    results = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "iterations": 1,
        "transports": ["http"],
        "measurements": [],
    }

    output_path = tmp_path / "request_response.json"
    save_request_response_experiment_results(results, output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8")