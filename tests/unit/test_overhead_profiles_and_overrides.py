from app.overhead.calculators import (
    calculate_sequence_overhead,
    calculate_single_message_overhead,
)
from app.overhead.models import (
    AggregationMode,
    ApplicationProtocol,
    PayloadEncoding,
    SequencePatternInput,
    TransmissionAnalysisInput,
    TransmissionProfile,
)


def test_standard_profile_is_used_when_no_manual_overrides_are_provided():
    input_data = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=100,
        transmission_profile=TransmissionProfile.STANDARD_ETHERNET,
    )

    result = calculate_single_message_overhead(input_data)

    assert result.effective_settings.transmission_profile == TransmissionProfile.STANDARD_ETHERNET
    assert result.effective_settings.mtu_bytes == 1500
    assert result.effective_settings.ipv4_header_size_bytes == 20
    assert result.effective_settings.tcp_header_size_bytes == 20


def test_constrained_mtu_profile_increases_fragmentation_for_large_payload():
    standard_input = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=4000,
        transmission_profile=TransmissionProfile.STANDARD_ETHERNET,
    )

    constrained_input = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_size_bytes=4000,
        transmission_profile=TransmissionProfile.CONSTRAINED_MTU,
    )

    standard_result = calculate_single_message_overhead(standard_input)
    constrained_result = calculate_single_message_overhead(constrained_input)

    assert constrained_result.frame_analysis.segment_count >= standard_result.frame_analysis.segment_count
    assert constrained_result.effective_settings.mtu_bytes == 576


def test_tcp_header_override_changes_effective_settings_and_total_transfer():
    base_input = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.GRPC,
        payload_encoding=PayloadEncoding.PROTOBUF,
        payload_size_bytes=500,
        transmission_profile=TransmissionProfile.STANDARD_ETHERNET,
    )

    override_input = TransmissionAnalysisInput(
        application_protocol=ApplicationProtocol.GRPC,
        payload_encoding=PayloadEncoding.PROTOBUF,
        payload_size_bytes=500,
        transmission_profile=TransmissionProfile.STANDARD_ETHERNET,
        tcp_header_size_bytes=40,
    )

    base_result = calculate_single_message_overhead(base_input)
    override_result = calculate_single_message_overhead(override_input)

    assert override_result.effective_settings.tcp_header_size_bytes == 40
    assert override_result.layer_breakdown.total_transmitted_bytes >= base_result.layer_breakdown.total_transmitted_bytes


def test_sequence_calculation_uses_profile_and_manual_overrides():
    input_data = SequencePatternInput(
        application_protocol=ApplicationProtocol.WEBSOCKET,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[50, 50, 50, 50],
        aggregation_mode=AggregationMode.BATCHED,
        batch_size=2,
        transmission_profile=TransmissionProfile.TCP_OPTIONS_HEAVY,
        ethernet_min_payload_bytes=64,
    )

    result = calculate_sequence_overhead(input_data)

    assert result.effective_settings.transmission_profile == TransmissionProfile.TCP_OPTIONS_HEAVY
    assert result.effective_settings.ipv4_header_size_bytes == 24
    assert result.effective_settings.tcp_header_size_bytes == 32
    assert result.effective_settings.ethernet_min_payload_bytes == 64
    assert result.aggregated_message_count == 2