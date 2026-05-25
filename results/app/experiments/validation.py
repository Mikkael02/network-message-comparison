from datetime import datetime, timezone
from pathlib import Path
import json
import statistics
import time

from pydantic import ValidationError

from app.core.models.message import MessageEnvelope
from app.core.validation.business import validate_business_rules
from app.core.validation.exceptions import BusinessValidationError
from app.experiments.models import (
    ValidationExperimentConfig,
    ValidationScenario,
)


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def summarize(timings_us: list[float]) -> dict:
    return {
        "count": len(timings_us),
        "min_us": min(timings_us),
        "max_us": max(timings_us),
        "avg_us": statistics.mean(timings_us),
        "median_us": statistics.median(timings_us),
    }


def build_valid_set_payload(config: ValidationExperimentConfig) -> dict:
    return {
        "source": config.source,
        "payload": {
            "operation": "set_value",
            "resource_id": config.valid_resource_id,
            "value": config.valid_value,
        },
    }


def build_structural_invalid_payload(config: ValidationExperimentConfig) -> dict:
    return {
        "source": config.source,
        "payload": {
            "operation": "set_value",
            "resource_id": "",
            "value": config.valid_value,
        },
    }


def build_business_invalid_payload(config: ValidationExperimentConfig) -> dict:
    return {
        "source": config.source,
        "payload": {
            "operation": "set_value",
            "resource_id": config.readonly_resource_id,
            "value": config.valid_value,
        },
    }


def baseline_access_valid_dict(payload: dict) -> None:
    _ = payload["source"]
    inner = payload["payload"]
    _ = inner["operation"]
    _ = inner["resource_id"]
    _ = inner["value"]


def structural_validation_valid_set(payload: dict) -> None:
    MessageEnvelope.model_validate(payload)


def full_validation_valid_set(payload: dict) -> None:
    envelope = MessageEnvelope.model_validate(payload)
    validate_business_rules(envelope)


def structural_validation_invalid(payload: dict) -> None:
    try:
        MessageEnvelope.model_validate(payload)
        raise RuntimeError("Expected structural validation error was not raised")
    except ValidationError:
        return


def business_validation_invalid(payload: dict) -> None:
    envelope = MessageEnvelope.model_validate(payload)
    try:
        validate_business_rules(envelope)
        raise RuntimeError("Expected business validation error was not raised")
    except BusinessValidationError:
        return


SCENARIO_RUNNERS = {
    ValidationScenario.BASELINE_VALID_DICT: (
        baseline_access_valid_dict,
        "success",
    ),
    ValidationScenario.STRUCTURAL_VALIDATION_VALID_SET: (
        structural_validation_valid_set,
        "success",
    ),
    ValidationScenario.FULL_VALIDATION_VALID_SET: (
        full_validation_valid_set,
        "success",
    ),
    ValidationScenario.STRUCTURAL_VALIDATION_INVALID: (
        structural_validation_invalid,
        "structural_validation_error",
    ),
    ValidationScenario.BUSINESS_VALIDATION_INVALID: (
        business_validation_invalid,
        "business_validation_error",
    ),
}


def measure_scenario(function, payload: dict, iterations: int) -> list[float]:
    timings_us: list[float] = []

    for _ in range(iterations):
        start = time.perf_counter_ns()
        function(payload)
        end = time.perf_counter_ns()

        timings_us.append((end - start) / 1_000)

    return timings_us


def run_validation_experiment(
    config: ValidationExperimentConfig,
) -> dict:
    started_at = now_utc_iso()

    valid_payload = build_valid_set_payload(config)
    structural_invalid_payload = build_structural_invalid_payload(config)
    business_invalid_payload = build_business_invalid_payload(config)

    payload_map = {
        ValidationScenario.BASELINE_VALID_DICT: valid_payload,
        ValidationScenario.STRUCTURAL_VALIDATION_VALID_SET: valid_payload,
        ValidationScenario.FULL_VALIDATION_VALID_SET: valid_payload,
        ValidationScenario.STRUCTURAL_VALIDATION_INVALID: structural_invalid_payload,
        ValidationScenario.BUSINESS_VALIDATION_INVALID: business_invalid_payload,
    }

    results = {
        "started_at": started_at,
        "iterations": config.iterations,
        "scenarios": [scenario.value for scenario in config.scenarios],
        "measurements": [],
    }

    for scenario in config.scenarios:
        runner, expected_outcome = SCENARIO_RUNNERS[scenario]
        payload = payload_map[scenario]

        timings_us = measure_scenario(runner, payload, config.iterations)

        results["measurements"].append(
            {
                "scenario": scenario.value,
                "expected_outcome": expected_outcome,
                "timings_us": timings_us,
                "summary": summarize(timings_us),
            }
        )

    results["finished_at"] = now_utc_iso()
    return results


def save_validation_experiment_results(
    results: dict,
    output_path: Path,
) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)