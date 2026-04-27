from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json


CSV_INPUT_PATH = Path("results/processed/validation_cost_summary.csv")
TEXT_OUTPUT_PATH = Path("results/processed/validation_cost_summary.txt")
JSON_OUTPUT_PATH = Path("results/processed/validation_cost_summary.json")


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"CSV file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        row["count"] = int(row["count"])
        row["min_us"] = float(row["min_us"])
        row["max_us"] = float(row["max_us"])
        row["avg_us"] = float(row["avg_us"])
        row["median_us"] = float(row["median_us"])

    return rows


def save_json(rows: list[dict], path: Path) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(rows, f, indent=2)


def build_report(rows: list[dict]) -> str:
    lines = []
    lines.append("VALIDATION COST SUMMARY")
    lines.append("")

    sorted_by_avg = sorted(rows, key=lambda x: x["avg_us"])

    lines.append("Scenarios sorted by average execution time:")
    for row in sorted_by_avg:
        lines.append(
            f"- {row['scenario']} "
            f"(expected: {row['expected_outcome']}): "
            f"avg={row['avg_us']:.3f} us, "
            f"median={row['median_us']:.3f} us, "
            f"min={row['min_us']:.3f} us, "
            f"max={row['max_us']:.3f} us, "
            f"count={row['count']}"
        )

    lines.append("")

    scenario_map = {row["scenario"]: row for row in rows}

    baseline = scenario_map["baseline_no_validation_valid_set"]
    structural = scenario_map["structural_validation_valid_set"]
    full_valid = scenario_map["full_validation_valid_set"]
    invalid_structural = scenario_map["structural_validation_invalid_set"]
    invalid_business = scenario_map["full_validation_invalid_business_set"]

    structural_over_baseline = structural["avg_us"] - baseline["avg_us"]
    full_over_structural = full_valid["avg_us"] - structural["avg_us"]
    full_over_baseline = full_valid["avg_us"] - baseline["avg_us"]

    lines.append("Key comparisons:")
    lines.append(
        f"- Structural validation adds {structural_over_baseline:.3f} us "
        f"on average over baseline."
    )
    lines.append(
        f"- Business validation adds {full_over_structural:.3f} us "
        f"on average over structural validation."
    )
    lines.append(
        f"- Full validation adds {full_over_baseline:.3f} us "
        f"on average over baseline."
    )
    lines.append(
        f"- Structural rejection average: {invalid_structural['avg_us']:.3f} us."
    )
    lines.append(
        f"- Business rejection average: {invalid_business['avg_us']:.3f} us."
    )

    lines.append("")
    lines.append("Fastest scenario:")
    lines.append(
        f"- {sorted_by_avg[0]['scenario']} ({sorted_by_avg[0]['avg_us']:.3f} us)"
    )

    lines.append("")
    lines.append("Slowest scenario:")
    lines.append(
        f"- {sorted_by_avg[-1]['scenario']} ({sorted_by_avg[-1]['avg_us']:.3f} us)"
    )

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