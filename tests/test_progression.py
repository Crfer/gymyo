from app.core.progression import (
    deload_trigger_logic,
    load_progression_algorithm,
    volume_progression_algorithm,
)


def test_progression_logic() -> None:
    load = load_progression_algorithm(last_load=100.0, readiness=0.8, trend=0.2, deload=False)
    sets = volume_progression_algorithm(last_sets=10, readiness=0.8, mrv_sets=12)
    deload = deload_trigger_logic([9.0, 8.9, 9.2], [0.4, 0.42, 0.41], plateau=False)

    assert load == 103.1
    assert sets == 11
    assert deload is True
