import grpc
from fastapi.testclient import TestClient

from app.core.services.state_store import InMemoryStateStore
from app.transport_grpc.generated import (
    message_service_pb2,
    message_service_pb2_grpc,
)
from app.transport_grpc.server import create_server
from app.transport_http.server import app as http_app, state_store as http_state_store
from app.transport_ws.server import app as ws_app, state_store as ws_state_store


class HttpRealtimeClient:
    def __init__(self) -> None:
        self.client = TestClient(http_app)
        self.state_store = http_state_store

    def reset(self) -> None:
        self.state_store.clear()

    def seed(self) -> None:
        self.state_store.set_value("sensor_01", 10)
        self.state_store.set_value("sensor_02", 20)
        self.state_store.set_value("sensor_01", 15)

    def get_changes(self, from_version: int) -> dict:
        response = self.client.get("/changes", params={"from_version": from_version})
        return response.json()


class WsRealtimeClient:
    def __init__(self) -> None:
        self.client = TestClient(ws_app)
        self.state_store = ws_state_store

    def reset(self) -> None:
        self.state_store.clear()

    def seed(self) -> None:
        self.state_store.set_value("sensor_01", 10)
        self.state_store.set_value("sensor_02", 20)
        self.state_store.set_value("sensor_01", 15)

    def get_changes(self, from_version: int) -> dict:
        with self.client.websocket_connect("/ws/changes") as websocket:
            websocket.send_json({"from_version": from_version})
            response = websocket.receive_json()

        if response["status"] != "success":
            raise RuntimeError(f"Unexpected WebSocket realtime error response: {response}")

        return response["batch"]


class GrpcRealtimeClient:
    def __init__(self) -> None:
        self.state_store = InMemoryStateStore()
        self.server = create_server(self.state_store)

        port = self.server.add_insecure_port("127.0.0.1:0")
        self.server.start()

        self.channel = grpc.insecure_channel(f"127.0.0.1:{port}")
        grpc.channel_ready_future(self.channel).result(timeout=5)
        self.stub = message_service_pb2_grpc.MessageServiceStub(self.channel)

    def close(self) -> None:
        self.channel.close()
        self.server.stop(None)

    def reset(self) -> None:
        self.state_store.clear()

    def seed(self) -> None:
        self.state_store.set_value("sensor_01", 10)
        self.state_store.set_value("sensor_02", 20)
        self.state_store.set_value("sensor_01", 15)

    def get_changes(self, from_version: int) -> dict:
        responses = list(
            self.stub.StreamChanges(
                message_service_pb2.StateChangeRequest(from_version=from_version)
            )
        )

        if len(responses) != 1:
            raise RuntimeError(
                f"Expected exactly one batch in current streaming setup, got {len(responses)}"
            )

        batch = responses[0]
        return {
            "from_version": batch.from_version,
            "current_version": batch.current_version,
            "events": [
                {
                    "version": event.version,
                    "timestamp": event.timestamp,
                    "resource_id": event.resource_id,
                    "value": event.value,
                }
                for event in batch.events
            ],
        }