from app.core.models.message import MessageEnvelope, OperationType
from app.core.services.state_store import InMemoryStateStore


def process_message(
    message: MessageEnvelope,
    state_store: InMemoryStateStore,
) -> dict:
    payload = message.payload

    if payload.operation == OperationType.SET_VALUE:
        state_store.set_value(payload.resource_id, payload.value)

        return {
            "status": "success",
            "message_id": str(message.message_id),
            "operation": payload.operation.value,
            "resource_id": payload.resource_id,
            "result": {
                "action": "value_updated",
                "stored_value": payload.value,
            },
        }

    if payload.operation == OperationType.GET_VALUE:
        current_value = state_store.get_value(payload.resource_id)

        return {
            "status": "success",
            "message_id": str(message.message_id),
            "operation": payload.operation.value,
            "resource_id": payload.resource_id,
            "result": {
                "action": "value_returned",
                "current_value": current_value,
            },
        }

    raise ValueError(f"Unsupported operation: {payload.operation}")