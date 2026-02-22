import pytest

from app.core.physiology import fatigue_model
from app.schemas.models import ExerciseLog


def test_fatigue_calculation_correctness() -> None:
    exercises = [
        ExerciseLog(exercise="Squat", sets=3, reps=5, load_kg=100, rir=2),
        ExerciseLog(exercise="Bench", sets=3, reps=8, load_kg=80, rir=1),
    ]

    fatigue = fatigue_model(exercises, session_rpe=8)
    assert fatigue == pytest.approx(1.9488, rel=1e-5)
