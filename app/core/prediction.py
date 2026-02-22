"""Deterministic prediction utilities for training decisions."""

from __future__ import annotations

from typing import Iterable

import numpy as np

from app.core.exceptions import InsufficientDataError
from app.schemas.models import ExerciseLog


def one_rm_estimator(log: ExerciseLog) -> float:
    """Estimate 1RM using Epley relation adjusted by RIR."""
    effective_reps = log.reps + max(0.0, log.rir)
    one_rm = log.load_kg * (1.0 + effective_reps / 30.0)
    return float(np.round(one_rm, 2))


def next_session_load_predictor(last_load: float, one_rm: float, target_reps: int, readiness: float) -> float:
    """Predict session load anchored to %1RM and readiness."""
    intensity = np.clip(1.0 - target_reps * 0.025, 0.6, 0.9)
    readiness_adj = np.clip((readiness - 0.5) * 0.06, -0.03, 0.04)
    base = one_rm * intensity * (1.0 + readiness_adj)
    constrained = np.clip(base, last_load * 0.9, last_load * 1.08)
    return float(np.round(constrained, 2))


def adaptation_score_calculator(stimulus_history: Iterable[float], fatigue_history: Iterable[float]) -> float:
    """Compute adaptation score from stimulus-fatigue balance."""
    stim = np.array(list(stimulus_history), dtype=float)
    fat = np.array(list(fatigue_history), dtype=float)
    if stim.size < 3 or fat.size < 3:
        raise InsufficientDataError("Need at least 3 observations for adaptation score")

    recent_stim = np.mean(stim[-3:])
    recent_fat = np.mean(fat[-3:])
    ratio = recent_stim / (recent_fat + 1e-6)
    return float(np.round(np.clip(ratio, 0.0, 3.0), 4))
