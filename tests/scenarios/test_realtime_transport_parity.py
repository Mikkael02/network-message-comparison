import pytest

from tests.scenarios.realtime_transport_clients import (
    GrpcRealtimeClient,
    HttpRealtimeClient,
    WsRealtimeClient,
)


@pytest.fixture(params=["http", "ws", "grpc"])
def realtime_client(request):
    if request.param == "http":
        client = HttpRealtimeClient()
        client.reset()
        yield client
        client.reset()

    elif request.param == "ws":
        client = WsRealtimeClient()
        client.reset()
        yield client
        client.reset()

    elif request.param == "grpc":
        client = GrpcRealtimeClient()
        client.reset()
        yield client
        client.close()


def test_realtime_returns_empty_batch_for_fresh_state(realtime_client):
    response = realtime_client.get_changes(0)

    assert response["from_version"] == 0
    assert response["current_version"] == 0
    assert response["events"] == []


def test_realtime_returns_only_newer_events(realtime_client):
    realtime_client.seed()

    response = realtime_client.get_changes(1)

    assert response["from_version"] == 1
    assert response["current_version"] == 3
    assert len(response["events"]) == 2

    assert response["events"][0]["version"] == 2
    assert response["events"][0]["resource_id"] == "sensor_02"
    assert response["events"][0]["value"] == 20

    assert response["events"][1]["version"] == 3
    assert response["events"][1]["resource_id"] == "sensor_01"
    assert response["events"][1]["value"] == 15


def test_realtime_returns_empty_batch_when_client_is_up_to_date(realtime_client):
    realtime_client.seed()

    response = realtime_client.get_changes(3)

    assert response["from_version"] == 3
    assert response["current_version"] == 3
    assert response["events"] == []