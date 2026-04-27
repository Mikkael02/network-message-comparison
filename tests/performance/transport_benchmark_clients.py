import json

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


class HttpBenchmarkClient:
    def __init__(self) -> None:
        self.client = TestClient(http_app)
        self.state_store = http_state_store

    def reset(self) -> None:
        self.state_store.clear()

    def close(self) -> None:
        pass

    def send(self, payload: dict) -> dict:
        response = self.client.post("/process", json=payload)
        return response.json()


class WsBenchmarkClient:
    def __init__(self) -> None:
        self.client = TestClient(ws_app)
        self.state_store = ws_state_store
        self._ws_context = None
        self.websocket = None

    def open(self) -> None:
        self._ws_context = self.client.websocket_connect("/ws/process")
        self.websocket = self._ws_context.__enter__()

    def reset(self) -> None:
        self.state_store.clear()

    def close(self) -> None:
        if self._ws_context is not None:
            self._ws_context.__exit__(None, None, None)
            self._ws_context = None
            self.websocket = None

    def send(self, payload: dict) -> dict:
        self.websocket.send_json(payload)
        return self.websocket.receive_json()


class GrpcBenchmarkClient:
    def __init__(self) -> None:
        self.state_store = InMemoryStateStore()
        self.server = create_server(self.state_store)
        port = self.server.add_insecure_port("127.0.0.1:0")
        self.server.start()

        self.channel = grpc.insecure_channel(f"127.0.0.1:{port}")
        grpc.channel_ready_future(self.channel).result(timeout=5)
        self.stub = message_service_pb2_grpc.MessageServiceStub(self.channel)

    def reset(self) -> None:
        self.state_store.clear()

    def close(self) -> None:
        self.channel.close()
        self.server.stop(None)

    def send(self, payload: dict) -> dict:
        request = self._build_request(payload)
        response = self.stub.Process(request)
        return self._normalize_response(response)

    @staticmethod
    def _build_request(payload: dict) -> message_service_pb2.MessageEnvelope:
        operation_map = {
            "set_value": message_service_pb2.SET_VALUE,
            "get_value": message_service_pb2.GET_VALUE,
        }

        payload_data = payload["payload"]
        message_payload = message_service_pb2.MessagePayload(
            operation=operation_map[payload_data["operation"]],
            resource_id=payload_data["resource_id"],
        )

        if "value" in payload_data:
            message_payload.value = payload_data["value"]

        request = message_service_pb2.MessageEnvelope(
            source=payload["source"],
            payload=message_payload,
        )

        if "message_id" in payload:
            request.message_id = payload["message_id"]

        if "timestamp" in payload:
            request.timestamp = payload["timestamp"]

        return request

    @staticmethod
    def _normalize_response(response: message_service_pb2.ProcessReply) -> dict:
        outcome = response.WhichOneof("outcome")

        if outcome == "success":
            success = response.success
            result_type = success.WhichOneof("result")

            if result_type == "update_result":
                result = {
                    "action": success.update_result.action,
                    "stored_value": success.update_result.stored_value,
                }
            else:
                result = {
                    "action": success.get_result.action,
                    "current_value": success.get_result.current_value,
                }

            return {
                "status": success.status,
                "message_id": success.message_id,
                "operation": success.operation,
                "resource_id": success.resource_id,
                "result": result,
            }

        details = json.loads(response.error.details_json) if response.error.details_json else None

        return {
            "status": response.error.status,
            "error": {
                "code": response.error.code,
                "message": response.error.message,
                "details": details,
            },
        }