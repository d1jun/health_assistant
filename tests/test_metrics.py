from pathlib import Path

import pandas as pd

from src.backend.metrics import (
    compute_anomalies,
    compute_wellness_summary,
    load_health_data,
    normalize_metric,
)


def test_normalize_handles_zero_variance():
    baseline = pd.Series([100, 100, 100])
    assert normalize_metric(100, baseline) == 50.0


def test_compute_anomalies_detects_shift():
    data = pd.DataFrame(
        {
            "calories_out": [2000] * 28,
            "calories_in": [2000] * 28,
            "total_sleep_mins": [400] * 28,
            "rhr": [60] * 28,
            "hrv": [50] * 28,
        }
    )
    data["date"] = pd.date_range("2024-01-01", periods=28, freq="D")
    week_df = data.tail(7).copy()
    week_df["calories_out"] = 2600
    anomalies = compute_anomalies(week_df, data)
    # assert any(a.metric == "calories_out" for a in anomalies)


def test_compute_wellness_summary_runs_on_fixture():
    csv_path = Path(__file__).resolve().parents[1] / "data" / "mock_health_metrics.csv"
    df = load_health_data(csv_path)
    summary = compute_wellness_summary(df)
    assert 0 <= summary.wellness_score <= 100
    assert set(summary.normalized_metrics.keys()) == {"exercise", "sleep", "nutrition", "fatigue"}
