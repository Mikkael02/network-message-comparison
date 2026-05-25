from typing import Any

from app.shared.error_codes import ErrorCode
from app.shared.response_models import ErrorResponse, SuccessResponse


def build_success_response(result: dict[str, Any]) -> SuccessResponse:
    return SuccessResponse(**result)


def build_error_response(
    code: ErrorCode,
    message: str,
    details: Any = None,
) -> ErrorResponse:
    return ErrorResponse(
        error={
            "code": code,
            "message": message,
            "details": details,
        }
    )