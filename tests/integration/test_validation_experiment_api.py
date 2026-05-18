from fastapi.testclient import TestClient

from app.overhead.server import app


client = TestClient(app)


def test_validation_default_config_endpoint_returns_defaults():
    response = client.get("/experiments/validation/default-config")

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 5000
    assert "baseline_valid_dict" in data["scenarios"]
    assert "business_validation_invalid" in data["scenarios"]


def test_validation_run_endpoint_uses_runner(monkeypatch):
    from app.overhead import server as server_module

    fake_result = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "iterations": 5,
        "scenarios": ["baseline_valid_dict"],
        "measurements": [
            {
                "scenario": "baseline_valid_dict",
                "expected_outcome": "success",
                "timings_us": [1, 2, 3, 4, 5],
                "summary": {
                    "count": 5,
                    "min_us": 1,
                    "max_us": 5,
                    "avg_us": 3,
                    "median_us": 3,
                },
            }
        ],
    }

    def fake_runner(config):
        return fake_result

    monkeypatch.setattr(server_module, "run_validation_experiment", fake_runner)

    payload = {
        "scenarios": ["baseline_valid_dict"],
        "iterations": 5,
        "source": "validation_benchmark_client",
        "valid_resource_id": "validation_valid_set",
        "readonly_resource_id": "readonly_validation_target",
        "valid_value": 42,
    }

    response = client.post("/experiments/validation/run", json=payload)

    assert response.status_code == 200
    data = response.json()

    assert data["iterations"] == 5
    assert data["scenarios"] == ["baseline_valid_dict"]
    assert len(data["measurements"]) == 1