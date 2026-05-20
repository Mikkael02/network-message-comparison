from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_request_response_run_endpoint_can_save_results(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "iterations": 5,
        "transports": ["http"],
        "measurements": [],
    }

    class FakeMetadata:
        def model_dump(self, mode="json"):
            return {
                "run_id": "request_response_20260101_demo",
                "experiment_name": "request_response",
                "saved_at": "2026-01-01T00:00:00+00:00",
                "run_label": "demo",
                "file_path": "results/runs/request_response/demo.json",
            }

    monkeypatch.setattr(
        server_module,
        "run_request_response_experiment",
        lambda config: fake_result,
    )
    monkeypatch.setattr(
        server_module,
        "save_experiment_run",
        lambda experiment_name, results, run_label=None: FakeMetadata(),
    )

    payload = {
        "transports": ["http"],
        "iterations": 5,
        "http_base_url": "http://127.0.0.1:8000",
        "ws_url": "ws://127.0.0.1:8001/ws/process",
        "grpc_address": "127.0.0.1:50051",
        "source": "external_benchmark_client",
        "set_value": 42,
        "get_seed_value": 77,
        "set_resource_prefix": "rr_benchmark_set",
        "get_resource_prefix": "rr_benchmark_get",
    }

    response = client.post(
        "/experiments/request-response/run?save_result=true&run_label=demo",
        json=payload,
    )

    assert response.status_code == 200
    data = response.json()

    assert data["saved_result"]["experiment_name"] == "request_response"
    assert data["saved_result"]["run_label"] == "demo"


def test_recent_experiment_runs_endpoint_returns_list(monkeypatch):
    from app.overhead import server as server_module

    fake_response = {
        "total_count": 2,
        "runs": [
            {
                "run_id": "validation_1",
                "experiment_name": "validation",
                "saved_at": "2026-01-01T00:00:00+00:00",
                "run_label": "first",
                "file_path": "results/runs/validation/validation_1.json",
            },
            {
                "run_id": "validation_2",
                "experiment_name": "validation",
                "saved_at": "2026-01-01T00:01:00+00:00",
                "run_label": "second",
                "file_path": "results/runs/validation/validation_2.json",
            },
        ],
    }

    monkeypatch.setattr(
        server_module,
        "list_saved_runs",
        lambda limit, experiment_name=None: fake_response,
    )

    response = client.get("/experiment-runs/recent?limit=10&experiment_name=validation")

    assert response.status_code == 200
    data = response.json()

    assert data["total_count"] == 2
    assert len(data["runs"]) == 2
    assert data["runs"][0]["experiment_name"] == "validation"