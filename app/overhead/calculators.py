import math

from app.overhead.models import (
    TransmissionAnalysisInput,
    TransmissionAnalysisResult,
    LayerOverheadBreakdown,
    FrameAnalysis,
    EfficiencyAnalysis,
    SequencePatternInput,
    SequenceTransmissionAnalysisResult,
    AggregatedTransmissionUnit,
    AggregationMode,
)
from app.overhead.presets import (
    DEFAULT_LAYER_PRESETS,
    DEFAULT_PROTOCOL_PRESETS,
)


def _estimate_serialized_size_for_encoding(encoding: str, payload_size_bytes: int) -> int:
    if encoding == "protobuf":
        return payload_size_bytes

    if encoding == "json":
        json_factor = 1.2
        return max(payload_size_bytes, math.ceil(payload_size_bytes * json_factor))

    return payload_size_bytes


def estimate_serialized_payload_size(input_data: TransmissionAnalysisInput) -> int:
    return _estimate_serialized_size_for_encoding(
        input_data.payload_encoding.value,
        input_data.payload_size_bytes,
    )


def resolve_application_protocol_overhead(input_data: TransmissionAnalysisInput) -> int:
    if input_data.application_header_overhead_bytes is not None:
        return input_data.application_header_overhead_bytes

    return DEFAULT_PROTOCOL_PRESETS[
        input_data.application_protocol
    ].default_header_overhead_bytes


def _resolve_application_protocol_overhead_for_sequence(
    input_data: SequencePatternInput,
) -> int:
    if input_data.application_header_overhead_bytes is not None:
        return input_data.application_header_overhead_bytes

    return DEFAULT_PROTOCOL_PRESETS[
        input_data.application_protocol
    ].default_header_overhead_bytes


def _calculate_transport_metrics(
    payload_size_bytes: int,
    serialized_payload_size_bytes: int,
    application_protocol_overhead_bytes: int,
    mtu_bytes: int,
    message_frequency_hz: float,
):
    transport_overhead_bytes = DEFAULT_LAYER_PRESETS["tcp"].header_size_bytes
    network_overhead_bytes = DEFAULT_LAYER_PRESETS["ipv4"].header_size_bytes
    link_header_bytes = DEFAULT_LAYER_PRESETS["ethernet"].header_size_bytes
    link_trailer_bytes = DEFAULT_LAYER_PRESETS["ethernet"].trailer_size_bytes
    ethernet_min_payload_bytes = DEFAULT_LAYER_PRESETS["ethernet"].minimum_payload_bytes

    transport_payload_bytes = (
        serialized_payload_size_bytes + application_protocol_overhead_bytes
    )

    max_transport_payload_per_segment = (
        mtu_bytes - transport_overhead_bytes - network_overhead_bytes
    )
    if max_transport_payload_per_segment <= 0:
        raise ValueError("MTU is too small for IPv4 + TCP headers")

    segment_count = math.ceil(
        transport_payload_bytes / max_transport_payload_per_segment
    )

    remaining_payload = transport_payload_bytes
    bytes_per_frame: list[int] = []
    total_transmitted_bytes = 0
    unused_payload_space_bytes = 0

    for _ in range(segment_count):
        segment_payload = min(remaining_payload, max_transport_payload_per_segment)
        remaining_payload -= segment_payload

        ip_packet_bytes = (
            network_overhead_bytes + transport_overhead_bytes + segment_payload
        )

        ethernet_payload_bytes = max(ip_packet_bytes, ethernet_min_payload_bytes)
        frame_bytes = link_header_bytes + ethernet_payload_bytes + link_trailer_bytes

        bytes_per_frame.append(frame_bytes)
        total_transmitted_bytes += frame_bytes

        if ip_packet_bytes < ethernet_min_payload_bytes:
            unused_payload_space_bytes += ethernet_min_payload_bytes - ip_packet_bytes

    overhead_bytes = total_transmitted_bytes - payload_size_bytes
    overhead_ratio = overhead_bytes / total_transmitted_bytes
    payload_efficiency_ratio = payload_size_bytes / total_transmitted_bytes

    required_bitrate_bps = total_transmitted_bytes * 8 * message_frequency_hz
    required_bitrate_kbps = required_bitrate_bps / 1000
    required_bitrate_mbps = required_bitrate_bps / 1_000_000

    return {
        "transport_overhead_bytes": transport_overhead_bytes,
        "network_overhead_bytes": network_overhead_bytes,
        "link_overhead_bytes": link_header_bytes + link_trailer_bytes,
        "segment_count": segment_count,
        "frame_count": segment_count,
        "bytes_per_frame": bytes_per_frame,
        "unused_payload_space_bytes": unused_payload_space_bytes,
        "fragmentation_occurred": segment_count > 1,
        "total_transmitted_bytes": total_transmitted_bytes,
        "overhead_bytes": overhead_bytes,
        "overhead_ratio": overhead_ratio,
        "payload_efficiency_ratio": payload_efficiency_ratio,
        "required_bitrate_bps": required_bitrate_bps,
        "required_bitrate_kbps": required_bitrate_kbps,
        "required_bitrate_mbps": required_bitrate_mbps,
        "max_transport_payload_per_segment": max_transport_payload_per_segment,
    }


