from pathlib import Path

import pytest

from app.experiments.storage import (
    read_saved_run,
    save_experiment_run,
)


def test_read_saved_run_returns_metadata_and_results(tmp_path: Path):
    results = {
        "iterations": 5,
        "measurements": [{"name": "demo"}],
    }

    metadata = save_experiment_run(
        experiment_name="validation",
        results=results,
        run_label="reader_test",
        base_dir=tmp_path,
    )

    detail = read_saved_run(metadata.run_id, base_dir=tmp_path)

    assert detail.metadata.run_id == metadata.run_id
    assert detail.metadata.experiment_name == "validation"
    assert detail.results["iterations"] == 5
    assert len(detail.results["measurements"]) == 1


def test_read_saved_run_raises_for_missing_run(tmp_path: Path):
    with pytest.raises(FileNotFoundError):
        read_saved_run("missing_run_id", base_dir=tmp_path)