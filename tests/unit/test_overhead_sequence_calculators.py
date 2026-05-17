from app.overhead.calculators import calculate_sequence_overhead
from app.overhead.models import (
    AggregationMode,
    ApplicationProtocol,
    PayloadEncoding,
    SequencePatternInput,
)


def test_per_message_mode_keeps_one_aggregated_unit_per_message():
    input_data = SequencePatternInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[10, 10, 10],
        aggregation_mode=AggregationMode.PER_MESSAGE,
        batch_size=10,
        mtu_bytes=1500,
        message_frequency_hz=100.0,
    )

    result = calculate_sequence_overhead(input_data)

    assert result.original_message_count == 3
    assert result.aggregated_message_count == 3
    assert len(result.aggregated_units) == 3
    assert all(unit.original_message_count == 1 for unit in result.aggregated_units)


def test_batched_mode_groups_messages_by_batch_size():
    input_data = SequencePatternInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[10, 20, 30, 40, 50],
        aggregation_mode=AggregationMode.BATCHED,
        batch_size=2,
        mtu_bytes=1500,
        message_frequency_hz=50.0,
    )

    result = calculate_sequence_overhead(input_data)

    assert result.original_message_count == 5
    assert result.aggregated_message_count == 3
    assert len(result.aggregated_units) == 3
    assert result.aggregated_units[0].original_message_count == 2
    assert result.aggregated_units[1].original_message_count == 2
    assert result.aggregated_units[2].original_message_count == 1


def test_nagle_like_mode_reduces_message_count_for_small_payloads():
    input_data = SequencePatternInput(
        application_protocol=ApplicationProtocol.WEBSOCKET,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[10, 10, 10, 10, 10, 10],
        aggregation_mode=AggregationMode.NAGLE_LIKE,
        batch_size=10,
        mtu_bytes=1500,
        message_frequency_hz=200.0,
    )

    result = calculate_sequence_overhead(input_data)

    assert result.original_message_count == 6
    assert result.aggregated_message_count < 6
    assert len(result.aggregated_units) == result.aggregated_message_count


def test_batched_mode_can_reduce_total_transmitted_bytes_vs_per_message():
    per_message_input = SequencePatternInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[10, 10, 10, 10],
        aggregation_mode=AggregationMode.PER_MESSAGE,
        batch_size=1,
        mtu_bytes=1500,
        message_frequency_hz=100.0,
    )

    batched_input = SequencePatternInput(
        application_protocol=ApplicationProtocol.HTTP,
        payload_encoding=PayloadEncoding.JSON,
        payload_sizes_bytes=[10, 10, 10, 10],
        aggregation_mode=AggregationMode.BATCHED,
        batch_size=4,
        mtu_bytes=1500,
        message_frequency_hz=100.0,
    )

    per_message_result = calculate_sequence_overhead(per_message_input)
    batched_result = calculate_sequence_overhead(batched_input)

    assert batched_result.total_transmitted_bytes <= per_message_result.total_transmitted_bytes


def test_sequence_result_has_positive_bitrate():
    input_data = SequencePatternInput(
        application_protocol=ApplicationProtocol.GRPC,
        payload_encoding=PayloadEncoding.PROTOBUF,
        payload_sizes_bytes=[100, 120, 80],
        aggregation_mode=AggregationMode.BATCHED,
        batch_size=2,
        mtu_bytes=1500,
        message_frequency_hz=25.0,
    )

    result = calculate_sequence_overhead(input_data)

    assert result.required_bitrate_bps > 0
    assert result.required_bitrate_kbps > 0
    assert result.required_bitrate_mbps > 0