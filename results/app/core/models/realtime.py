from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field, field_validator


class StateChangeEvent(BaseModel):
    version: int = Field(..., ge=1)
    timestamp: datetime
    resource_id: str = Field(..., min_length=1, max_length=100)
    value: int = Field(..., ge=0, le=1000)

    @field_validator("resource_id")
    @classmethod
    def validate_resource_id(cls, value: str) -> str:
        value = value.strip()
        if not value:
            raise ValueError("resource_id cannot be empty or blank")
        return value


class StateChangeBatch(BaseModel):
    from_version: int = Field(..., ge=0)
    current_version: int = Field(..., ge=0)
    events: list[StateChangeEvent]


class StateChangeRequest(BaseModel):
    from_version: int = Field(..., ge=0)


class StateChangeWsResponse(BaseModel):
    status: Literal["success"] = "success"
    batch: StateChangeBatch