"""Deterministic physiology models for adaptive training."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from app.core.exceptions import InsufficientDataError, ValidationError
from app.schemas.models import ExerciseLog, SessionMetrics, UserProfile


def fatigue_model(exercises: Iterable[ExerciseLog], session_rpe: float) -> float:
    """Compute session fatigue index from workload and proximity to failure."""
    loads = np.array([e.load_kg for e in exercises], dtype=float)
    reps = np.array([e.reps for e in exercises], dtype=float)
    sets = np.array([e.sets for e in exercises], dtype=float)
    rir = np.array([e.rir for e in exercises], dtype=float)

    if loads.size == 0:
        raise ValidationError("At least one exercise is required for fatigue model")

    effort_factor = np.clip((5.0 - rir) / 5.0, 0.2, 1.0)
    work = loads * reps * sets
    normalized_work = np.sum(work * effort_factor) / 1000.0
    fatigue = normalized_work * (session_rpe / 10.0)
    return float(np.round(fatigue, 4))


def stimulus_model(exercises: Iterable[ExerciseLog]) -> float:
    """Estimate hypertrophic stimulus from hard sets and rep quality."""
    total_stimulus = 0.0
    for ex in exercises:
        rep_quality = 1.0 - abs(8.0 - ex.reps) / 12.0
        intensity_quality = np.clip(ex.load_kg / (ex.load_kg + 40.0), 0.35, 0.95)
        effort_quality = np.clip((4.0 - ex.rir) / 4.0, 0.1, 1.0)
        total_stimulus += ex.sets * rep_quality * intensity_quality * effort_quality
    return float(np.round(total_stimulus, 4))


def recovery_model(metrics: SessionMetrics) -> float:
    """Convert biofeedback indicators into readiness score [0, 1]."""
    sleep_score = np.clip(metrics.sleep_hours / 8.0, 0.0, 1.1)
    hrv_score = np.clip(metrics.hrv_rmssd / 55.0, 0.3, 1.3)
    hr_penalty = np.clip((metrics.resting_hr - 55) / 30.0, 0.0, 1.0)
    soreness_penalty = metrics.soreness / 10.0
    motivation_bonus = metrics.motivation / 10.0

    readiness = 0.35 * sleep_score + 0.3 * hrv_score + 0.2 * motivation_bonus - 0.1 * hr_penalty - 0.15 * soreness_penalty
    return float(np.round(np.clip(readiness, 0.0, 1.0), 4))


def mrv_estimator(profile: UserProfile, fatigue_history: Iterable[float]) -> int:
    """Estimate max recoverable volume from baseline and fatigue tolerance."""
    fatigue_arr = np.array(list(fatigue_history), dtype=float)
    if fatigue_arr.size < 3:
        raise InsufficientDataError("Need at least 3 fatigue observations to estimate MRV")

    fatigue_trend = np.mean(fatigue_arr[-3:])
    tolerance = np.clip(1.2 - fatigue_trend / 12.0, 0.75, 1.2)
    experience_adj = np.clip(0.9 + profile.training_age_years / 20.0, 0.9, 1.25)
    mrv_sets = int(np.round(profile.mrv_baseline_sets * tolerance * experience_adj))
    return int(np.clip(mrv_sets, 6, 45))


def performance_trend_analyzer(performance_scores: Iterable[float]) -> float:
    """Return linear trend slope of recent performance."""
    values = np.array(list(performance_scores), dtype=float)
    if values.size < 4:
        raise InsufficientDataError("Need at least 4 sessions for trend analysis")

    x = np.arange(values.size, dtype=float)
    x_centered = x - np.mean(x)
    y_centered = values - np.mean(values)
    slope = np.sum(x_centered * y_centered) / np.sum(x_centered**2)
    return float(np.round(slope, 4))
