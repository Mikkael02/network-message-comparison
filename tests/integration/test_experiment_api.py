from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_request_response_default_config_endpoint_returns_defaults():
    response = client.get("/experiments/request-response/default-config")

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 50
    assert data["transports"] == ["http", "ws", "grpc"]


def test_request_response_run_endpoint_uses_runner(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "iterations": 5,
        "transports": ["http"],
        "measurements": [
            {
                "transport": "http",
                "iterations": 5,
                "set_value": {
                    "latencies_ms": [1, 2, 3, 4, 5],
                    "summary": {
                        "count": 5,
                        "min_ms": 1,
                        "max_ms": 5,
                        "avg_ms": 3,
                        "median_ms": 3,
                    },
                },
                "get_value": {
                    "latencies_ms": [1, 1, 1, 1, 1],
                    "summary": {
                        "count": 5,
                        "min_ms": 1,
                        "max_ms": 1,
                        "avg_ms": 1,
                        "median_ms": 1,
                    },
                },
            }
        ],
    }

    def fake_runner(config):
        return fake_result

    monkeypatch.setattr(server_module, "run_request_response_experiment", fake_runner)

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

    response = client.post("/experiments/request-response/run", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 5
    assert data["transports"] == ["http"]
    assert len(data["measurements"]) == 1