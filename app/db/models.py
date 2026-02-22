"""SQLAlchemy table schema for adaptive training platform."""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import JSON, Boolean, Date, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.database import Base


class User(Base):
    """User profile table."""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    age: Mapped[int] = mapped_column(Integer, nullable=False)
    bodyweight_kg: Mapped[float] = mapped_column(Float, nullable=False)
    training_age_years: Mapped[float] = mapped_column(Float, nullable=False)
    goal: Mapped[str] = mapped_column(String(32), nullable=False)
    mrv_baseline_sets: Mapped[int] = mapped_column(Integer, nullable=False)

    sessions: Mapped[list[Session]] = relationship(back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Training session root table."""

    __tablename__ = "sessions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    session_date: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    user: Mapped[User] = relationship(back_populates="sessions")
    exercise_logs: Mapped[list[ExerciseLogDB]] = relationship(back_populates="session", cascade="all, delete-orphan")
    metrics: Mapped[Metric | None] = relationship(back_populates="session", cascade="all, delete-orphan", uselist=False)


class ExerciseLogDB(Base):
    """Exercise execution details per session."""

    __tablename__ = "exercise_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), nullable=False)
    exercise: Mapped[str] = mapped_column(String(64), nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    load_kg: Mapped[float] = mapped_column(Float, nullable=False)
    rir: Mapped[float] = mapped_column(Float, nullable=False)

    session: Mapped[Session] = relationship(back_populates="exercise_logs")


class Metric(Base):
    """Readiness and physiological metrics per session."""

    __tablename__ = "metrics"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    session_id: Mapped[int] = mapped_column(ForeignKey("sessions.id", ondelete="CASCADE"), unique=True, nullable=False)
    sleep_hours: Mapped[float] = mapped_column(Float, nullable=False)
    resting_hr: Mapped[int] = mapped_column(Integer, nullable=False)
    hrv_rmssd: Mapped[float] = mapped_column(Float, nullable=False)
    soreness: Mapped[float] = mapped_column(Float, nullable=False)
    motivation: Mapped[float] = mapped_column(Float, nullable=False)
    rpe_session: Mapped[float] = mapped_column(Float, nullable=False)
    duration_min: Mapped[int] = mapped_column(Integer, nullable=False)

    session: Mapped[Session] = relationship(back_populates="metrics")


class Prescription(Base):
    """Generated prescription records for traceability."""

    __tablename__ = "prescriptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    target_date: Mapped[date] = mapped_column(Date, nullable=False)
    exercise: Mapped[str] = mapped_column(String(64), nullable=False)
    sets: Mapped[int] = mapped_column(Integer, nullable=False)
    reps: Mapped[int] = mapped_column(Integer, nullable=False)
    load_kg: Mapped[float] = mapped_column(Float, nullable=False)
    deload: Mapped[bool] = mapped_column(Boolean, nullable=False)
    rationale: Mapped[dict] = mapped_column(JSON, nullable=False)
