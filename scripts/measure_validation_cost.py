from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse

from app.experiments.models import (
    ValidationExperimentConfig,
    ValidationScenario,
)
from app.experiments.validation import (
    run_validation_experiment,
    save_validation_experiment_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run validation cost experiment."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=5000,
        help="Number of iterations per scenario.",
    )
    parser.add_argument(
        "--scenarios",
        nargs="+",
        default=[
            "baseline_valid_dict",
            "structural_validation_valid_set",
            "full_validation_valid_set",
            "structural_validation_invalid",
            "business_validation_invalid",
        ],
        help="Validation scenarios to measure.",
    )
    parser.add_argument(
        "--output",
        default="results/raw/validation_cost.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--source",
        default="validation_benchmark_client",
    )
    parser.add_argument(
        "--valid-resource-id",
        default="validation_valid_set",
    )
    parser.add_argument(
        "--readonly-resource-id",
        default="readonly_validation_target",
    )
    parser.add_argument(
        "--valid-value",
        type=int,
        default=42,
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = ValidationExperimentConfig(
        scenarios=[ValidationScenario(value) for value in args.scenarios],
        iterations=args.iterations,
        source=args.source,
        valid_resource_id=args.valid_resource_id,
        readonly_resource_id=args.readonly_resource_id,
        valid_value=args.valid_value,
    )

    results = run_validation_experiment(config)
    output_path = Path(args.output)
    save_validation_experiment_results(results, output_path)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()