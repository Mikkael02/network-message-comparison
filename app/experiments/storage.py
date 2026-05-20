from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import json
import re
import uuid

from app.experiments.models import (
    SavedExperimentRunMetadata,
    SavedExperimentRunsResponse,
)


PROJECT_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_RUNS_DIR = PROJECT_ROOT / "results" / "runs"
DEFAULT_INDEX_PATH = DEFAULT_RUNS_DIR / "index.json"


def now_utc_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def normalize_run_label(run_label: str | None) -> str | None:
    if run_label is None:
        return None

    normalized = run_label.strip().lower()
    if not normalized:
        return None

    normalized = re.sub(r"[^a-z0-9_-]+", "_", normalized)
    normalized = re.sub(r"_+", "_", normalized).strip("_")

    return normalized or None


def build_run_id(experiment_name: str) -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
    short_uuid = uuid.uuid4().hex[:8]
    return f"{experiment_name}_{timestamp}_{short_uuid}"


def ensure_runs_storage(base_dir: Path = DEFAULT_RUNS_DIR) -> None:
    base_dir.mkdir(parents=True, exist_ok=True)


def load_run_index(index_path: Path = DEFAULT_INDEX_PATH) -> list[dict]:
    if not index_path.exists():
        return []

    with index_path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    if not isinstance(data, list):
        raise ValueError("Run index file must contain a list")

    return data


def save_run_index(entries: list[dict], index_path: Path = DEFAULT_INDEX_PATH) -> None:
    index_path.parent.mkdir(parents=True, exist_ok=True)
    with index_path.open("w", encoding="utf-8") as f:
        json.dump(entries, f, indent=2)


def build_stored_file_path(output_path: Path, base_dir: Path) -> str:
    try:
        return str(output_path.relative_to(PROJECT_ROOT)).replace("\\", "/")
    except ValueError:
        try:
            return str(output_path.relative_to(base_dir)).replace("\\", "/")
        except ValueError:
            return str(output_path).replace("\\", "/")


def save_experiment_run(
    experiment_name: str,
    results: dict,
    run_label: str | None = None,
    base_dir: Path = DEFAULT_RUNS_DIR,
) -> SavedExperimentRunMetadata:
    ensure_runs_storage(base_dir)

    normalized_label = normalize_run_label(run_label)
    saved_at = now_utc_iso()
    run_id = build_run_id(experiment_name)

    experiment_dir = base_dir / experiment_name
    experiment_dir.mkdir(parents=True, exist_ok=True)

    filename = run_id
    if normalized_label:
        filename += f"_{normalized_label}"
    filename += ".json"

    output_path = experiment_dir / filename

    metadata = SavedExperimentRunMetadata(
        run_id=run_id,
        experiment_name=experiment_name,
        saved_at=saved_at,
        run_label=normalized_label,
        file_path=build_stored_file_path(output_path, base_dir),
    )

    payload = {
        "metadata": metadata.model_dump(mode="json"),
        "results": results,
    }

    with output_path.open("w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2)

    index_path = base_dir / "index.json"
    entries = load_run_index(index_path)
    entries.append(metadata.model_dump(mode="json"))
    entries.sort(key=lambda item: item["saved_at"], reverse=True)
    save_run_index(entries, index_path)

    return metadata


def list_saved_runs(
    limit: int = 20,
    experiment_name: str | None = None,
    base_dir: Path = DEFAULT_RUNS_DIR,
) -> SavedExperimentRunsResponse:
    ensure_runs_storage(base_dir)

    index_path = base_dir / "index.json"
    entries = load_run_index(index_path)

    if experiment_name is not None:
        entries = [
            entry for entry in entries if entry["experiment_name"] == experiment_name
        ]

    entries.sort(key=lambda item: item["saved_at"], reverse=True)
    selected = entries[:limit]

    return SavedExperimentRunsResponse(
        total_count=len(entries),
        runs=[SavedExperimentRunMetadata(**entry) for entry in selected],
    )