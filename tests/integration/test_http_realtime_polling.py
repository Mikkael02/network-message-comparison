import pytest
from fastapi.testclient import TestClient

from app.transport_http.server import app, state_store


client = TestClient(app)


@pytest.fixture(autouse=True)
def clear_state_store():
    state_store.clear()
    yield
    state_store.clear()


def test_get_changes_returns_empty_batch_for_fresh_state():
    response = client.get("/changes", params={"from_version": 0})

    assert response.status_code == 200

    data = response.json()
    assert data["from_version"] == 0
    assert data["current_version"] == 0
    assert data["events"] == []


def test_get_changes_returns_newer_events_only():
    client.post(
        "/process",
        json={
            "source": "client_1",
            "payload": {
                "operation": "set_value",
                "resource_id": "sensor_01",
                "value": 10,
            },
        },
    )
    client.post(
        "/process",
        json={
            "source": "client_1",
            "payload": {
                "operation": "set_value",
                "resource_id": "sensor_02",
                "value": 20,
            },
        },
    )
    client.post(
        "/process",
        json={
            "source": "client_1",
            "payload": {
                "operation": "set_value",
                "resource_id": "sensor_01",
                "value": 15,
            },
        },
    )

    response = client.get("/changes", params={"from_version": 1})

    assert response.status_code == 200

    data = response.json()
    assert data["from_version"] == 1
    assert data["current_version"] == 3
    assert len(data["events"]) == 2

    assert data["events"][0]["version"] == 2
    assert data["events"][0]["resource_id"] == "sensor_02"
    assert data["events"][0]["value"] == 20

    assert data["events"][1]["version"] == 3
    assert data["events"][1]["resource_id"] == "sensor_01"
    assert data["events"][1]["value"] == 15


def test_get_changes_returns_empty_batch_when_client_is_up_to_date():
    client.post(
        "/process",
        json={
            "source": "client_1",
            "payload": {
                "operation": "set_value",
                "resource_id": "sensor_01",
                "value": 10,
            },
        },
    )

    response = client.get("/changes", params={"from_version": 1})

    assert response.status_code == 200

    data = response.json()
    assert data["from_version"] == 1
    assert data["current_version"] == 1
    assert data["events"] == []


def test_get_changes_rejects_negative_from_version():
    response = client.get("/changes", params={"from_version": -1})

    assert response.status_code == 422

    data = response.json()
    assert data["status"] == "error"
    assert data["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"


def test_seed_changes_endpoint_populates_demo_events():
    response = client.post("/changes/seed")

    assert response.status_code == 200

    data = response.json()
    assert data["from_version"] == 0
    assert data["current_version"] == 3
    assert len(data["events"]) == 3

    assert data["events"][0]["version"] == 1
    assert data["events"][1]["version"] == 2
    assert data["events"][2]["version"] == 3