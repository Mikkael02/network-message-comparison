from pathlib import Path

import pytest

from app.experiments.models import (
    ValidationExperimentConfig,
    ValidationScenario,
)
from app.experiments.validation import (
    run_validation_experiment,
    save_validation_experiment_results,
)


def test_run_validation_experiment_returns_selected_scenarios():
    config = ValidationExperimentConfig(
        scenarios=[
            ValidationScenario.BASELINE_VALID_DICT,
            ValidationScenario.FULL_VALIDATION_VALID_SET,
        ],
        iterations=3,
        valid_resource_id="validation_valid_set",
        readonly_resource_id="readonly_validation_target",
        valid_value=42,
    )

    result = run_validation_experiment(config)

    assert result["iterations"] == 3
    assert result["scenarios"] == [
        "baseline_valid_dict",
        "full_validation_valid_set",
    ]
    assert len(result["measurements"]) == 2

    for measurement in result["measurements"]:
        assert measurement["summary"]["count"] == 3
        assert len(measurement["timings_us"]) == 3


def test_validation_config_rejects_duplicate_scenarios():
    with pytest.raises(Exception):
        ValidationExperimentConfig(
            scenarios=[
                ValidationScenario.BASELINE_VALID_DICT,
                ValidationScenario.BASELINE_VALID_DICT,
            ]
        )


def test_save_validation_experiment_results_writes_file(tmp_path: Path):
    results = {
        "started_at": "2026-01-01T00:00:00+00:00",
        "finished_at": "2026-01-01T00:00:01+00:00",
        "iterations": 1,
        "scenarios": ["baseline_valid_dict"],
        "measurements": [],
    }

    output_path = tmp_path / "validation_cost.json"
    save_validation_experiment_results(results, output_path)

    assert output_path.exists()
    assert output_path.read_text(encoding="utf-8")