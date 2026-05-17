from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import json
from datetime import datetime, timezone

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
)


RAW_OUTPUT_PATH = Path("results/raw/transmission_overhead_demo.json")
TEXT_OUTPUT_PATH = Path("results/processed/transmission_overhead_demo.txt")

RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
TEXT_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def build_demo_scenarios() -> dict:
    return {
        "single_message": [
            (
                "http_small_json_single",
                calculate_single_message_overhead(
                    TransmissionAnalysisInput(
                        application_protocol=ApplicationProtocol.HTTP,
                        payload_encoding=PayloadEncoding.JSON,
                        payload_size_bytes=10,
                        message_count=1,
                        message_frequency_hz=100.0,
                        mtu_bytes=1500,
                    )
                ),
            ),
            (
                "grpc_small_protobuf_single",
                calculate_single_message_overhead(
                    TransmissionAnalysisInput(
                        application_protocol=ApplicationProtocol.GRPC,
                        payload_encoding=PayloadEncoding.PROTOBUF,
                        payload_size_bytes=10,
                        message_count=1,
                        message_frequency_hz=100.0,
                        mtu_bytes=1500,
                    )
                ),
            ),
            (
                "http_large_json_single",
                calculate_single_message_overhead(
                    TransmissionAnalysisInput(
                        application_protocol=ApplicationProtocol.HTTP,
                        payload_encoding=PayloadEncoding.JSON,
                        payload_size_bytes=5000,
                        message_count=1,
                        message_frequency_hz=10.0,
                        mtu_bytes=1500,
                    )
                ),
            ),
        ],
        "sequence": [
            (
                "http_sequence_per_message",
                calculate_sequence_overhead(
                    SequencePatternInput(
                        application_protocol=ApplicationProtocol.HTTP,
                        payload_encoding=PayloadEncoding.JSON,
                        payload_sizes_bytes=[10, 10, 10, 10, 10, 10],
                        aggregation_mode=AggregationMode.PER_MESSAGE,
                        batch_size=1,
                        message_frequency_hz=100.0,
                        mtu_bytes=1500,
                    )
                ),
            ),
            (
                "http_sequence_batched",
                calculate_sequence_overhead(
                    SequencePatternInput(
                        application_protocol=ApplicationProtocol.HTTP,
                        payload_encoding=PayloadEncoding.JSON,
                        payload_sizes_bytes=[10, 10, 10, 10, 10, 10],
                        aggregation_mode=AggregationMode.BATCHED,
                        batch_size=3,
                        message_frequency_hz=100.0,
                        mtu_bytes=1500,
                    )
                ),
            ),
            (
                "ws_sequence_nagle_like",
                calculate_sequence_overhead(
                    SequencePatternInput(
                        application_protocol=ApplicationProtocol.WEBSOCKET,
                        payload_encoding=PayloadEncoding.JSON,
                        payload_sizes_bytes=[10, 10, 10, 10, 10, 10],
                        aggregation_mode=AggregationMode.NAGLE_LIKE,
                        batch_size=10,
                        message_frequency_hz=100.0,
                        mtu_bytes=1500,
                    )
                ),
            ),
        ],
    }


def build_raw_output(scenarios: dict) -> dict:
    return {
        "generated_at": now_utc_iso(),
        "single_message": [
            {
                "scenario_name": scenario_name,
                "result": result.model_dump(mode="json"),
            }
            for scenario_name, result in scenarios["single_message"]
        ],
        "sequence": [
            {
                "scenario_name": scenario_name,
                "result": result.model_dump(mode="json"),
            }
            for scenario_name, result in scenarios["sequence"]
        ],
    }


def build_text_report(scenarios: dict) -> str:
    lines: list[str] = []

    lines.append("TRANSMISSION OVERHEAD DEMO REPORT")
    lines.append("")

    lines.append("1. Single message scenarios")
    for scenario_name, result in scenarios["single_message"]:
        lines.append(f"Scenario: {scenario_name}")
        lines.append(
            f"- payload_size_bytes={result.layer_breakdown.payload_size_bytes}"
        )
        lines.append(
            f"- serialized_payload_size_bytes={result.serialized_payload_size_bytes}"
        )
        lines.append(
            f"- application_protocol_overhead_bytes="
            f"{result.layer_breakdown.application_protocol_overhead_bytes}"
        )
        lines.append(
            f"- total_transmitted_bytes={result.layer_breakdown.total_transmitted_bytes}"
        )
        lines.append(
            f"- frame_count={result.frame_analysis.frame_count}"
        )
        lines.append(
            f"- fragmentation_occurred={result.frame_analysis.fragmentation_occurred}"
        )
        lines.append(
            f"- payload_efficiency_ratio={result.efficiency.payload_efficiency_ratio:.4f}"
        )
        lines.append(
            f"- required_bitrate_kbps={result.efficiency.required_bitrate_kbps:.4f}"
        )
        lines.append("")

    lines.append("2. Sequence scenarios")
    for scenario_name, result in scenarios["sequence"]:
        lines.append(f"Scenario: {scenario_name}")
        lines.append(
            f"- original_message_count={result.original_message_count}"
        )
        lines.append(
            f"- aggregated_message_count={result.aggregated_message_count}"
        )
        lines.append(
            f"- total_original_payload_bytes={result.total_original_payload_bytes}"
        )
        lines.append(
            f"- total_serialized_payload_bytes={result.total_serialized_payload_bytes}"
        )
        lines.append(
            f"- total_transmitted_bytes={result.total_transmitted_bytes}"
        )
        lines.append(
            f"- total_frame_count={result.total_frame_count}"
        )
        lines.append(
            f"- overhead_ratio={result.overhead_ratio:.4f}"
        )
        lines.append(
            f"- payload_efficiency_ratio={result.payload_efficiency_ratio:.4f}"
        )
        lines.append(
            f"- required_bitrate_kbps={result.required_bitrate_kbps:.4f}"
        )
        lines.append("- aggregated_units:")
        for unit in result.aggregated_units:
            lines.append(
                f"  - batch_index={unit.batch_index}, "
                f"original_message_count={unit.original_message_count}, "
                f"original_payload_bytes_sum={unit.original_payload_bytes_sum}, "
                f"total_transmitted_bytes={unit.total_transmitted_bytes}, "
                f"frame_count={unit.frame_count}"
            )
        lines.append("")

    lines.append("3. Quick interpretation")
    lines.append(
        "- Compare small single-message HTTP and gRPC to see how protocol overhead changes payload efficiency."
    )
    lines.append(
        "- Compare small and large single-message HTTP to see when frame/segment fragmentation appears."
    )
    lines.append(
        "- Compare sequence per_message vs batched vs nagle_like to show how aggregating small messages can reduce transfer overhead."
    )

    return "\n".join(lines)


def main() -> None:
    scenarios = build_demo_scenarios()
    raw_output = build_raw_output(scenarios)
    text_report = build_text_report(scenarios)

    with RAW_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(raw_output, f, indent=2)

    with TEXT_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        f.write(text_report)

    print(f"Raw demo output saved to: {RAW_OUTPUT_PATH}")
    print(f"Text demo report saved to: {TEXT_OUTPUT_PATH}")
    print()
    print(text_report)


if __name__ == "__main__":
    main()