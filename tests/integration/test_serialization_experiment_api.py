from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_serialization_default_config_endpoint_returns_defaults():
    response = client.get("/experiments/serialization/default-config")

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 2000
    assert data["transports"] == ["http", "ws", "grpc"]
    assert data["operations"] == ["set_value", "get_value"]


def test_serialization_run_endpoint_uses_runner(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "iterations": 5,
        "transports": ["http"],
        "operations": ["set_value"],
        "measurements": [
            {
                "transport": "http",
                "operation": "set_value",
                "encoding": "json",
                "request_size_bytes": 100,
                "response_size_bytes": 80,
                "request_serialize_us": [1, 2, 3],
                "request_deserialize_us": [1, 1, 1],
                "response_serialize_us": [1, 2, 3],
                "response_deserialize_us": [1, 1, 1],
                "request_serialize_summary": {
                    "count": 3,
                    "min_us": 1,
                    "max_us": 3,
                    "avg_us": 2,
                    "median_us": 2,
                },
                "request_deserialize_summary": {
                    "count": 3,
                    "min_us": 1,
                    "max_us": 1,
                    "avg_us": 1,
                    "median_us": 1,
                },
                "response_serialize_summary": {
                    "count": 3,
                    "min_us": 1,
                    "max_us": 3,
                    "avg_us": 2,
                    "median_us": 2,
                },
                "response_deserialize_summary": {
                    "count": 3,
                    "min_us": 1,
                    "max_us": 1,
                    "avg_us": 1,
                    "median_us": 1,
                },
            }
        ],
    }

    def fake_runner(config):
        return fake_result

    monkeypatch.setattr(server_module, "run_serialization_experiment", fake_runner)

    payload = {
        "transports": ["http"],
        "operations": ["set_value"],
        "iterations": 5,
        "http_base_url": "http://127.0.0.1:8000",
        "ws_url": "ws://127.0.0.1:8001/ws/process",
        "grpc_address": "127.0.0.1:50051",
        "source": "serialization_benchmark_client",
        "set_value": 42,
        "get_seed_value": 77,
        "set_resource_prefix": "serialization_set",
        "get_resource_prefix": "serialization_get",
    }

    response = client.post("/experiments/serialization/run", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 5
    assert data["transports"] == ["http"]
    assert data["operations"] == ["set_value"]
    assert len(data["measurements"]) == 1