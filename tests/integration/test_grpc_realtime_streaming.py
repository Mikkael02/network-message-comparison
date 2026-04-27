import grpc
import pytest

from app.core.services.state_store import InMemoryStateStore
from app.transport_grpc.generated import (
    message_service_pb2,
    message_service_pb2_grpc,
)
from app.transport_grpc.server import create_server


@pytest.fixture()
def grpc_realtime_context():
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


def test_grpc_stream_changes_returns_empty_batch_for_fresh_state(grpc_realtime_context):
    stub = grpc_realtime_context["stub"]

    responses = list(
        stub.StreamChanges(
            message_service_pb2.StateChangeRequest(from_version=0)
        )
    )

    assert len(responses) == 1
    batch = responses[0]

    assert batch.from_version == 0
    assert batch.current_version == 0
    assert list(batch.events) == []


def test_grpc_stream_changes_returns_only_newer_events(grpc_realtime_context):
    store = grpc_realtime_context["state_store"]
    stub = grpc_realtime_context["stub"]

    store.set_value("sensor_01", 10)
    store.set_value("sensor_02", 20)
    store.set_value("sensor_01", 15)

    responses = list(
        stub.StreamChanges(
            message_service_pb2.StateChangeRequest(from_version=1)
        )
    )

    assert len(responses) == 1
    batch = responses[0]

    assert batch.from_version == 1
    assert batch.current_version == 3
    assert len(batch.events) == 2

    assert batch.events[0].version == 2
    assert batch.events[0].resource_id == "sensor_02"
    assert batch.events[0].value == 20

    assert batch.events[1].version == 3
    assert batch.events[1].resource_id == "sensor_01"
    assert batch.events[1].value == 15


def test_grpc_stream_changes_returns_empty_batch_when_client_is_up_to_date(grpc_realtime_context):
    store = grpc_realtime_context["state_store"]
    stub = grpc_realtime_context["stub"]

    store.set_value("sensor_01", 10)

    responses = list(
        stub.StreamChanges(
            message_service_pb2.StateChangeRequest(from_version=1)
        )
    )

    assert len(responses) == 1
    batch = responses[0]

    assert batch.from_version == 1
    assert batch.current_version == 1
    assert list(batch.events) == []


def test_grpc_stream_changes_rejects_negative_version(grpc_realtime_context):
    stub = grpc_realtime_context["stub"]

    with pytest.raises(grpc.RpcError) as exc_info:
        list(
            stub.StreamChanges(
                message_service_pb2.StateChangeRequest(from_version=-1)
            )
        )

    assert exc_info.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    assert exc_info.value.details() == "last_version cannot be negative"