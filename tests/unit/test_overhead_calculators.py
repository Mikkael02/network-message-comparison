from app.overhead.calculators import (
    calculate_single_message_overhead,
    estimate_serialized_payload_size,
    resolve_application_protocol_overhead,
)
from app.overhead.models import (
    ApplicationProtocol,
    PayloadEncoding,
    TransmissionAnalysisInput,
)


def test_estimate_serialized_payload_size_for_protobuf_keeps_payload_size():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.GRPC,
        payload_encoding=PayloadEncoding.PROTOBUF,
        payload_size_bytes=100,
    )

    result = estimate_serialized_payload_size(input_data)

    assert result == 100


def test_estimate_serialized_payload_size_for_json_is_not_smaller_than_payload():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=100,
    )

    result = estimate_serialized_payload_size(input_data)

    assert result >= 100


def test_resolve_application_protocol_overhead_uses_manual_override():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=50,
        application_header_overhead_bytes=321,
    )

    result = resolve_application_protocol_overhead(input_data)

    assert result == 321


def test_calculate_single_message_overhead_for_small_http_payload():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=10,
        message_count=1,
        message_frequency_hz=10.0,
        mtu_bytes=1500,
    )

    result = calculate_single_message_overhead(input_data)

    assert result.frame_analysis.segment_count == 1
    assert result.frame_analysis.frame_count == 1
    assert result.layer_breakdown.payload_size_bytes == 10
    assert result.layer_breakdown.total_transmitted_bytes > 10
    assert result.efficiency.overhead_bytes > 0
    assert result.efficiency.payload_efficiency_ratio < 1.0


def test_calculate_single_message_overhead_detects_fragmentation_for_large_payload():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=5000,
        message_count=1,
        message_frequency_hz=1.0,
        mtu_bytes=1500,
    )

    result = calculate_single_message_overhead(input_data)

    assert result.frame_analysis.segment_count > 1
    assert result.frame_analysis.fragmentation_occurred is True
    assert len(result.frame_analysis.bytes_per_frame) == result.frame_analysis.frame_count


def test_calculate_single_message_overhead_for_grpc_protobuf_is_supported():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.GRPC,
        payload_encoding=PayloadEncoding.PROTOBUF,
        payload_size_bytes=120,
        message_count=2,
        message_frequency_hz=50.0,
        mtu_bytes=1500,
    )

    result = calculate_single_message_overhead(input_data)

    assert result.serialized_payload_size_bytes == 120
    assert result.input_summary.application_protocol == ApplicationProtocol.GRPC
    assert result.total_sequence_payload_bytes == 240
    assert result.total_sequence_transmitted_bytes >= result.layer_breakdown.total_transmitted_bytes * 2


def test_required_bitrate_is_positive():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.WEBSOCKET,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=64,
        message_count=1,
        message_frequency_hz=100.0,
        mtu_bytes=1500,
    )

    result = calculate_single_message_overhead(input_data)

    assert result.efficiency.required_bitrate_bps > 0
    assert result.efficiency.required_bitrate_kbps > 0
    assert result.efficiency.required_bitrate_mbps > 0