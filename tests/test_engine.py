from datetime import date, timedelta

from app.core.engine import AdaptiveEngine
from app.schemas.models import ExerciseLog, SessionMetrics, UserProfile


def test_prescription_validity() -> None:
    profile = UserProfile(
        user_id=1,
        age=30,
        bodyweight_kg=82.0,
        training_age_years=4.0,
        goal="strength",
        mrv_baseline_sets=14,
    )

    sessions = []
    base_date = date(2026, 1, 1)
    for i in range(5):
        metrics = SessionMetrics(
            date=base_date + timedelta(days=i * 2),
            sleep_hours=7.5,
            resting_hr=56,
            hrv_rmssd=58,
            soreness=3,
            motivation=8,
            rpe_session=7.5,
            duration_min=75,
        )
        exercises = [ExerciseLog(exercise="Squat", sets=4, reps=5, load_kg=120 + i, rir=2)]
        sessions.append((metrics, exercises))

    prescription = AdaptiveEngine().prescribe(profile, sessions)

    assert prescription.exercise == "Squat"
    assert 1 <= prescription.sets <= 20
    assert prescription.load_kg > 0
    assert prescription.target_date == sessions[-1][0].date + timedelta(days=2)
