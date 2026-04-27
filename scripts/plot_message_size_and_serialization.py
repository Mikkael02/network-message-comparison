from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import matplotlib.pyplot as plt


CSV_INPUT_PATH = Path("results/processed/message_size_and_serialization_summary.csv")
OUTPUT_DIR = Path("results/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


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


def filter_rows(rows: list[dict], operation: str) -> list[dict]:
    return [row for row in rows if row["operation"] == operation]


def plot_metric(rows: list[dict], operation: str, metric: str, ylabel: str, output_path: Path) -> None:
    sorted_rows = sorted(rows, key=lambda x: x[metric])

    labels = [f"{row['transport']}\n({row['encoding']})" for row in sorted_rows]
    values = [row[metric] for row in sorted_rows]

    plt.figure(figsize=(8, 5))
    plt.bar(labels, values)
    plt.title(f"{operation} - {metric}")
    plt.xlabel("Transport")
    plt.ylabel(ylabel)
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    rows = load_rows(CSV_INPUT_PATH)

    metrics = [
        ("request_size_bytes", "Bytes"),
        ("response_size_bytes", "Bytes"),
        ("request_serialize_avg_us", "Time [us]"),
        ("request_deserialize_avg_us", "Time [us]"),
        ("response_serialize_avg_us", "Time [us]"),
        ("response_deserialize_avg_us", "Time [us]"),
    ]

    for operation in ["set_value", "get_value"]:
        operation_rows = filter_rows(rows, operation)

        for metric, ylabel in metrics:
            output_path = OUTPUT_DIR / f"{operation}_{metric}.png"
            plot_metric(operation_rows, operation, metric, ylabel, output_path)
            print(f"Saved chart: {output_path}")


if __name__ == "__main__":
    main()