from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import argparse

from app.experiments.models import (
    ExperimentTransport,
    RequestResponseExperimentConfig,
)
from app.experiments.request_response import (
    run_request_response_experiment,
    save_request_response_experiment_results,
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run request-response external experiment."
    )
    parser.add_argument(
        "--iterations",
        type=int,
        default=50,
        help="Number of iterations per operation and transport.",
    )
    parser.add_argument(
        "--transports",
        nargs="+",
        default=["http", "ws", "grpc"],
        help="Transports to measure. Example: --transports http grpc",
    )
    parser.add_argument(
        "--output",
        default="results/raw/request_response_external.json",
        help="Output JSON path.",
    )
    parser.add_argument(
        "--http-base-url",
        default="http://127.0.0.1:8000",
    )
    parser.add_argument(
        "--ws-url",
        default="ws://127.0.0.1:8001/ws/process",
    )
    parser.add_argument(
        "--grpc-address",
        default="127.0.0.1:50051",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    config = RequestResponseExperimentConfig(
        transports=[ExperimentTransport(value) for value in args.transports],
        iterations=args.iterations,
        http_base_url=args.http_base_url,
        ws_url=args.ws_url,
        grpc_address=args.grpc_address,
    )

    results = run_request_response_experiment(config)
    output_path = Path(args.output)
    save_request_response_experiment_results(results, output_path)

    print(f"Results saved to: {output_path}")


if __name__ == "__main__":
    main()