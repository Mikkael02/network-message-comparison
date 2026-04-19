import pytest

from tests.scenarios.transport_clients import (
    GrpcTransportClient,
    HttpTransportClient,
    WsTransportClient,
)


@pytest.fixture(params=["http", "ws", "grpc"])
def transport_client(request):
    if request.param == "http":
        client = HttpTransportClient()
        client.reset()
        yield client
        client.reset()

    elif request.param == "ws":
        client = WsTransportClient()
        client.reset()
        yield client
        client.reset()

    elif request.param == "grpc":
        client = GrpcTransportClient()
        client.reset()
        yield client
        client.close()


def test_set_value_succeeds_for_all_transports(transport_client):
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "sensor_01",
            "value": 42,
        },
    }

    response = transport_client.send(payload)

    assert response["status"] == "success"
    assert response["operation"] == "set_value"
    assert response["resource_id"] == "sensor_01"
    assert response["result"]["action"] == "value_updated"
    assert response["result"]["stored_value"] == 42
    assert "message_id" in response


def test_get_value_returns_previously_stored_value_for_all_transports(transport_client):
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

    set_response = transport_client.send(set_payload)
    assert set_response["status"] == "success"

    get_response = transport_client.send(get_payload)

    assert get_response["status"] == "success"
    assert get_response["operation"] == "get_value"
    assert get_response["resource_id"] == "sensor_01"
    assert get_response["result"]["action"] == "value_returned"
    assert get_response["result"]["current_value"] == 42


def test_structural_validation_error_is_reported_for_all_transports(transport_client):
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "",
            "value": 42,
        },
    }

    response = transport_client.send(payload)

    assert response["status"] == "error"
    assert response["error"]["code"] == "STRUCTURAL_VALIDATION_ERROR"
    assert response["error"]["message"] == "Request validation failed"
    assert response["error"]["details"] is not None


def test_business_validation_error_is_reported_for_all_transports(transport_client):
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "set_value",
            "resource_id": "readonly_sensor",
            "value": 42,
        },
    }

    response = transport_client.send(payload)

    assert response["status"] == "error"
    assert response["error"]["code"] == "BUSINESS_VALIDATION_ERROR"
    assert response["error"]["message"] == "Cannot modify resources marked as readonly"


def test_missing_resource_is_reported_for_all_transports(transport_client):
    payload = {
        "source": "client_1",
        "payload": {
            "operation": "get_value",
            "resource_id": "sensor_missing",
        },
    }

    response = transport_client.send(payload)

    assert response["status"] == "error"
    assert response["error"]["code"] == "RESOURCE_NOT_FOUND"
    assert response["error"]["message"] == "Resource 'sensor_missing' was not found"