"""Pydantic schemas for adaptive training domain."""

from __future__ import annotations

from datetime import date
from typing import Dict, List

from pydantic import BaseModel, Field, field_validator


class UserProfile(BaseModel):
    """Athlete profile and constraints for training decisions."""

    user_id: int = Field(gt=0)
    age: int = Field(ge=14, le=90)
    bodyweight_kg: float = Field(gt=30, lt=300)
    training_age_years: float = Field(ge=0, le=50)
    goal: str = Field(min_length=3, max_length=32)
    mrv_baseline_sets: int = Field(ge=6, le=40)


class ProfileUpdate(BaseModel):
    """Mutable profile fields for profile update endpoint."""

    age: int = Field(ge=14, le=90)
    bodyweight_kg: float = Field(gt=30, lt=300)
    training_age_years: float = Field(ge=0, le=50)
    goal: str = Field(min_length=3, max_length=32)
    mrv_baseline_sets: int = Field(ge=6, le=40)


class ExerciseLog(BaseModel):
    """Single exercise performed in a session."""

    exercise: str = Field(min_length=2, max_length=64)
    sets: int = Field(ge=1, le=20)
    reps: int = Field(ge=1, le=30)
    load_kg: float = Field(gt=0, lt=600)
    rir: float = Field(ge=0, le=6)


class SessionMetrics(BaseModel):
    """Session-level outcomes and readiness indicators."""

    date: date
    sleep_hours: float = Field(ge=0, le=16)
    resting_hr: int = Field(ge=30, le=120)
    hrv_rmssd: float = Field(ge=5, le=250)
    soreness: float = Field(ge=0, le=10)
    motivation: float = Field(ge=0, le=10)
    rpe_session: float = Field(ge=1, le=10)
    duration_min: int = Field(ge=10, le=300)


class TrainingPrescription(BaseModel):
    """Prescribed training outputs for the next session."""

    target_date: date
    exercise: str
    sets: int = Field(ge=1, le=20)
    reps: int = Field(ge=1, le=20)
    load_kg: float = Field(gt=0)
    deload: bool
    rationale: Dict[str, float | str]


class SessionInput(BaseModel):
    """Payload used by API for logging a full session."""

    user_id: int = Field(gt=0)
    metrics: SessionMetrics
    exercises: List[ExerciseLog] = Field(min_length=1)

    @field_validator("exercises")
    def unique_exercises(cls, values: List[ExerciseLog]) -> List[ExerciseLog]:
        names = [x.exercise.lower() for x in values]
        if len(set(names)) != len(names):
            raise ValueError("Exercise names must be unique per session")
        return values


class DailyMetricsUpdate(BaseModel):
    """Payload for updating daily physiological metrics."""

    user_id: int = Field(gt=0)
    metrics: SessionMetrics


class SessionSummary(BaseModel):
    """Short summary of a recent session."""

    date: date
    exercise_count: int
    tonnage: float
    avg_rir: float


class WeeklyVolumePoint(BaseModel):
    """Weekly volume metric by muscle group."""

    week_start: date
    muscle: str
    volume: float


class E1RMPoint(BaseModel):
    """Estimated 1RM point for trend display."""

    date: date
    exercise: str
    e1rm: float


class AnalyticsResponse(BaseModel):
    """Chart-friendly analytics payload."""

    sessions: int
    fatigue_mean: float
    stimulus_mean: float
    readiness_mean: float
    weekly_volume: List[WeeklyVolumePoint]
    e1rm_trend: List[E1RMPoint]


class DashboardResponse(BaseModel):
    """Dashboard data bundle for web UI."""

    next_workout: TrainingPrescription
    latest_metrics: SessionMetrics
    recent_sessions: List[SessionSummary]
