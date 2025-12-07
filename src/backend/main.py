from __future__ import annotations

from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from src.backend.metrics import compute_wellness_summary, load_health_data

DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "mock_health_metrics.csv"
# DATA_PATH = Path(__file__).resolve().parents[2] / "data" / "mock_health_metrics_anomaly.csv"


app = FastAPI(title="Health Assistant API", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/api/summary")
def get_summary():
    if not DATA_PATH.exists():
        raise HTTPException(status_code=500, detail="Data source not found.")
    df = load_health_data(DATA_PATH)
    summary = compute_wellness_summary(df)
    return {
        "week_range": summary.week_range,
        "wellness_score": summary.wellness_score,
        "normalized_metrics": summary.normalized_metrics,
        "anomalies": [anomaly.__dict__ for anomaly in summary.anomalies],
        "suggestion": summary.suggestion,
    }


@app.get("/health")
def healthcheck():
    return {"status": "ok"}
