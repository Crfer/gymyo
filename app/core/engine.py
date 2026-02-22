"""Central adaptive training decision engine."""

from __future__ import annotations

from datetime import timedelta
from typing import Sequence

from app.core.physiology import (
    fatigue_model,
    mrv_estimator,
    performance_trend_analyzer,
    recovery_model,
    stimulus_model,
)
from app.core.prediction import (
    adaptation_score_calculator,
    next_session_load_predictor,
    one_rm_estimator,
)
from app.core.progression import (
    deload_trigger_logic,
    load_progression_algorithm,
    plateau_detection,
    volume_progression_algorithm,
)
from app.schemas.models import ExerciseLog, SessionMetrics, TrainingPrescription, UserProfile


class AdaptiveEngine:
    """Produces deterministic next-session prescriptions from recent data."""

    def prescribe(
        self,
        profile: UserProfile,
        recent_sessions: Sequence[tuple[SessionMetrics, Sequence[ExerciseLog]]],
    ) -> TrainingPrescription:
        if len(recent_sessions) < 5:
            raise ValueError("At least 5 recent sessions are required for a prescription")

        fatigue_hist = [fatigue_model(exs, m.rpe_session) for m, exs in recent_sessions]
        stimulus_hist = [stimulus_model(exs) for _, exs in recent_sessions]
        readiness_hist = [recovery_model(m) for m, _ in recent_sessions]
        performance_hist = [adaptation_score_calculator(stimulus_hist[: i + 1], fatigue_hist[: i + 1]) if i >= 2 else 1.0 for i in range(len(fatigue_hist))]

        mrv_sets = mrv_estimator(profile, fatigue_hist)
        plateau = plateau_detection(performance_hist)
        deload = deload_trigger_logic(fatigue_hist, readiness_hist, plateau)
        trend = performance_trend_analyzer(performance_hist)

        last_metrics, last_exercises = recent_sessions[-1]
        anchor = max(last_exercises, key=lambda x: x.load_kg)
        one_rm = one_rm_estimator(anchor)

        next_sets = volume_progression_algorithm(anchor.sets, readiness_hist[-1], mrv_sets)
        projected_load = next_session_load_predictor(anchor.load_kg, one_rm, anchor.reps, readiness_hist[-1])
        next_load = load_progression_algorithm(projected_load, readiness_hist[-1], trend, deload)

        target_date = last_metrics.date + timedelta(days=2)
        rationale = {
            "readiness": readiness_hist[-1],
            "fatigue": fatigue_hist[-1],
            "trend": trend,
            "mrv_sets": float(mrv_sets),
            "adaptation_score": adaptation_score_calculator(stimulus_hist, fatigue_hist),
            "deload": "1" if deload else "0",
        }

        return TrainingPrescription(
            target_date=target_date,
            exercise=anchor.exercise,
            sets=next_sets,
            reps=anchor.reps,
            load_kg=next_load,
            deload=deload,
            rationale=rationale,
        )
