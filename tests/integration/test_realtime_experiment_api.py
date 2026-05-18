from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_realtime_default_config_endpoint_returns_defaults():
    response = client.get("/experiments/realtime/default-config")

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 50
    assert data["transports"] == ["http", "ws", "grpc"]
    assert data["resource_prefix"] == "realtime_benchmark"


def test_realtime_run_endpoint_uses_runner(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "iterations": 5,
        "transports": ["http"],
        "measurements": [
            {
                "transport": "http",
                "scenario": "non_empty_fetch",
                "latencies_ms": [1, 2, 3, 4, 5],
                "event_counts": [3, 3, 3, 3, 3],
                "summary": {
                    "count": 5,
                    "min_ms": 1,
                    "max_ms": 5,
                    "avg_ms": 3,
                    "median_ms": 3,
                },
                "expected_event_count": 3,
            },
            {
                "transport": "http",
                "scenario": "empty_fetch",
                "latencies_ms": [1, 1, 1, 1, 1],
                "event_counts": [0, 0, 0, 0, 0],
                "summary": {
                    "count": 5,
                    "min_ms": 1,
                    "max_ms": 1,
                    "avg_ms": 1,
                    "median_ms": 1,
                },
                "expected_event_count": 0,
            },
        ],
    }

    def fake_runner(config):
        return fake_result

    monkeypatch.setattr(server_module, "run_realtime_fetch_experiment", fake_runner)

    payload = {
        "transports": ["http"],
        "iterations": 5,
        "http_base_url": "http://127.0.0.1:8000",
        "ws_changes_url": "ws://127.0.0.1:8001/ws/changes",
        "ws_process_url": "ws://127.0.0.1:8001/ws/process",
        "grpc_address": "127.0.0.1:50051",
        "resource_prefix": "realtime_benchmark",
        "first_value": 10,
        "second_value": 20,
        "third_value": 15,
    }

    response = client.post("/experiments/realtime/run", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 5
    assert data["transports"] == ["http"]
    assert len(data["measurements"]) == 2