import json

import grpc
import pytest

from app.core.services.state_store import InMemoryStateStore
from app.shared.error_codes import ErrorCode
from app.transport_grpc.generated import (
    message_service_pb2,
    message_service_pb2_grpc,
)
from app.transport_grpc.server import create_server


@pytest.fixture()
def grpc_test_context():
    state_store = InMemoryStateStore()
    server = create_server(state_store)

    port = server.add_insecure_port("127.0.0.1:0")
    server.start()

    channel = grpc.insecure_channel(f"127.0.0.1:{port}")
    grpc.channel_ready_future(channel).result(timeout=5)
    stub = message_service_pb2_grpc.MessageServiceStub(channel)

    yield {
        "state_store": state_store,
        "server": server,
        "channel": channel,
        "stub": stub,
    }

    channel.close()
    server.stop(None)


def build_set_value_request(resource_id: str, value: int):
    return message_service_pb2.MessageEnvelope(
        source="client_1",
        payload=message_service_pb2.MessagePayload(
            operation=message_service_pb2.SET_VALUE,
            resource_id=resource_id,
            value=value,
        ),
    )


def build_get_value_request(resource_id: str):
    return message_service_pb2.MessageEnvelope(
        source="client_1",
        payload=message_service_pb2.MessagePayload(
            operation=message_service_pb2.GET_VALUE,
            resource_id=resource_id,
        ),
    )


def test_grpc_set_value_returns_success(grpc_test_context):
    stub = grpc_test_context["stub"]

    response = stub.Process(build_set_value_request("sensor_01", 42))

    assert response.WhichOneof("outcome") == "success"
    assert response.success.status == "success"
    assert response.success.operation == "set_value"
    assert response.success.resource_id == "sensor_01"
    assert response.success.WhichOneof("result") == "update_result"
    assert response.success.update_result.action == "value_updated"
    assert response.success.update_result.stored_value == 42
    assert response.success.message_id


def test_grpc_get_value_returns_previously_stored_value(grpc_test_context):
    stub = grpc_test_context["stub"]

    set_response = stub.Process(build_set_value_request("sensor_01", 42))
    assert set_response.WhichOneof("outcome") == "success"

    get_response = stub.Process(build_get_value_request("sensor_01"))

    assert get_response.WhichOneof("outcome") == "success"
    assert get_response.success.status == "success"
    assert get_response.success.operation == "get_value"
    assert get_response.success.resource_id == "sensor_01"
    assert get_response.success.WhichOneof("result") == "get_result"
    assert get_response.success.get_result.action == "value_returned"
    assert get_response.success.get_result.current_value == 42
    assert get_response.success.message_id


def test_grpc_rejects_invalid_structural_payload(grpc_test_context):
    stub = grpc_test_context["stub"]

    request = message_service_pb2.MessageEnvelope(
        source="client_1",
        payload=message_service_pb2.MessagePayload(
            operation=message_service_pb2.SET_VALUE,
            resource_id="",
            value=42,
        ),
    )

    response = stub.Process(request)

    assert response.WhichOneof("outcome") == "error"
    assert response.error.status == "error"
    assert response.error.code == ErrorCode.STRUCTURAL_VALIDATION_ERROR.value
    assert response.error.message == "Request validation failed"

    details = json.loads(response.error.details_json)
    assert isinstance(details, list)


def test_grpc_rejects_invalid_business_payload(grpc_test_context):
    stub = grpc_test_context["stub"]

    response = stub.Process(build_set_value_request("readonly_sensor", 42))

    assert response.WhichOneof("outcome") == "error"
    assert response.error.status == "error"
    assert response.error.code == ErrorCode.BUSINESS_VALIDATION_ERROR.value
    assert response.error.message == "Cannot modify resources marked as readonly"
    assert response.error.details_json == ""


def test_grpc_returns_not_found_for_missing_resource(grpc_test_context):
    stub = grpc_test_context["stub"]

    response = stub.Process(build_get_value_request("sensor_missing"))

    assert response.WhichOneof("outcome") == "error"
    assert response.error.status == "error"
    assert response.error.code == ErrorCode.RESOURCE_NOT_FOUND.value
    assert response.error.message == "Resource 'sensor_missing' was not found"
    assert response.error.details_json == ""