def calculate_single_message_overhead(
    input_data: TransmissionAnalysisInput,
) -> TransmissionAnalysisResult:
    serialized_payload_size_bytes = estimate_serialized_payload_size(input_data)
    application_protocol_overhead_bytes = resolve_application_protocol_overhead(
        input_data
    )

    metrics = _calculate_transport_metrics(
        payload_size_bytes=input_data.payload_size_bytes,
        serialized_payload_size_bytes=serialized_payload_size_bytes,
        application_protocol_overhead_bytes=application_protocol_overhead_bytes,
        mtu_bytes=input_data.mtu_bytes,
        message_frequency_hz=input_data.message_frequency_hz,
    )

    total_sequence_payload_bytes = input_data.payload_size_bytes * input_data.message_count
    total_sequence_transmitted_bytes = (
        metrics["total_transmitted_bytes"] * input_data.message_count
    )

    notes = [
        f"Application protocol: {input_data.application_protocol.value}",
        f"Payload encoding: {input_data.payload_encoding.value}",
        "Calculation assumes Ethernet II + IPv4 + TCP baseline model.",
    ]

    if metrics["segment_count"] > 1:
        notes.append("Payload exceeds single TCP segment for the configured MTU.")

    if metrics["unused_payload_space_bytes"] > 0:
        notes.append("Ethernet minimum payload size caused additional unused space.")

    return TransmissionAnalysisResult(
        input_summary=input_data,
        serialized_payload_size_bytes=serialized_payload_size_bytes,
        total_sequence_payload_bytes=total_sequence_payload_bytes,
        total_sequence_transmitted_bytes=total_sequence_transmitted_bytes,
        total_messages_after_aggregation=input_data.message_count,
        layer_breakdown=LayerOverheadBreakdown(
            payload_size_bytes=input_data.payload_size_bytes,
            serialized_payload_size_bytes=serialized_payload_size_bytes,
            application_protocol_overhead_bytes=application_protocol_overhead_bytes,
            transport_overhead_bytes=metrics["transport_overhead_bytes"],
            network_overhead_bytes=metrics["network_overhead_bytes"],
            link_overhead_bytes=metrics["link_overhead_bytes"],
            total_transmitted_bytes=metrics["total_transmitted_bytes"],
        ),
        frame_analysis=FrameAnalysis(
            mtu_bytes=input_data.mtu_bytes,
            segment_count=metrics["segment_count"],
            frame_count=metrics["frame_count"],
            bytes_per_frame=metrics["bytes_per_frame"],
            unused_payload_space_bytes=metrics["unused_payload_space_bytes"],
            fragmentation_occurred=metrics["fragmentation_occurred"],
        ),
        efficiency=EfficiencyAnalysis(
            overhead_bytes=metrics["overhead_bytes"],
            overhead_ratio=metrics["overhead_ratio"],
            payload_efficiency_ratio=metrics["payload_efficiency_ratio"],
            required_bitrate_bps=metrics["required_bitrate_bps"],
            required_bitrate_kbps=metrics["required_bitrate_kbps"],
            required_bitrate_mbps=metrics["required_bitrate_mbps"],
        ),
        notes=notes,
    )


def _group_payloads_batched(
    payload_sizes: list[int],
    serialized_sizes: list[int],
    batch_size: int,
) -> list[tuple[int, int, int]]:
    groups = []

    for i in range(0, len(payload_sizes), batch_size):
        payload_chunk = payload_sizes[i:i + batch_size]
        serialized_chunk = serialized_sizes[i:i + batch_size]

        groups.append(
            (
                len(payload_chunk),
                sum(payload_chunk),
                sum(serialized_chunk),
            )
        )

    return groups


def _group_payloads_nagle_like(
    payload_sizes: list[int],
    serialized_sizes: list[int],
    batch_size: int,
    application_protocol_overhead_bytes: int,
    max_transport_payload_per_segment: int,
) -> list[tuple[int, int, int]]:
    groups: list[tuple[int, int, int]] = []

    current_count = 0
    current_payload_sum = 0
    current_serialized_sum = 0

    for payload_size, serialized_size in zip(payload_sizes, serialized_sizes):
        candidate_serialized_sum = current_serialized_sum + serialized_size
        candidate_transport_payload = (
            candidate_serialized_sum + application_protocol_overhead_bytes
        )

        should_flush = False

        if current_count > 0:
            if candidate_transport_payload > max_transport_payload_per_segment:
                should_flush = True
            elif current_count >= batch_size:
                should_flush = True

        if should_flush:
            groups.append(
                (
                    current_count,
                    current_payload_sum,
                    current_serialized_sum,
                )
            )
            current_count = 0
            current_payload_sum = 0
            current_serialized_sum = 0

        current_count += 1
        current_payload_sum += payload_size
        current_serialized_sum += serialized_size

    if current_count > 0:
        groups.append(
            (
                current_count,
                current_payload_sum,
                current_serialized_sum,
            )
        )

    return groups


