from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json


RAW_INPUT_PATH = Path("results/raw/transmission_overhead_demo.json")
PROCESSED_DIR = Path("results/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CSV_OUTPUT_PATH = PROCESSED_DIR / "transmission_overhead_demo_summary.csv"
TEXT_OUTPUT_PATH = PROCESSED_DIR / "transmission_overhead_demo_summary.txt"
JSON_OUTPUT_PATH = PROCESSED_DIR / "transmission_overhead_demo_summary.json"


def load_raw_results(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Raw results file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_measurements(raw_data: dict) -> list[dict]:
    rows = []

    for item in raw_data["single_message"]:
        scenario_name = item["scenario_name"]
        result = item["result"]

        rows.append(
            {
                "category": "single_message",
                "scenario_name": scenario_name,
                "total_transmitted_bytes": result["layer_breakdown"]["total_transmitted_bytes"],
                "payload_size_bytes": result["layer_breakdown"]["payload_size_bytes"],
                "serialized_payload_size_bytes": result["serialized_payload_size_bytes"],
                "frame_count": result["frame_analysis"]["frame_count"],
                "fragmentation_occurred": int(result["frame_analysis"]["fragmentation_occurred"]),
                "payload_efficiency_ratio": result["efficiency"]["payload_efficiency_ratio"],
                "required_bitrate_kbps": result["efficiency"]["required_bitrate_kbps"],
            }
        )

    for item in raw_data["sequence"]:
        scenario_name = item["scenario_name"]
        result = item["result"]

        rows.append(
            {
                "category": "sequence",
                "scenario_name": scenario_name,
                "total_transmitted_bytes": result["total_transmitted_bytes"],
                "payload_size_bytes": result["total_original_payload_bytes"],
                "serialized_payload_size_bytes": result["total_serialized_payload_bytes"],
                "frame_count": result["total_frame_count"],
                "fragmentation_occurred": 0,
                "payload_efficiency_ratio": result["payload_efficiency_ratio"],
                "required_bitrate_kbps": result["required_bitrate_kbps"],
            }
        )

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "category",
        "scenario_name",
        "total_transmitted_bytes",
        "payload_size_bytes",
        "serialized_payload_size_bytes",
        "frame_count",
        "fragmentation_occurred",
        "payload_efficiency_ratio",
        "required_bitrate_kbps",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def build_text_report(rows: list[dict]) -> str:
    lines = []
    lines.append("TRANSMISSION OVERHEAD DEMO SUMMARY")
    lines.append("")

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["category"], []).append(row)

    for category, category_rows in grouped.items():
        lines.append(f"Category: {category}")

        by_transfer = sorted(category_rows, key=lambda x: x["total_transmitted_bytes"])
        by_efficiency = sorted(category_rows, key=lambda x: x["payload_efficiency_ratio"], reverse=True)

        lines.append("Sorted by total transmitted bytes:")
        for row in by_transfer:
            lines.append(
                f"- {row['scenario_name']}: "
                f"total_transmitted_bytes={row['total_transmitted_bytes']}, "
                f"frame_count={row['frame_count']}, "
                f"payload_efficiency_ratio={row['payload_efficiency_ratio']:.4f}, "
                f"required_bitrate_kbps={row['required_bitrate_kbps']:.4f}"
            )

        lines.append("")
        lines.append("Best payload efficiency:")
        best_efficiency = by_efficiency[0]
        lines.append(
            f"- {best_efficiency['scenario_name']} "
            f"({best_efficiency['payload_efficiency_ratio']:.4f})"
        )
        lines.append("")

    return "\n".join(lines)


def save_text(report: str, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(report)


def main() -> None:
    raw_data = load_raw_results(RAW_INPUT_PATH)
    rows = flatten_measurements(raw_data)

    save_csv(rows, CSV_OUTPUT_PATH)
    save_json(rows, JSON_OUTPUT_PATH)

    report = build_text_report(rows)
    save_text(report, TEXT_OUTPUT_PATH)

    print(f"CSV summary saved to: {CSV_OUTPUT_PATH}")
    print(f"JSON summary saved to: {JSON_OUTPUT_PATH}")
    print(f"Text report saved to: {TEXT_OUTPUT_PATH}")
    print()
    print(report)


if __name__ == "__main__":
    main()