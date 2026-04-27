from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json


RAW_INPUT_PATH = Path("results/raw/realtime_fetch_external.json")
PROCESSED_DIR = Path("results/processed")
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

CSV_OUTPUT_PATH = PROCESSED_DIR / "realtime_fetch_summary.csv"
TEXT_OUTPUT_PATH = PROCESSED_DIR / "realtime_fetch_summary.txt"
JSON_OUTPUT_PATH = PROCESSED_DIR / "realtime_fetch_summary.json"


def load_raw_results(path: Path) -> dict:
    if not path.exists():
        raise FileNotFoundError(f"Raw results file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def flatten_measurements(raw_data: dict) -> list[dict]:
    rows = []

    for measurement in raw_data["measurements"]:
        summary = measurement["summary"]

        rows.append(
            {
                "transport": measurement["transport"],
                "scenario": measurement["scenario"],
                "count": summary["count"],
                "min_ms": summary["min_ms"],
                "max_ms": summary["max_ms"],
                "avg_ms": summary["avg_ms"],
                "median_ms": summary["median_ms"],
                "expected_event_count": measurement["expected_event_count"],
            }
        )

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "transport",
        "scenario",
        "count",
        "min_ms",
        "max_ms",
        "avg_ms",
        "median_ms",
        "expected_event_count",
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
    lines.append("REALTIME FETCH EXTERNAL MEASUREMENT SUMMARY")
    lines.append("")

    grouped: dict[str, list[dict]] = {}
    for row in rows:
        grouped.setdefault(row["scenario"], []).append(row)

    for scenario, scenario_rows in grouped.items():
        lines.append(f"Scenario: {scenario}")

        sorted_by_avg = sorted(scenario_rows, key=lambda x: x["avg_ms"])
        best = sorted_by_avg[0]

        for row in sorted_by_avg:
            lines.append(
                f"- {row['transport']}: "
                f"avg={row['avg_ms']:.3f} ms, "
                f"median={row['median_ms']:.3f} ms, "
                f"min={row['min_ms']:.3f} ms, "
                f"max={row['max_ms']:.3f} ms, "
                f"count={row['count']}, "
                f"expected_event_count={row['expected_event_count']}"
            )

        lines.append(
            f"Best average result for {scenario}: "
            f"{best['transport']} ({best['avg_ms']:.3f} ms)"
        )
        lines.append("")

    return "\n".join(lines)


def save_text_report(report: str, path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        f.write(report)


def main() -> None:
    raw_data = load_raw_results(RAW_INPUT_PATH)
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