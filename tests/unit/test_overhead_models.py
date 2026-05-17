import pytest
from pydantic import ValidationError

from app.overhead.models import (
    AggregationMode,
    ApplicationProtocol,
    PayloadEncoding,
    SequencePatternInput,
    TrafficDirection,
    TransmissionAnalysisInput,
)


def test_transmission_analysis_input_validates_correctly():
    model = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=128,
        message_count=10,
        message_frequency_hz=20.0,
        batch_size=2,
        aggregation_mode=AggregationMode.BATCHED,
        traffic_direction=TrafficDirection.REQUEST,
        mtu_bytes=1500,
        nagle_enabled=True,
    )

    assert model.application_protocol == ApplicationProtocol.HTTP
    assert model.payload_encoding == PayloadEncoding.JSON
    assert model.payload_size_bytes == 128
    assert model.message_count == 10
    assert model.batch_size == 2
    assert model.mtu_bytes == 1500
    assert model.nagle_enabled is True


def test_transmission_analysis_input_rejects_invalid_payload_size():
    with pytest.raises(ValidationError):
        TransmissionAnalysisInput(
            application_protocol=ApplicationProtocol.HTTP,
            payload_encoding=PayloadEncoding.JSON,
            payload_size_bytes=0,
        )


def test_transmission_analysis_input_rejects_invalid_mtu():
    with pytest.raises(ValidationError):
        TransmissionAnalysisInput(
            application_protocol=ApplicationProtocol.GRPC,
            payload_encoding=PayloadEncoding.PROTOBUF,
            payload_size_bytes=64,
            mtu_bytes=40,
        )


def test_sequence_pattern_input_accepts_valid_payload_list():
    model = SequencePatternInput(
        application_protocol=ApplicationProtocol.WEBSOCKET,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[10, 20, 30],
    )

    assert model.payload_sizes_bytes == [10, 20, 30]


def test_sequence_pattern_input_rejects_empty_list():
    with pytest.raises(ValidationError):
        SequencePatternInput(
            application_protocol=ApplicationProtocol.WEBSOCKET,
            payload_encoding=PayloadEncoding.JSON,
            payload_sizes_bytes=[],
        )


def test_sequence_pattern_input_rejects_non_positive_payload_sizes():
    with pytest.raises(ValidationError):
        SequencePatternInput(
            application_protocol=ApplicationProtocol.WEBSOCKET,
            payload_encoding=PayloadEncoding.JSON,
            payload_sizes_bytes=[10, 0, 30],
        )