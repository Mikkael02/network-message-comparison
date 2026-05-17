from pathlib import Path
import json

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from app.overhead.calculators import (
    calculate_sequence_overhead,
    calculate_single_message_overhead,
)
from app.overhead.models import (
    SequencePatternInput,
    SequenceTransmissionAnalysisResult,
    TransmissionAnalysisInput,
    TransmissionAnalysisResult,
)
from app.overhead.presets import (
    DEFAULT_LAYER_PRESETS,
    DEFAULT_PROTOCOL_PRESETS,
)


class PresetsResponse(BaseModel):
    layer_presets: dict
    protocol_presets: dict


BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "frontend" / "static"
PROJECT_ROOT = BASE_DIR.parent
RESULTS_DIR = PROJECT_ROOT / "results" / "processed"

REPORT_FILE_MAP = {
    "request-response": "request_response_summary.json",
    "realtime-fetch": "realtime_fetch_summary.json",
    "message-size": "message_size_and_serialization_summary.json",
    "validation-cost": "validation_cost_summary.json",
    "combined": "combined_research_summary.json",
    "interpretation": "interpretation_notes.txt",
    "overhead-demo": "transmission_overhead_demo_summary.json",
}


app = FastAPI(
    title="Transmission Overhead Analysis API",
    version="0.1.0",
)

app.mount("/static", StaticFiles(directory=FRONTEND_DIR), name="static")


@app.get("/", include_in_schema=False)
def frontend_index():
    return FileResponse(FRONTEND_DIR / "index.html")


@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/presets", response_model=PresetsResponse)
def get_presets() -> PresetsResponse:
    return PresetsResponse(
        layer_presets={
            key: preset.model_dump(mode="json")
            for key, preset in DEFAULT_LAYER_PRESETS.items()
        },
        protocol_presets={
            key.value: preset.model_dump(mode="json")
            for key, preset in DEFAULT_PROTOCOL_PRESETS.items()
        },
    )


@app.post("/analyze/single", response_model=TransmissionAnalysisResult)
def analyze_single_message(
    input_data: TransmissionAnalysisInput,
) -> TransmissionAnalysisResult:
    return calculate_single_message_overhead(input_data)


@app.post("/analyze/sequence", response_model=SequenceTransmissionAnalysisResult)
def analyze_sequence(
    input_data: SequencePatternInput,
) -> SequenceTransmissionAnalysisResult:
    return calculate_sequence_overhead(input_data)


@app.get("/reports/available")
def get_available_reports() -> dict:
    reports = []

    for report_key, filename in REPORT_FILE_MAP.items():
        path = RESULTS_DIR / filename
        reports.append(
            {
                "key": report_key,
                "filename": filename,
                "exists": path.exists(),
            }
        )

    return {"reports": reports}


@app.get("/reports/{report_key}")
def get_report(report_key: str):
    if report_key not in REPORT_FILE_MAP:
        raise HTTPException(status_code=404, detail="Report key not found")

    path = RESULTS_DIR / REPORT_FILE_MAP[report_key]
    if not path.exists():
        raise HTTPException(status_code=404, detail="Report file not found")

    if path.suffix == ".json":
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)

    if path.suffix == ".txt":
        with path.open("r", encoding="utf-8") as f:
            return {"content": f.read()}

    raise HTTPException(status_code=400, detail="Unsupported report format")