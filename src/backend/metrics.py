from __future__ import annotations

from dataclasses import dataclass
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd


METRIC_FIELDS = ["calories_out", "calories_in", "total_sleep_mins", "rhr", "hrv"]


@dataclass
class Anomaly:
    metric: str
    value: float
    baseline_mean: float
    z_score: float
    direction: str


@dataclass
class WellnessSummary:
    week_range: Dict[str, str]
    wellness_score: float
    normalized_metrics: Dict[str, float]
    anomalies: List[Anomaly]
    suggestion: Dict[str, str]


def load_health_data(csv_path: Path) -> pd.DataFrame:
    df = pd.read_csv(csv_path)
    if not all(field in df.columns for field in METRIC_FIELDS):
        missing = [field for field in METRIC_FIELDS if field not in df.columns]
        raise ValueError(f"CSV missing required fields: {missing}")
    start_date = date.today() - timedelta(days=len(df) - 1)
    df["date"] = [start_date + timedelta(days=offset) for offset in range(len(df))]
    return df


def clip_outliers(series: pd.Series, lower: float = 1.0, upper: float = 99.0) -> pd.Series:
    low, high = np.percentile(series, [lower, upper])
    return series.clip(lower=low, upper=high)


def normalize_metric(value: float, baseline: pd.Series) -> float:
    clipped = clip_outliers(baseline)
    min_val, max_val = clipped.min(), clipped.max()
    if np.isclose(max_val, min_val):
        return 50.0
    normalized = 100.0 * (value - min_val) / (max_val - min_val)
    return float(np.clip(normalized, 0.0, 100.0))


def compute_anomalies(
    week_df: pd.DataFrame, baseline_df: pd.DataFrame, z_threshold: float = 1.5
) -> List[Anomaly]:
    anomalies: List[Anomaly] = []
    if len(baseline_df) < 14:
        return anomalies
    for metric in METRIC_FIELDS:
        baseline_series = baseline_df[metric]
        baseline_mean = baseline_series.mean()
        baseline_std = baseline_series.std(ddof=0)
        if np.isclose(baseline_std, 0):
            continue
        week_value = week_df[metric].mean()
        z_score = (week_value - baseline_mean) / baseline_std
        if abs(z_score) >= z_threshold:
            direction = "higher" if z_score > 0 else "lower"
            anomalies.append(
                Anomaly(
                    metric=metric,
                    value=float(week_value),
                    baseline_mean=float(baseline_mean),
                    z_score=float(z_score),
                    direction=direction,
                )
            )
    return anomalies


def generate_suggestion(normalized_metrics: Dict[str, float], anomalies: List[Anomaly]) -> Dict[str, str]:
    weakest_metric = min(normalized_metrics, key=normalized_metrics.get)
    focus_score = normalized_metrics[weakest_metric]
    focus_note = f"{weakest_metric} is the lowest this week at {focus_score:.1f}/100."
    if anomalies:
        notable = anomalies[0]
        anomaly_note = (
            f"{notable.metric} is {notable.direction} than normal (z-score {notable.z_score:.1f})."
        )
    else:
        anomaly_note = "No strong anomalies detected."
    guidance = {
        "sleep": "Aim for consistent bed and wake times plus a 30–60 minute increase in total sleep.",
        "nutrition": "Increase calorie intake with protein-forward meals and steady hydration.",
        "exercise": "Balance training load with at least one lighter recovery day and easy movement.",
        "fatigue": "Schedule a lighter training block and include gentle mobility to support recovery.",
    }
    suggestion_text = (
        f"{focus_note} {anomaly_note} "
        f"Suggested action: {guidance.get(weakest_metric, 'Prioritize balanced routines this week.')} "
        "These are general wellness tips, not medical advice."
    )
    return {"text": suggestion_text, "caveats": "For informational purposes only; not medical guidance."}


def compute_wellness_summary(df: pd.DataFrame) -> WellnessSummary:
    baseline_df = df.copy()
    week_df = df.tail(7)
    metric_map = {
        "exercise": "calories_out",
        "sleep": "total_sleep_mins",
        "nutrition": "calories_in",
        "fatigue": "hrv",
    }
    normalized_metrics: Dict[str, float] = {}
    for category, metric in metric_map.items():
        week_value = week_df[metric].mean()
        normalized_metrics[category] = normalize_metric(week_value, baseline_df[metric])
    wellness_score = float(np.mean(list(normalized_metrics.values())))
    anomalies = compute_anomalies(week_df, baseline_df)
    suggestion = generate_suggestion(normalized_metrics, anomalies)
    week_range = {
        "start": week_df["date"].min().isoformat(),
        "end": week_df["date"].max().isoformat(),
    }
    return WellnessSummary(
        week_range=week_range,
        wellness_score=round(wellness_score, 1),
        normalized_metrics=normalized_metrics,
        anomalies=anomalies,
        suggestion=suggestion,
    )
