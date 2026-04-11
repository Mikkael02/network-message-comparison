import pytest
from fastapi.testclient import TestClient

from app.transport_ws.server import app, state_store

client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_state_store():
    state_store.clear()
    yield
    state_store.clear()


def test_ws_health_check_returns_ok():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_ws_set_value_returns_success():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "sensor_01",
            "value": 42,
        },
    }

    with client.websocket_connect("/ws/process") as websocket:
        websocket.send_json(payload)
        data = websocket.receive_json()

    assert data["status"] == "success"
    assert data["operation"] == "set_value"
    assert data["resource_id"] == "sensor_01"
    assert data["result"]["action"] == "value_updated"
    assert data["result"]["stored_value"] == 42
    assert "message_id" in data


def test_ws_get_value_returns_previously_stored_value():
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

    with client.websocket_connect("/ws/process") as websocket:
        websocket.send_json(set_payload)
        set_data = websocket.receive_json()
        assert set_data["status"] == "success"

        websocket.send_json(get_payload)
        get_data = websocket.receive_json()

    assert get_data["status"] == "success"
    assert get_data["operation"] == "get_value"
    assert get_data["resource_id"] == "sensor_01"
    assert get_data["result"]["action"] == "value_returned"
    assert get_data["result"]["current_value"] == 42
    assert "message_id" in get_data


def test_ws_rejects_invalid_structural_payload():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "",
            "value": 42,
        },
    }

    with client.websocket_connect("/ws/process") as websocket:
        websocket.send_json(payload)
        data = websocket.receive_json()

    assert data["status"] == "error"
    assert data["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert isinstance(data["error"]["details"], list)


def test_ws_rejects_invalid_business_payload():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "readonly_sensor",
            "value": 42,
        },
    }

    with client.websocket_connect("/ws/process") as websocket:
        websocket.send_json(payload)
        data = websocket.receive_json()

    assert data["status"] == "error"
    assert data["error"]["code"] == "BUSINESS_VALIDATION_ERROR"
    assert data["error"]["message"] == "Cannot modify resources marked as readonly"
    assert data["error"]["details"] is None


def test_ws_returns_not_found_for_missing_resource():
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "get_value",
            "resource_id": "sensor_missing",
        },
    }

    with client.websocket_connect("/ws/process") as websocket:
        websocket.send_json(payload)
        data = websocket.receive_json()

    assert data["status"] == "error"
    assert data["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert data["error"]["message"] == "Resource 'sensor_missing' was not found"
    assert data["error"]["details"] is None


def test_ws_connection_stays_open_after_error_and_accepts_next_message():
    invalid_payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "",
            "value": 42,
        },
    }

    valid_payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "sensor_01",
            "value": 99,
        },
    }

    with client.websocket_connect("/ws/process") as websocket:
        websocket.send_json(invalid_payload)
        first_response = websocket.receive_json()

        websocket.send_json(valid_payload)
        second_response = websocket.receive_json()

    assert first_response["status"] == "error"
    assert first_response["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"

    assert second_response["status"] == "success"
    assert second_response["result"]["stored_value"] == 99