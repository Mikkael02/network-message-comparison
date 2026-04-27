from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json


PROCESSED_DIR = Path("results/processed")

REQUEST_RESPONSE_PATH = PROCESSED_DIR / "request_response_summary.csv"
REALTIME_PATH = PROCESSED_DIR / "realtime_fetch_summary.csv"
MESSAGE_SIZE_PATH = PROCESSED_DIR / "message_size_and_serialization_summary.csv"
VALIDATION_PATH = PROCESSED_DIR / "validation_cost_summary.csv"

OUTPUT_CSV_PATH = PROCESSED_DIR / "combined_research_summary.csv"
OUTPUT_JSON_PATH = PROCESSED_DIR / "combined_research_summary.json"
OUTPUT_TEXT_PATH = PROCESSED_DIR / "combined_research_summary.txt"


def load_csv(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Missing input file: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def to_float(row: dict, keys: list[str]) -> dict:
    converted = dict(row)
    for key in keys:
        if key in converted and converted[key] != "":
            converted[key] = float(converted[key])
    return converted


def to_int(row: dict, keys: list[str]) -> dict:
    converted = dict(row)
    for key in keys:
        if key in converted and converted[key] != "":
            converted[key] = int(float(converted[key]))
    return converted


def normalize_request_response(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        row = to_int(row, ["count"])
        row = to_float(row, ["min_ms", "max_ms", "avg_ms", "median_ms"])
        result.append(
            {
                "category": "request_response",
                "subject": row["operation"],
                "transport": row["transport"],
                "metric_1_name": "avg_ms",
                "metric_1_value": row["avg_ms"],
                "metric_2_name": "median_ms",
                "metric_2_value": row["median_ms"],
                "metric_3_name": "min_ms",
                "metric_3_value": row["min_ms"],
                "metric_4_name": "max_ms",
                "metric_4_value": row["max_ms"],
                "notes": f"count={row['count']}",
            }
        )
    return result


def normalize_realtime(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        row = to_int(row, ["count", "expected_event_count"])
        row = to_float(row, ["min_ms", "max_ms", "avg_ms", "median_ms"])
        result.append(
            {
                "category": "realtime_fetch",
                "subject": row["scenario"],
                "transport": row["transport"],
                "metric_1_name": "avg_ms",
                "metric_1_value": row["avg_ms"],
                "metric_2_name": "median_ms",
                "metric_2_value": row["median_ms"],
                "metric_3_name": "expected_event_count",
                "metric_3_value": row["expected_event_count"],
                "metric_4_name": "max_ms",
                "metric_4_value": row["max_ms"],
                "notes": f"count={row['count']}",
            }
        )
    return result


def normalize_message_size(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        row = to_int(row, ["request_size_bytes", "response_size_bytes"])
        row = to_float(
            row,
            [
                "request_serialize_avg_us",
                "request_deserialize_avg_us",
                "response_serialize_avg_us",
                "response_deserialize_avg_us",
            ],
        )
        result.append(
            {
                "category": "message_size_and_serialization",
                "subject": row["operation"],
                "transport": row["transport"],
                "metric_1_name": "request_size_bytes",
                "metric_1_value": row["request_size_bytes"],
                "metric_2_name": "response_size_bytes",
                "metric_2_value": row["response_size_bytes"],
                "metric_3_name": "request_serialize_avg_us",
                "metric_3_value": row["request_serialize_avg_us"],
                "metric_4_name": "response_serialize_avg_us",
                "metric_4_value": row["response_serialize_avg_us"],
                "notes": f"encoding={row['encoding']}",
            }
        )
    return result


def normalize_validation(rows: list[dict]) -> list[dict]:
    result = []
    for row in rows:
        row = to_int(row, ["count"])
        row = to_float(row, ["min_us", "max_us", "avg_us", "median_us"])
        result.append(
            {
                "category": "validation_cost",
                "subject": row["scenario"],
                "transport": "shared",
                "metric_1_name": "avg_us",
                "metric_1_value": row["avg_us"],
                "metric_2_name": "median_us",
                "metric_2_value": row["median_us"],
                "metric_3_name": "min_us",
                "metric_3_value": row["min_us"],
                "metric_4_name": "max_us",
                "metric_4_value": row["max_us"],
                "notes": f"expected_outcome={row['expected_outcome']}; count={row['count']}",
            }
        )
    return result


def save_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "category",
        "subject",
        "transport",
        "metric_1_name",
        "metric_1_value",
        "metric_2_name",
        "metric_2_value",
        "metric_3_name",
        "metric_3_value",
        "metric_4_name",
        "metric_4_value",
        "notes",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def save_json(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def best_by(rows: list[dict], category: str, subject: str, metric_name: str) -> list[dict]:
    filtered = [
        row for row in rows
        if row["category"] == category
        and row["subject"] == subject
        and row["metric_1_name"] == metric_name
    ]
    return sorted(filtered, key=lambda x: x["metric_1_value"])


def build_text_report(rows: list[dict]) -> str:
    lines = []
    lines.append("COMBINED RESEARCH SUMMARY")
    lines.append("")

    lines.append("1. Request-response")
    for subject in ["set_value", "get_value"]:
        candidates = [
            row for row in rows
            if row["category"] == "request_response" and row["subject"] == subject
        ]
        ordered = sorted(candidates, key=lambda x: x["metric_1_value"])
        lines.append(f"- Operation: {subject}")
        for row in ordered:
            lines.append(
                f"  - {row['transport']}: "
                f"{row['metric_1_name']}={row['metric_1_value']:.3f}, "
                f"{row['metric_2_name']}={row['metric_2_value']:.3f}"
            )
    lines.append("")

    lines.append("2. Realtime fetch")
    for subject in ["non_empty_fetch", "empty_fetch"]:
        candidates = [
            row for row in rows
            if row["category"] == "realtime_fetch" and row["subject"] == subject
        ]
        ordered = sorted(candidates, key=lambda x: x["metric_1_value"])
        lines.append(f"- Scenario: {subject}")
        for row in ordered:
            lines.append(
                f"  - {row['transport']}: "
                f"{row['metric_1_name']}={row['metric_1_value']:.3f}, "
                f"{row['metric_3_name']}={int(row['metric_3_value'])}"
            )
    lines.append("")

    lines.append("3. Message size and serialization")
    for subject in ["set_value", "get_value"]:
        candidates = [
            row for row in rows
            if row["category"] == "message_size_and_serialization" and row["subject"] == subject
        ]
        ordered = sorted(candidates, key=lambda x: x["metric_1_value"])
        lines.append(f"- Operation: {subject}")
        for row in ordered:
            lines.append(
                f"  - {row['transport']}: "
                f"{row['metric_1_name']}={int(row['metric_1_value'])}, "
                f"{row['metric_2_name']}={int(row['metric_2_value'])}, "
                f"{row['notes']}"
            )
    lines.append("")

    lines.append("4. Validation cost")
    candidates = [
        row for row in rows
        if row["category"] == "validation_cost"
    ]
    ordered = sorted(candidates, key=lambda x: x["metric_1_value"])
    for row in ordered:
        lines.append(
            f"- {row['subject']}: "
            f"{row['metric_1_name']}={row['metric_1_value']:.3f}, "
            f"{row['metric_2_name']}={row['metric_2_value']:.3f}, "
            f"{row['notes']}"
        )

    return "\n".join(lines)


def save_text(report: str, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(report)


def main() -> None:
    request_response_rows = normalize_request_response(load_csv(REQUEST_RESPONSE_PATH))
    realtime_rows = normalize_realtime(load_csv(REALTIME_PATH))
    message_rows = normalize_message_size(load_csv(MESSAGE_SIZE_PATH))
    validation_rows = normalize_validation(load_csv(VALIDATION_PATH))

    combined_rows = (
        request_response_rows
        + realtime_rows
        + message_rows
        + validation_rows
    )

    save_csv(combined_rows, OUTPUT_CSV_PATH)
    save_json(combined_rows, OUTPUT_JSON_PATH)

    report = build_text_report(combined_rows)
    save_text(report, OUTPUT_TEXT_PATH)

    print(f"Combined CSV saved to: {OUTPUT_CSV_PATH}")
    print(f"Combined JSON saved to: {OUTPUT_JSON_PATH}")
    print(f"Combined text report saved to: {OUTPUT_TEXT_PATH}")
    print()
    print(report)


if __name__ == "__main__":
    main()