from app.shared.error_codes import ErrorCode
from app.shared.response_builders import (
    build_error_response,
    build_success_response,
)


def test_build_success_response_returns_expected_structure():
    result = {
        "message_id": "123",
        "operation": "set_value",
        "resource_id": "sensor_01",
        "result": {
            "action": "value_updated",
            "stored_value": 42,
        },
    }

    response = build_success_response(result)

    assert response.status == "success"
    assert response.message_id == "123"
    assert response.operation == "set_value"
    assert response.resource_id == "sensor_01"
    assert response.result["stored_value"] == 42


def test_build_error_response_returns_expected_structure():
    response = build_error_response(
        code=ErrorCode.BUSINESS_VALIDATION_ERROR,
        message="Cannot modify resources marked as readonly",
    )

    assert response.status == "error"
    assert response.error.code == ErrorCode.BUSINESS_VALIDATION_ERROR
    assert response.error.message == "Cannot modify resources marked as readonly"
    assert response.error.details is None