def calculate_sequence_overhead(
    input_data: SequencePatternInput,
) -> SequenceTransmissionAnalysisResult:
    payload_sizes = input_data.payload_sizes_bytes
    serialized_sizes = [
        _estimate_serialized_size_for_encoding(
            input_data.payload_encoding.value,
            payload_size,
        )
        for payload_size in payload_sizes
    ]

    application_protocol_overhead_bytes = _resolve_application_protocol_overhead_for_sequence(
        input_data
    )

    transport_overhead_bytes = DEFAULT_LAYER_PRESETS["tcp"].header_size_bytes
    network_overhead_bytes = DEFAULT_LAYER_PRESETS["ipv4"].header_size_bytes
    max_transport_payload_per_segment = (
        input_data.mtu_bytes - transport_overhead_bytes - network_overhead_bytes
    )
    if max_transport_payload_per_segment <= 0:
        raise ValueError("MTU is too small for IPv4 + TCP headers")

    if input_data.aggregation_mode == AggregationMode.PER_MESSAGE:
        grouped = list(
            zip(
                [1] * len(payload_sizes),
                payload_sizes,
                serialized_sizes,
            )
        )

    elif input_data.aggregation_mode == AggregationMode.BATCHED:
        grouped = _group_payloads_batched(
            payload_sizes,
            serialized_sizes,
            input_data.batch_size,
        )

    else:
        grouped = _group_payloads_nagle_like(
            payload_sizes,
            serialized_sizes,
            input_data.batch_size,
            application_protocol_overhead_bytes,
            max_transport_payload_per_segment,
        )

    aggregated_units: list[AggregatedTransmissionUnit] = []
    total_transmitted_bytes = 0
    total_frame_count = 0
    total_original_payload_bytes = sum(payload_sizes)
    total_serialized_payload_bytes = sum(serialized_sizes)

    for index, (message_count, payload_sum, serialized_sum) in enumerate(grouped, start=1):
        metrics = _calculate_transport_metrics(
            payload_size_bytes=payload_sum,
            serialized_payload_size_bytes=serialized_sum,
            application_protocol_overhead_bytes=application_protocol_overhead_bytes,
            mtu_bytes=input_data.mtu_bytes,
            message_frequency_hz=input_data.message_frequency_hz,
        )

        aggregated_units.append(
            AggregatedTransmissionUnit(
                batch_index=index,
                original_message_count=message_count,
                original_payload_bytes_sum=payload_sum,
                aggregated_serialized_payload_size_bytes=serialized_sum,
                application_protocol_overhead_bytes=application_protocol_overhead_bytes,
                total_transmitted_bytes=metrics["total_transmitted_bytes"],
                frame_count=metrics["frame_count"],
            )
        )

        total_transmitted_bytes += metrics["total_transmitted_bytes"]
        total_frame_count += metrics["frame_count"]

    overhead_bytes = total_transmitted_bytes - total_original_payload_bytes
    overhead_ratio = overhead_bytes / total_transmitted_bytes
    payload_efficiency_ratio = total_original_payload_bytes / total_transmitted_bytes

    sequence_duration_seconds = (
        len(payload_sizes) / input_data.message_frequency_hz
    )
    required_bitrate_bps = (total_transmitted_bytes * 8) / sequence_duration_seconds
    required_bitrate_kbps = required_bitrate_bps / 1000
    required_bitrate_mbps = required_bitrate_bps / 1_000_000

    notes = [
        f"Aggregation mode: {input_data.aggregation_mode.value}",
        "Sequence calculation assumes Ethernet II + IPv4 + TCP baseline model.",
    ]

    if input_data.aggregation_mode == AggregationMode.BATCHED:
        notes.append(
            "Messages are grouped into fixed-size batches before transmission."
        )

    if input_data.aggregation_mode == AggregationMode.NAGLE_LIKE:
        notes.append(
            "Messages are greedily aggregated until the payload nears single-segment capacity."
        )

    return SequenceTransmissionAnalysisResult(
        input_summary=input_data,
        original_message_count=len(payload_sizes),
        aggregated_message_count=len(grouped),
        total_original_payload_bytes=total_original_payload_bytes,
        total_serialized_payload_bytes=total_serialized_payload_bytes,
        total_transmitted_bytes=total_transmitted_bytes,
        total_frame_count=total_frame_count,
        overhead_bytes=overhead_bytes,
        overhead_ratio=overhead_ratio,
        payload_efficiency_ratio=payload_efficiency_ratio,
        required_bitrate_bps=required_bitrate_bps,
        required_bitrate_kbps=required_bitrate_kbps,
        required_bitrate_mbps=required_bitrate_mbps,
        aggregated_units=aggregated_units,
        notes=notes,
    )