from pathlib import Path

from app.experiments.storage import (
    list_saved_runs,
    normalize_run_label,
    save_experiment_run,
)


def test_normalize_run_label_returns_slug_like_value():
    assert normalize_run_label(" My First Run ") == "my_first_run"
    assert normalize_run_label("rr/demo#1") == "rr_demo_1"
    assert normalize_run_label("") is None
    assert normalize_run_label("   ") is None
    assert normalize_run_label(None) is None


def test_save_experiment_run_writes_file_and_index(tmp_path: Path):
    results = {
        "iterations": 5,
        "measurements": [],
    }

    metadata = save_experiment_run(
        experiment_name="request_response",
        results=results,
        run_label="demo run",
        base_dir=tmp_path,
    )

    assert metadata.experiment_name == "request_response"
    assert metadata.run_label == "demo_run"

    saved_files = list((tmp_path / "request_response").glob("*.json"))
    assert len(saved_files) == 1

    index_file = tmp_path / "index.json"
    assert index_file.exists()


def test_list_saved_runs_returns_recent_entries(tmp_path: Path):
    save_experiment_run(
        experiment_name="validation",
        results={"iterations": 1},
        run_label="a",
        base_dir=tmp_path,
    )
    save_experiment_run(
        experiment_name="validation",
        results={"iterations": 2},
        run_label="b",
        base_dir=tmp_path,
    )
    save_experiment_run(
        experiment_name="realtime",
        results={"iterations": 3},
        run_label="c",
        base_dir=tmp_path,
    )

    result = list_saved_runs(
        limit=10,
        experiment_name="validation",
        base_dir=tmp_path,
    )

    assert result.total_count == 2
    assert len(result.runs) == 2
    assert all(run.experiment_name == "validation" for run in result.runs)