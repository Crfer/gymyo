"""Data access repositories."""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Sequence
from datetime import timedelta

from sqlalchemy import select
from sqlalchemy.orm import Session, joinedload

from app.core.prediction import one_rm_estimator
from app.db.models import ExerciseLogDB, Metric, Prescription, Session as SessionDB, User
from app.schemas.models import (
    E1RMPoint,
    ExerciseLog,
    ProfileUpdate,
    SessionInput,
    SessionMetrics,
    SessionSummary,
    TrainingPrescription,
    UserProfile,
    WeeklyVolumePoint,
)

DEFAULT_USER_ID = 1


def get_or_create_default_user(db: Session) -> User:
    """Return app user, creating deterministic baseline profile if missing."""
    user = db.get(User, DEFAULT_USER_ID)
    if user is None:
        user = User(
            id=DEFAULT_USER_ID,
            age=30,
            bodyweight_kg=80.0,
            training_age_years=2.0,
            goal="hypertrophy",
            mrv_baseline_sets=14,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


def get_user_profile(db: Session, user_id: int) -> UserProfile:
    user = db.get(User, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")
    return UserProfile(
        user_id=user.id,
        age=user.age,
        bodyweight_kg=user.bodyweight_kg,
        training_age_years=user.training_age_years,
        goal=user.goal,
        mrv_baseline_sets=user.mrv_baseline_sets,
    )


def update_user_profile(db: Session, user_id: int, payload: ProfileUpdate) -> UserProfile:
    """Persist profile update and return updated schema."""
    user = db.get(User, user_id)
    if user is None:
        raise ValueError(f"User {user_id} not found")

    user.age = payload.age
    user.bodyweight_kg = payload.bodyweight_kg
    user.training_age_years = payload.training_age_years
    user.goal = payload.goal
    user.mrv_baseline_sets = payload.mrv_baseline_sets
    db.commit()
    return get_user_profile(db, user_id)


def save_session(db: Session, payload: SessionInput) -> int:
    if db.get(User, payload.user_id) is None:
        raise ValueError(f"User {payload.user_id} not found")

    session = SessionDB(user_id=payload.user_id, session_date=payload.metrics.date)
    db.add(session)
    db.flush()

    metric = Metric(
        session_id=session.id,
        sleep_hours=payload.metrics.sleep_hours,
        resting_hr=payload.metrics.resting_hr,
        hrv_rmssd=payload.metrics.hrv_rmssd,
        soreness=payload.metrics.soreness,
        motivation=payload.metrics.motivation,
        rpe_session=payload.metrics.rpe_session,
        duration_min=payload.metrics.duration_min,
    )
    db.add(metric)

    for ex in payload.exercises:
        db.add(
            ExerciseLogDB(
                session_id=session.id,
                exercise=ex.exercise,
                sets=ex.sets,
                reps=ex.reps,
                load_kg=ex.load_kg,
                rir=ex.rir,
            )
        )

    db.commit()
    return session.id


def get_recent_sessions(db: Session, user_id: int, limit: int = 8) -> Sequence[tuple[SessionMetrics, list[ExerciseLog]]]:
    stmt = (
        select(SessionDB)
        .where(SessionDB.user_id == user_id)
        .options(joinedload(SessionDB.metrics), joinedload(SessionDB.exercise_logs))
        .order_by(SessionDB.session_date.desc())
        .limit(limit)
    )
    rows = db.scalars(stmt).unique().all()
    sessions = []
    for session in reversed(rows):
        if session.metrics is None:
            continue
        metrics = SessionMetrics(
            date=session.session_date,
            sleep_hours=session.metrics.sleep_hours,
            resting_hr=session.metrics.resting_hr,
            hrv_rmssd=session.metrics.hrv_rmssd,
            soreness=session.metrics.soreness,
            motivation=session.metrics.motivation,
            rpe_session=session.metrics.rpe_session,
            duration_min=session.metrics.duration_min,
        )
        exercises = [
            ExerciseLog(
                exercise=e.exercise,
                sets=e.sets,
                reps=e.reps,
                load_kg=e.load_kg,
                rir=e.rir,
            )
            for e in session.exercise_logs
        ]
        sessions.append((metrics, exercises))
    return sessions


def get_latest_metrics(db: Session, user_id: int) -> SessionMetrics | None:
    """Fetch latest metrics for dashboard card."""
    stmt = (
        select(SessionDB)
        .where(SessionDB.user_id == user_id)
        .options(joinedload(SessionDB.metrics))
        .order_by(SessionDB.session_date.desc())
        .limit(1)
    )
    session = db.scalars(stmt).first()
    if session is None or session.metrics is None:
        return None

    return SessionMetrics(
        date=session.session_date,
        sleep_hours=session.metrics.sleep_hours,
        resting_hr=session.metrics.resting_hr,
        hrv_rmssd=session.metrics.hrv_rmssd,
        soreness=session.metrics.soreness,
        motivation=session.metrics.motivation,
        rpe_session=session.metrics.rpe_session,
        duration_min=session.metrics.duration_min,
    )


def update_metrics(db: Session, user_id: int, metrics: SessionMetrics) -> None:
    """Update metrics row for latest session of given date."""
    stmt = (
        db.query(SessionDB)
        .filter(SessionDB.user_id == user_id, SessionDB.session_date == metrics.date)
        .order_by(SessionDB.id.desc())
    )
    session = stmt.first()
    if session is None or session.metrics is None:
        raise ValueError("Session metrics not found")

    session.metrics.sleep_hours = metrics.sleep_hours
    session.metrics.resting_hr = metrics.resting_hr
    session.metrics.hrv_rmssd = metrics.hrv_rmssd
    session.metrics.soreness = metrics.soreness
    session.metrics.motivation = metrics.motivation
    session.metrics.rpe_session = metrics.rpe_session
    session.metrics.duration_min = metrics.duration_min
    db.commit()


def get_recent_session_summaries(db: Session, user_id: int, limit: int = 5) -> list[SessionSummary]:
    """Return compact recent session summaries for dashboard."""
    stmt = (
        select(SessionDB)
        .where(SessionDB.user_id == user_id)
        .options(joinedload(SessionDB.exercise_logs))
        .order_by(SessionDB.session_date.desc())
        .limit(limit)
    )
    rows = db.scalars(stmt).unique().all()
    result: list[SessionSummary] = []
    for row in rows:
        total_tonnage = sum(ex.load_kg * ex.reps * ex.sets for ex in row.exercise_logs)
        avg_rir = sum(ex.rir for ex in row.exercise_logs) / max(len(row.exercise_logs), 1)
        result.append(
            SessionSummary(
                date=row.session_date,
                exercise_count=len(row.exercise_logs),
                tonnage=round(total_tonnage, 2),
                avg_rir=round(avg_rir, 2),
            )
        )
    return result


def get_weekly_volume(db: Session, user_id: int, weeks: int = 8) -> list[WeeklyVolumePoint]:
    """Aggregate weekly volume by coarse muscle mapping from exercise name."""
    sessions = get_recent_sessions(db, user_id, limit=weeks * 4)
    buckets: dict[tuple, float] = defaultdict(float)

    for metrics, exercises in sessions:
        week_start = metrics.date - timedelta(days=metrics.date.weekday())
        for ex in exercises:
            muscle = _infer_muscle_group(ex.exercise)
            buckets[(week_start, muscle)] += ex.load_kg * ex.reps * ex.sets

    points = [
        WeeklyVolumePoint(week_start=week, muscle=muscle, volume=round(volume, 2))
        for (week, muscle), volume in sorted(buckets.items(), key=lambda item: (item[0][0], item[0][1]))
    ]
    return points


def get_e1rm_trend(db: Session, user_id: int, exercise: str) -> list[E1RMPoint]:
    """Return chronological e1RM estimates for selected exercise."""
    sessions = get_recent_sessions(db, user_id, limit=40)
    trend: list[E1RMPoint] = []
    normalized = exercise.lower()
    for metrics, exercises in sessions:
        for ex in exercises:
            if ex.exercise.lower() == normalized:
                trend.append(E1RMPoint(date=metrics.date, exercise=exercise, e1rm=one_rm_estimator(ex)))
    return trend


def save_prescription(db: Session, user_id: int, prescription: TrainingPrescription) -> int:
    row = Prescription(
        user_id=user_id,
        target_date=prescription.target_date,
        exercise=prescription.exercise,
        sets=prescription.sets,
        reps=prescription.reps,
        load_kg=prescription.load_kg,
        deload=prescription.deload,
        rationale=prescription.rationale,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return row.id


def _infer_muscle_group(exercise_name: str) -> str:
    lowered = exercise_name.lower()
    if any(token in lowered for token in ["squat", "lunge", "leg", "hamstring", "quad", "deadlift"]):
        return "Lower Body"
    if any(token in lowered for token in ["row", "pull", "lat", "chin"]):
        return "Back"
    if any(token in lowered for token in ["press", "bench", "chest", "dip"]):
        return "Chest"
    if any(token in lowered for token in ["curl", "extension", "tricep", "bicep", "shoulder", "raise"]):
        return "Arms/Shoulders"
    return "Other"
