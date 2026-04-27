from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import matplotlib.pyplot as plt


CSV_INPUT_PATH = Path("results/processed/validation_cost_summary.csv")
OUTPUT_DIR = Path("results/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def plot_metric(rows: list[dict], metric: str, output_path: Path) -> None:
    sorted_rows = sorted(rows, key=lambda x: x[metric])

    labels = [row["scenario"] for row in sorted_rows]
    values = [row[metric] for row in sorted_rows]

    plt.figure(figsize=(11, 6))
    plt.bar(labels, values)
    plt.title(f"Validation cost - {metric}")
    plt.xlabel("Scenario")
    plt.ylabel("Time [us]")
    plt.xticks(rotation=30, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    rows = load_rows(CSV_INPUT_PATH)

    avg_output = OUTPUT_DIR / "validation_cost_avg_us.png"
    median_output = OUTPUT_DIR / "validation_cost_median_us.png"

    plot_metric(rows, "avg_us", avg_output)
    plot_metric(rows, "median_us", median_output)

    print(f"Saved chart: {avg_output}")
    print(f"Saved chart: {median_output}")


if __name__ == "__main__":
    main()