"""Progression and load management algorithms."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from app.core.exceptions import InsufficientDataError


def load_progression_algorithm(last_load: float, readiness: float, trend: float, deload: bool) -> float:
    """Compute next load with bounded deterministic increments."""
    if deload:
        return float(np.round(last_load * 0.9, 2))

    readiness_boost = (readiness - 0.5) * 0.05
    trend_boost = np.clip(trend * 0.03, -0.02, 0.03)
    progression_rate = np.clip(0.01 + readiness_boost + trend_boost, -0.03, 0.05)
    return float(np.round(last_load * (1.0 + progression_rate), 2))


def volume_progression_algorithm(last_sets: int, readiness: float, mrv_sets: int) -> int:
    """Adjust set volume while respecting MRV."""
    if readiness >= 0.72 and last_sets < mrv_sets:
        return min(last_sets + 1, mrv_sets)
    if readiness <= 0.4:
        return max(last_sets - 1, 1)
    return last_sets


def deload_trigger_logic(fatigue_history: Iterable[float], readiness_history: Iterable[float], plateau: bool) -> bool:
    """Trigger deload from accumulating fatigue and low readiness."""
    fatigue = np.array(list(fatigue_history), dtype=float)
    readiness = np.array(list(readiness_history), dtype=float)
    if fatigue.size < 3 or readiness.size < 3:
        raise InsufficientDataError("Need at least 3 observations for deload logic")

    fatigue_flag = np.mean(fatigue[-3:]) > 8.5
    readiness_flag = np.mean(readiness[-3:]) < 0.45
    return bool(fatigue_flag and readiness_flag or plateau)


def plateau_detection(performance_scores: Iterable[float]) -> bool:
    """Detect plateau when gains flatten and variance collapses."""
    values = np.array(list(performance_scores), dtype=float)
    if values.size < 5:
        raise InsufficientDataError("Need at least 5 sessions for plateau detection")

    diffs = np.diff(values[-5:])
    low_growth = np.mean(diffs) < 0.15
    low_variance = np.std(values[-5:]) < 0.75
    return bool(low_growth and low_variance)
