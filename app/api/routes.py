"""FastAPI routes for adaptive training engine."""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.core.engine import AdaptiveEngine
from app.core.physiology import fatigue_model, recovery_model, stimulus_model
from app.db.database import get_db
from app.db.repositories import (
    get_e1rm_trend,
    get_latest_metrics,
    get_or_create_default_user,
    get_recent_session_summaries,
    get_recent_sessions,
    get_user_profile,
    get_weekly_volume,
    save_prescription,
    save_session,
    update_metrics,
    update_user_profile,
)
from app.schemas.models import (
    AnalyticsResponse,
    DailyMetricsUpdate,
    DashboardResponse,
    ProfileUpdate,
    SessionInput,
    SessionMetrics,
    TrainingPrescription,
    UserProfile,
)

router = APIRouter()
engine = AdaptiveEngine()


@router.get("/profile", response_model=UserProfile)
def profile(db: Session = Depends(get_db)) -> UserProfile:
    user = get_or_create_default_user(db)
    return get_user_profile(db, user.id)


@router.put("/profile", response_model=UserProfile)
def put_profile(payload: ProfileUpdate, db: Session = Depends(get_db)) -> UserProfile:
    user = get_or_create_default_user(db)
    try:
        return update_user_profile(db, user.id, payload)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc


@router.post("/log-session")
def log_session(payload: SessionInput, db: Session = Depends(get_db)) -> dict[str, int]:
    get_or_create_default_user(db)
    try:
        session_id = save_session(db, payload)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return {"session_id": session_id}


@router.post("/update-metrics")
def post_update_metrics(payload: DailyMetricsUpdate, db: Session = Depends(get_db)) -> dict[str, str]:
    try:
        update_metrics(db, payload.user_id, payload.metrics)
    except ValueError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return {"status": "updated", "date": str(date.fromisoformat(str(payload.metrics.date)))}


@router.get("/next-workout", response_model=TrainingPrescription)
def next_workout(user_id: int = Query(default=1, gt=0), db: Session = Depends(get_db)) -> TrainingPrescription:
    try:
        profile_data = get_user_profile(db, user_id)
        recent = get_recent_sessions(db, user_id)
        prescription = engine.prescribe(profile_data, recent)
        save_prescription(db, user_id, prescription)
        return prescription
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/analytics", response_model=AnalyticsResponse)
def analytics(user_id: int = Query(default=1, gt=0), exercise: str = Query(default="Squat"), db: Session = Depends(get_db)) -> AnalyticsResponse:
    recent = get_recent_sessions(db, user_id, limit=12)
    if len(recent) < 3:
        raise HTTPException(status_code=400, detail="Need at least 3 sessions")

    fatigue = [fatigue_model(ex, m.rpe_session) for m, ex in recent]
    stimulus = [stimulus_model(ex) for _, ex in recent]
    readiness = [recovery_model(m) for m, _ in recent]
    weekly_volume = get_weekly_volume(db, user_id, weeks=8)
    e1rm_trend = get_e1rm_trend(db, user_id, exercise)
    return AnalyticsResponse(
        sessions=len(recent),
        fatigue_mean=float(sum(fatigue) / len(fatigue)),
        stimulus_mean=float(sum(stimulus) / len(stimulus)),
        readiness_mean=float(sum(readiness) / len(readiness)),
        weekly_volume=weekly_volume,
        e1rm_trend=e1rm_trend,
    )


@router.get("/dashboard", response_model=DashboardResponse)
def dashboard(user_id: int = Query(default=1, gt=0), db: Session = Depends(get_db)) -> DashboardResponse:
    profile_data = get_user_profile(db, user_id)
    recent = get_recent_sessions(db, user_id)
    if not recent:
        raise HTTPException(status_code=400, detail="Need at least 1 logged session")

    latest_metrics = get_latest_metrics(db, user_id)
    if latest_metrics is None:
        raise HTTPException(status_code=400, detail="No metrics available")

    if len(recent) < 5:
        raise HTTPException(status_code=400, detail="Need at least 5 sessions for next workout")

    prescription = engine.prescribe(profile_data, recent)
    summaries = get_recent_session_summaries(db, user_id)
    return DashboardResponse(next_workout=prescription, latest_metrics=latest_metrics, recent_sessions=summaries)
