from datetime import datetime, timezone
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field, field_validator, model_validator


class OperationType(str, Enum):
    SET_VALUE = "set_value"
    GET_VALUE = "get_value"


class MessagePayload(BaseModel):
    operation: OperationType
    resource_id: str = Field(..., min_length=1, max_length=100)
    value: Optional[int] = Field(default=None, ge=0, le=1000)

    @field_validator("resource_id")
    @classmethod
    def validate_resource_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("resource_id cannot be empty or blank")
        return value

    @model_validator(mode="after")
    def validate_payload_consistency(self) -> "MessagePayload":
        if self.operation == OperationType.SET_VALUE and self.value is None:
            raise ValueError("value is required for set_value operation")

        if self.operation == OperationType.GET_VALUE and self.value is not None:
            raise ValueError("value must not be provided for get_value operation")

        return self


class MessageEnvelope(BaseModel):
    message_id: UUID = Field(default_factory=uuid4)
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = Field(..., min_length=1, max_length=50)
    payload: MessagePayload

    @field_validator("source")
    @classmethod
    def validate_source(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("source cannot be empty or blank")
        return value