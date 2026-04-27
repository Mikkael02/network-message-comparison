import pytest

from tests.performance.transport_benchmark_clients import (
    GrpcBenchmarkClient,
    HttpBenchmarkClient,
    WsBenchmarkClient,
)


@pytest.fixture(params=["http", "ws", "grpc"])
def transport_client(request):
    if request.param == "http":
        client = HttpBenchmarkClient()
        client.reset()
        yield request.param, client
        client.reset()
        client.close()

    elif request.param == "ws":
        client = WsBenchmarkClient()
        client.reset()
        client.open()
        yield request.param, client
        client.close()
        client.reset()

    elif request.param == "grpc":
        client = GrpcBenchmarkClient()
        client.reset()
        yield request.param, client
        client.close()


def test_set_value_baseline(benchmark, transport_client):
    transport_name, client = transport_client

    payload = {
        "source": "benchmark_client",
        "payload": {
            "operation": "set_value",
            "resource_id": f"{transport_name}_sensor_01",
            "value": 42,
        },
    }

    response = benchmark(client.send, payload)

    assert response["status"] == "success"
    assert response["operation"] == "set_value"
    assert response["result"]["action"] == "value_updated"
    assert response["result"]["stored_value"] == 42


def test_get_value_baseline(benchmark, transport_client):
    transport_name, client = transport_client

    set_payload = {
        "source": "benchmark_client",
        "payload": {
            "operation": "set_value",
            "resource_id": f"{transport_name}_sensor_02",
            "value": 77,
        },
    }

    get_payload = {
        "source": "benchmark_client",
        "payload": {
            "operation": "get_value",
            "resource_id": f"{transport_name}_sensor_02",
        },
    }

    set_response = client.send(set_payload)
    assert set_response["status"] == "success"

    response = benchmark(client.send, get_payload)

    assert response["status"] == "success"
    assert response["operation"] == "get_value"
    assert response["result"]["action"] == "value_returned"
    assert response["result"]["current_value"] == 77