from app.core.models.message import MessageEnvelope, OperationType
from app.core.validation.exceptions import BusinessValidationError


def validate_business_rules(message: MessageEnvelope) -> None:
    payload = message.payload

    if payload.operation == OperationType.SET_VALUE:
        if payload.resource_id.startswith("readonly_"):
            raise BusinessValidationError(
                "Cannot modify resources marked as readonly"
            )

        if payload.value is None:
            raise BusinessValidationError(
                "SET_VALUE operation requires a value"
            )

    if payload.operation == OperationType.GET_VALUE:
        if payload.resource_id.startswith("archived_"):
            raise BusinessValidationError(
                "Archived resources cannot be queried"
            )