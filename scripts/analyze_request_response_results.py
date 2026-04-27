from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json


RAW_RESULTS_PATH = Path("results/raw/request_response_external.json")
PROCESSED_DIR = Path("results/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CSV_OUTPUT_PATH = PROCESSED_DIR / "request_response_summary.csv"
TEXT_OUTPUT_PATH = PROCESSED_DIR / "request_response_summary.txt"
JSON_OUTPUT_PATH = PROCESSED_DIR / "request_response_summary.json"


def load_raw_results(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Raw results file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_measurements(raw_data: dict) -> list[dict]:
    rows = []

    for measurement in raw_data["measurements"]:
        transport = measurement["transport"]

        for operation_name in ["set_value", "get_value"]:
            summary = measurement[operation_name]["summary"]

            rows.append(
                {
                    "transport": transport,
                    "operation": operation_name,
                    "count": summary["count"],
                    "min_ms": summary["min_ms"],
                    "max_ms": summary["max_ms"],
                    "avg_ms": summary["avg_ms"],
                    "median_ms": summary["median_ms"],
                }
            )

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "transport",
        "operation",
        "count",
        "min_ms",
        "max_ms",
        "avg_ms",
        "median_ms",
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
    lines.append("REQUEST-RESPONSE EXTERNAL MEASUREMENT SUMMARY")
    lines.append("")

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["operation"], []).append(row)

    for operation, operation_rows in grouped.items():
        lines.append(f"Operation: {operation}")

        sorted_by_avg = sorted(operation_rows, key=lambda x: x["avg_ms"])
        best = sorted_by_avg[0]

        for row in sorted_by_avg:
            lines.append(
                f"- {row['transport']}: "
                f"avg={row['avg_ms']:.3f} ms, "
                f"median={row['median_ms']:.3f} ms, "
                f"min={row['min_ms']:.3f} ms, "
                f"max={row['max_ms']:.3f} ms, "
                f"count={row['count']}"
            )

        lines.append(
            f"Best average result for {operation}: "
            f"{best['transport']} ({best['avg_ms']:.3f} ms)"
        )
        lines.append("")

    return "\n".join(lines)


def save_text_report(report: str, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(report)


def main() -> None:
    raw_data = load_raw_results(RAW_RESULTS_PATH)
    rows = flatten_measurements(raw_data)

    save_csv(rows, CSV_OUTPUT_PATH)
    save_json(rows, JSON_OUTPUT_PATH)

    report = build_text_report(rows)
    save_text_report(report, TEXT_OUTPUT_PATH)

    print(f"CSV summary saved to: {CSV_OUTPUT_PATH}")
    print(f"JSON summary saved to: {JSON_OUTPUT_PATH}")
    print(f"Text report saved to: {TEXT_OUTPUT_PATH}")
    print()
    print(report)


if __name__ == "__main__":
    main()