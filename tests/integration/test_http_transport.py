import pytest
from fastapi.testclient import TestClient

from app.transport_http.server import app, state_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_state_store():
    state_store.clear()
    yield
    state_store.clear()


def test_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_process_set_value_returns_success():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "sensor_01",
            "value": 42,
        },
    }

    response = client.post("/process", json=payload)

    assert response.status_code == 200

    data = response.json()
    assert data["status"] == "success"
    assert data["operation"] == "set_value"
    assert data["resource_id"] == "sensor_01"
    assert data["result"]["action"] == "value_updated"
    assert data["result"]["stored_value"] == 42
    assert "message_id" in data


def test_process_get_value_returns_previously_stored_value():
    set_payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "sensor_01",
            "value": 42,
        },
    }

    get_payload = {
        "source": "client_1",
        "payload": {
            "operation": "get_value",
            "resource_id": "sensor_01",
        },
    }

    set_response = client.post("/process", json=set_payload)
    assert set_response.status_code == 200

    get_response = client.post("/process", json=get_payload)
    assert get_response.status_code == 200

    data = get_response.json()
    assert data["status"] == "success"
    assert data["operation"] == "get_value"
    assert data["resource_id"] == "sensor_01"
    assert data["result"]["action"] == "value_returned"
    assert data["result"]["current_value"] == 42
    assert "message_id" in data


def test_process_rejects_invalid_structural_payload():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "",
            "value": 42,
        },
    }

    response = client.post("/process", json=payload)

    assert response.status_code == 422

    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert isinstance(data["error"]["details"], list)


def test_process_rejects_invalid_business_payload():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "readonly_sensor",
            "value": 42,
        },
    }

    response = client.post("/process", json=payload)

    assert response.status_code == 422

    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "BUSINESS_VALIDATION_ERROR"
    assert data["error"]["message"] == "Cannot modify resources marked as readonly"
    assert data["error"]["details"] is None


def test_process_returns_404_for_missing_resource():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "get_value",
            "resource_id": "sensor_missing",
        },
    }

    response = client.post("/process", json=payload)

    assert response.status_code == 404

    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Resource 'sensor_missing' was not found"
    assert data["error"]["details"] is None