from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json


CSV_INPUT_PATH = Path("results/processed/message_size_and_serialization_summary.csv")
TEXT_OUTPUT_PATH = Path("results/processed/message_size_and_serialization_summary.txt")
JSON_OUTPUT_PATH = Path("results/processed/message_size_and_serialization_summary.json")


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        row["request_size_bytes"] = int(row["request_size_bytes"])
        row["response_size_bytes"] = int(row["response_size_bytes"])
        row["request_serialize_avg_us"] = float(row["request_serialize_avg_us"])
        row["request_deserialize_avg_us"] = float(row["request_deserialize_avg_us"])
        row["response_serialize_avg_us"] = float(row["response_serialize_avg_us"])
        row["response_deserialize_avg_us"] = float(row["response_deserialize_avg_us"])

    return rows


def save_json(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def build_report(rows: list[dict]) -> str:
    lines = []
    lines.append("MESSAGE SIZE AND SERIALIZATION SUMMARY")
    lines.append("")

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["operation"], []).append(row)

    for operation, operation_rows in grouped.items():
        lines.append(f"Operation: {operation}")
        lines.append("")

        by_request_size = sorted(operation_rows, key=lambda x: x["request_size_bytes"])
        by_response_size = sorted(operation_rows, key=lambda x: x["response_size_bytes"])
        by_request_serialize = sorted(operation_rows, key=lambda x: x["request_serialize_avg_us"])
        by_response_serialize = sorted(operation_rows, key=lambda x: x["response_serialize_avg_us"])

        lines.append("Request size:")
        for row in by_request_size:
            lines.append(
                f"- {row['transport']} ({row['encoding']}): {row['request_size_bytes']} bytes"
            )
        lines.append(
            f"Smallest request for {operation}: "
            f"{by_request_size[0]['transport']} ({by_request_size[0]['request_size_bytes']} bytes)"
        )
        lines.append("")

        lines.append("Response size:")
        for row in by_response_size:
            lines.append(
                f"- {row['transport']} ({row['encoding']}): {row['response_size_bytes']} bytes"
            )
        lines.append(
            f"Smallest response for {operation}: "
            f"{by_response_size[0]['transport']} ({by_response_size[0]['response_size_bytes']} bytes)"
        )
        lines.append("")

        lines.append("Request serialization average:")
        for row in by_request_serialize:
            lines.append(
                f"- {row['transport']} ({row['encoding']}): {row['request_serialize_avg_us']:.3f} us"
            )
        lines.append(
            f"Fastest request serialization for {operation}: "
            f"{by_request_serialize[0]['transport']} "
            f"({by_request_serialize[0]['request_serialize_avg_us']:.3f} us)"
        )
        lines.append("")

        lines.append("Response serialization average:")
        for row in by_response_serialize:
            lines.append(
                f"- {row['transport']} ({row['encoding']}): {row['response_serialize_avg_us']:.3f} us"
            )
        lines.append(
            f"Fastest response serialization for {operation}: "
            f"{by_response_serialize[0]['transport']} "
            f"({by_response_serialize[0]['response_serialize_avg_us']:.3f} us)"
        )
        lines.append("")
        lines.append("-" * 60)
        lines.append("")

    return "\n".join(lines)


def save_text(report: str, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(report)


def main() -> None:
    rows = load_rows(CSV_INPUT_PATH)
    save_json(rows, JSON_OUTPUT_PATH)

    report = build_report(rows)
    save_text(report, TEXT_OUTPUT_PATH)

    print(f"JSON summary saved to: {JSON_OUTPUT_PATH}")
    print(f"Text report saved to: {TEXT_OUTPUT_PATH}")
    print()
    print(report)


if __name__ == "__main__":
    main()