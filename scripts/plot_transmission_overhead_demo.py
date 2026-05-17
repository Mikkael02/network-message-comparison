from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import matplotlib.pyplot as plt


CSV_INPUT_PATH = Path("results/processed/transmission_overhead_demo_summary.csv")
OUTPUT_DIR = Path("results/processed")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def load_rows(path: Path) -> list[dict]:
    if not path.exists():
        raise FileNotFoundError(f"Summary CSV file not found: {path}")

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    for row in rows:
        row["total_transmitted_bytes"] = int(row["total_transmitted_bytes"])
        row["payload_size_bytes"] = int(row["payload_size_bytes"])
        row["serialized_payload_size_bytes"] = int(row["serialized_payload_size_bytes"])
        row["frame_count"] = int(row["frame_count"])
        row["fragmentation_occurred"] = int(row["fragmentation_occurred"])
        row["payload_efficiency_ratio"] = float(row["payload_efficiency_ratio"])
        row["required_bitrate_kbps"] = float(row["required_bitrate_kbps"])

    return rows


def filter_rows(rows: list[dict], category: str) -> list[dict]:
    return [row for row in rows if row["category"] == category]


def plot_metric(rows: list[dict], category: str, metric: str, ylabel: str, output_path: Path) -> None:
    sorted_rows = sorted(rows, key=lambda x: x[metric])

    labels = [row["scenario_name"] for row in sorted_rows]
    values = [row[metric] for row in sorted_rows]

    plt.figure(figsize=(10, 5))
    plt.bar(labels, values)
    plt.title(f"{category} - {metric}")
    plt.xlabel("Scenario")
    plt.ylabel(ylabel)
    plt.xticks(rotation=25, ha="right")
    plt.tight_layout()
    plt.savefig(output_path, dpi=150)
    plt.close()


def main() -> None:
    rows = load_rows(CSV_INPUT_PATH)

    metrics = [
        ("total_transmitted_bytes", "Bytes"),
        ("payload_efficiency_ratio", "Ratio"),
        ("frame_count", "Count"),
        ("required_bitrate_kbps", "kbps"),
    ]

    for category in ["single_message", "sequence"]:
        category_rows = filter_rows(rows, category)

        for metric, ylabel in metrics:
            output_path = OUTPUT_DIR / f"{category}_{metric}.png"
            plot_metric(category_rows, category, metric, ylabel, output_path)
            print(f"Saved chart: {output_path}")


if __name__ == "__main__":
    main()