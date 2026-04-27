import pytest
from fastapi.testclient import TestClient

from app.transport_ws.server import app, state_store


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_state_store():
    state_store.clear()
    yield
    state_store.clear()


def test_ws_changes_returns_empty_batch_for_fresh_state():
    with client.websocket_connect("/ws/changes") as websocket:
        websocket.send_json({"from_version": 0})
        data = websocket.receive_json()

    assert data["status"] == "success"
    assert data["batch"]["from_version"] == 0
    assert data["batch"]["current_version"] == 0
    assert data["batch"]["events"] == []


def test_ws_changes_returns_only_newer_events():
    state_store.set_value("sensor_01", 10)
    state_store.set_value("sensor_02", 20)
    state_store.set_value("sensor_01", 15)

    with client.websocket_connect("/ws/changes") as websocket:
        websocket.send_json({"from_version": 1})
        data = websocket.receive_json()

    assert data["status"] == "success"
    assert data["batch"]["from_version"] == 1
    assert data["batch"]["current_version"] == 3
    assert len(data["batch"]["events"]) == 2

    assert data["batch"]["events"][0]["version"] == 2
    assert data["batch"]["events"][0]["resource_id"] == "sensor_02"
    assert data["batch"]["events"][0]["value"] == 20

    assert data["batch"]["events"][1]["version"] == 3
    assert data["batch"]["events"][1]["resource_id"] == "sensor_01"
    assert data["batch"]["events"][1]["value"] == 15


def test_ws_changes_returns_empty_batch_when_client_is_up_to_date():
    state_store.set_value("sensor_01", 10)

    with client.websocket_connect("/ws/changes") as websocket:
        websocket.send_json({"from_version": 1})
        data = websocket.receive_json()

    assert data["status"] == "success"
    assert data["batch"]["from_version"] == 1
    assert data["batch"]["current_version"] == 1
    assert data["batch"]["events"] == []


def test_ws_changes_rejects_negative_version():
    with client.websocket_connect("/ws/changes") as websocket:
        websocket.send_json({"from_version": -1})
        data = websocket.receive_json()

    assert data["status"] == "error"
    assert data["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"
    assert data["error"]["message"] == "Request validation failed"
    assert isinstance(data["error"]["details"], list)


def test_ws_changes_connection_stays_open_after_error():
    with client.websocket_connect("/ws/changes") as websocket:
        websocket.send_json({"from_version": -1})
        first_response = websocket.receive_json()

        websocket.send_json({"from_version": 0})
        second_response = websocket.receive_json()

    assert first_response["status"] == "error"
    assert first_response["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"

    assert second_response["status"] == "success"
    assert second_response["batch"]["from_version"] == 0