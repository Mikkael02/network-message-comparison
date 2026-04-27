from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import matplotlib.pyplot as plt


CSV_INPUT_PATH = Path("results/processed/request_response_summary.csv")
OUTPUT_DIR = Path("results/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Summary CSV file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        row["count"] = int(row["count"])
        row["min_ms"] = float(row["min_ms"])
        row["max_ms"] = float(row["max_ms"])
        row["avg_ms"] = float(row["avg_ms"])
        row["median_ms"] = float(row["median_ms"])

    return rows


def filter_rows(rows: list[dict], operation: str) -> list[dict]:
    return [row for row in rows if row["operation"] == operation]


def plot_metric(rows: list[dict], operation: str, metric: str, output_path: Path) -> None:
    sorted_rows = sorted(rows, key=lambda x: x[metric])

    transports = [row["transport"] for row in sorted_rows]
    values = [row[metric] for row in sorted_rows]

    plt.figure(figsize=(8, 5))
    plt.bar(transports, values)
    plt.title(f"{operation} - {metric}")
    plt.xlabel("Transport")
    plt.ylabel("Time [ms]")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    rows = load_rows(CSV_INPUT_PATH)

    for operation in ["set_value", "get_value"]:
        operation_rows = filter_rows(rows, operation)

        avg_output = OUTPUT_DIR / f"{operation}_avg_ms.png"
        median_output = OUTPUT_DIR / f"{operation}_median_ms.png"

        plot_metric(operation_rows, operation, "avg_ms", avg_output)
        plot_metric(operation_rows, operation, "median_ms", median_output)

        print(f"Saved chart: {avg_output}")
        print(f"Saved chart: {median_output}")


if __name__ == "__main__":
    main()