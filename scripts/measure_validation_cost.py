from pathlib import Path
import sys

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import csv
import json
import statistics
import time
from datetime import datetime, timezone

from pydantic import ValidationError

from app.core.models.message import MessageEnvelope
from app.core.validation.business import validate_business_rules
from app.core.validation.exceptions import BusinessValidationError


RAW_OUTPUT_PATH = Path("results/raw/validation_cost.json")
CSV_OUTPUT_PATH = Path("results/processed/validation_cost_summary.csv")

RAW_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
CSV_OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

ITERATIONS = 5000


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize_us(values: list[float]) -> dict:
    return {
        "count": len(values),
        "min_us": min(values),
        "max_us": max(values),
        "avg_us": statistics.mean(values),
        "median_us": statistics.median(values),
    }


def baseline_no_validation(payload: dict) -> dict:
    return {
        "source": payload["source"],
        "operation": payload["payload"]["operation"],
        "resource_id": payload["payload"]["resource_id"],
        "value": payload["payload"].get("value"),
    }


def structural_validation(payload: dict) -> MessageEnvelope:
    return MessageEnvelope.model_validate(payload)


def full_validation(payload: dict) -> MessageEnvelope:
    message = MessageEnvelope.model_validate(payload)
    validate_business_rules(message)
    return message


def measure_success_case(name: str, func, payload: dict, iterations: int) -> dict:
    timings_us: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        result = func(payload)
        end = time.perf_counter_ns()

        if result is None:
            raise RuntimeError(f"Scenario {name} returned None unexpectedly")

        timings_us.append((end - start) / 1_000)

    return {
        "scenario": name,
        "expected_outcome": "success",
        "timings_us": timings_us,
        "summary": summarize_us(timings_us),
    }


def measure_expected_exception_case(
    name: str,
    func,
    payload: dict,
    expected_exception: type[Exception],
    iterations: int,
) -> dict:
    timings_us: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        try:
            func(payload)
            raise RuntimeError(
                f"Scenario {name} did not raise {expected_exception.__name__}"
            )
        except expected_exception:
            end = time.perf_counter_ns()
            timings_us.append((end - start) / 1_000)

    return {
        "scenario": name,
        "expected_outcome": expected_exception.__name__,
        "timings_us": timings_us,
        "summary": summarize_us(timings_us),
    }


def flatten_for_csv(results: list[dict]) -> list[dict]:
    rows = []

    for item in results:
        rows.append(
            {
                "scenario": item["scenario"],
                "expected_outcome": item["expected_outcome"],
                "count": item["summary"]["count"],
                "min_us": item["summary"]["min_us"],
                "max_us": item["summary"]["max_us"],
                "avg_us": item["summary"]["avg_us"],
                "median_us": item["summary"]["median_us"],
            }
        )

    return rows


def save_csv(rows: list[dict], path: Path) -> None:
    fieldnames = [
        "scenario",
        "expected_outcome",
        "count",
        "min_us",
        "max_us",
        "avg_us",
        "median_us",
    ]

    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    valid_set_payload = {
        "source": "validation_client",
        "payload": {
            "operation": "set_value",
            "resource_id": "sensor_01",
            "value": 42,
        },
    }

    invalid_structural_payload = {
        "source": "validation_client",
        "payload": {
            "operation": "set_value",
            "resource_id": "",
            "value": 42,
        },
    }

    invalid_business_payload = {
        "source": "validation_client",
        "payload": {
            "operation": "set_value",
            "resource_id": "readonly_sensor",
            "value": 42,
        },
    }

    started_at = now_utc_iso()

    results = [
        measure_success_case(
            "baseline_no_validation_valid_set",
            baseline_no_validation,
            valid_set_payload,
            ITERATIONS,
        ),
        measure_success_case(
            "structural_validation_valid_set",
            structural_validation,
            valid_set_payload,
            ITERATIONS,
        ),
        measure_success_case(
            "full_validation_valid_set",
            full_validation,
            valid_set_payload,
            ITERATIONS,
        ),
        measure_expected_exception_case(
            "structural_validation_invalid_set",
            structural_validation,
            invalid_structural_payload,
            ValidationError,
            ITERATIONS,
        ),
        measure_expected_exception_case(
            "full_validation_invalid_business_set",
            full_validation,
            invalid_business_payload,
            BusinessValidationError,
            ITERATIONS,
        ),
    ]

    raw_output = {
        "started_at": started_at,
        "iterations": ITERATIONS,
        "measurements": results,
        "finished_at": now_utc_iso(),
    }

    with RAW_OUTPUT_PATH.open("w", encoding="utf-8") as f:
        json.dump(raw_output, f, indent=2)

    csv_rows = flatten_for_csv(results)
    save_csv(csv_rows, CSV_OUTPUT_PATH)

    print(f"Raw results saved to: {RAW_OUTPUT_PATH}")
    print(f"CSV summary saved to: {CSV_OUTPUT_PATH}")
    print()

    for item in results:
        summary = item["summary"]
        print(
            f"{item['scenario']}: "
            f"avg={summary['avg_us']:.3f} us, "
            f"median={summary['median_us']:.3f} us, "
            f"min={summary['min_us']:.3f} us, "
            f"max={summary['max_us']:.3f} us"
        )


if __name__ == "__main__":
    main()