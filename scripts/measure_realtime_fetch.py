from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse

from app.experiments.models import (
    ExperimentTransport,
    RealtimeFetchExperimentConfig,
)
from app.experiments.realtime import (
    run_realtime_fetch_experiment,
    save_realtime_fetch_experiment_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run realtime fetch external experiment."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of iterations per scenario and transport.",
    )
    parser.add_argument(
        "--transports",
        nargs="+",
        default=["http", "ws", "grpc"],
        help="Transports to measure. Example: --transports http ws",
    )
    parser.add_argument(
        "--output",
        default="results/raw/realtime_fetch_external.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--http-base-url",
        default="http://127.0.0.1:8000",
    )
    parser.add_argument(
        "--ws-changes-url",
        default="ws://127.0.0.1:8001/ws/changes",
    )
    parser.add_argument(
        "--ws-process-url",
        default="ws://127.0.0.1:8001/ws/process",
    )
    parser.add_argument(
        "--grpc-address",
        default="127.0.0.1:50051",
    )
    parser.add_argument(
        "--resource-prefix",
        default="realtime_benchmark",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = RealtimeFetchExperimentConfig(
        transports=[ExperimentTransport(value) for value in args.transports],
        iterations=args.iterations,
        http_base_url=args.http_base_url,
        ws_changes_url=args.ws_changes_url,
        ws_process_url=args.ws_process_url,
        grpc_address=args.grpc_address,
        resource_prefix=args.resource_prefix,
    )

    results = run_realtime_fetch_experiment(config)
    output_path = Path(args.output)
    save_realtime_fetch_experiment_results(results, output_path)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()