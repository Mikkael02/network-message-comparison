import json
from typing import Any

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


class HttpTransportClient:
    def __init__(self) -> None:
        self.client = TestClient(http_app)
        self.state_store = http_state_store

    def reset(self) -> None:
        self.state_store.clear()

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        response = self.client.post("/process", json=payload)
        data = response.json()
        data["_transport_status"] = response.status_code
        return data


class WsTransportClient:
    def __init__(self) -> None:
        self.client = TestClient(ws_app)
        self.state_store = ws_state_store

    def reset(self) -> None:
        self.state_store.clear()

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        with self.client.websocket_connect("/ws/process") as websocket:
            websocket.send_json(payload)
            return websocket.receive_json()


class GrpcTransportClient:
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

    def send(self, payload: dict[str, Any]) -> dict[str, Any]:
        request = self._build_request(payload)
        response = self.stub.Process(request)
        return self._normalize_response(response)

    @staticmethod
    def _build_request(payload: dict[str, Any]) -> message_service_pb2.MessageEnvelope:
        operation_map = {
            "set_value": message_service_pb2.SET_VALUE,
            "get_value": message_service_pb2.GET_VALUE,
        }

        payload_data = payload["payload"]
        message_payload = message_service_pb2.MessagePayload(
            operation=operation_map.get(
                payload_data["operation"],
                message_service_pb2.OPERATION_TYPE_UNSPECIFIED,
            ),
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
    def _normalize_response(response: message_service_pb2.ProcessReply) -> dict[str, Any]:
        outcome = response.WhichOneof("outcome")

        if outcome == "success":
            success = response.success
            result_type = success.WhichOneof("result")

            if result_type == "update_result":
                result = {
                    "action": success.update_result.action,
                    "stored_value": success.update_result.stored_value,
                }
            elif result_type == "get_result":
                result = {
                    "action": success.get_result.action,
                    "current_value": success.get_result.current_value,
                }
            else:
                result = {}

            return {
                "status": success.status,
                "message_id": success.message_id,
                "operation": success.operation,
                "resource_id": success.resource_id,
                "result": result,
            }

        error = response.error
        details = json.loads(error.details_json) if error.details_json else None

        return {
            "status": error.status,
            "error": {
                "code": error.code,
                "message": error.message,
                "details": details,
            },
        }