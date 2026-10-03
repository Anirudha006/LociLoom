"""
Tests for Spaced Repetition (SM-2) algorithm and Empirical Statistics.
"""

import pytest
from core.spaced_repetition import calculate_sm2, score_to_sm2_quality, schedule_next_review
from core.stats import calculate_cohens_d, analyze_experiment_results


def test_sm2_initial_review_success():
    # Repetition 0, first success (q=4) -> repetitions=1, interval=1
    new_reps, new_interval, new_ef = calculate_sm2(
        quality=4, repetitions=0, previous_interval=0, previous_ease_factor=2.5
    )
    assert new_reps == 1
    assert new_interval == 1
    assert new_ef == 2.5


def test_sm2_second_review_success():
    # Repetition 1 -> repetitions=2, interval=6
    new_reps, new_interval, new_ef = calculate_sm2(
        quality=4, repetitions=1, previous_interval=1, previous_ease_factor=2.5
    )
    assert new_reps == 2
    assert new_interval == 6


def test_sm2_subsequent_review_growth():
    # Repetition 2 -> interval = round(6 * 2.5) = 15
    new_reps, new_interval, new_ef = calculate_sm2(
        quality=4, repetitions=2, previous_interval=6, previous_ease_factor=2.5
    )
    assert new_reps == 3
    assert new_interval == 15


def test_sm2_lapse_reset():
    # Quality score < 3 (failure/lapse) resets repetitions to 0 and interval to 1
    new_reps, new_interval, new_ef = calculate_sm2(
        quality=1, repetitions=4, previous_interval=25, previous_ease_factor=2.5
    )
    assert new_reps == 0
    assert new_interval == 1
    # Ease factor should decrease but not below 1.3
    assert new_ef < 2.5
    assert new_ef >= 1.3


def test_sm2_ease_factor_floor():
    # Repeated failures should never lower ease factor below 1.3
    new_reps, new_interval, new_ef = calculate_sm2(
        quality=0, repetitions=0, previous_interval=1, previous_ease_factor=1.32
    )
    assert new_ef == 1.3


def test_score_to_sm2_quality():
    assert score_to_sm2_quality(correct=True, hints_used=0, response_time=3.0) == 5
    assert score_to_sm2_quality(correct=True, hints_used=0, response_time=8.5) == 4
    assert score_to_sm2_quality(correct=True, hints_used=1, response_time=4.0) == 3
    assert score_to_sm2_quality(correct=True, hints_used=2, response_time=5.0) == 2
    assert score_to_sm2_quality(correct=False, hints_used=1, response_time=6.0) == 1
    assert score_to_sm2_quality(correct=False, hints_used=0, response_time=0.5) == 0


def test_schedule_next_review():
    sched = schedule_next_review(quality=5, repetitions=1, previous_interval=1, previous_ease_factor=2.5)
    assert sched["repetitions"] == 2
    assert sched["interval_days"] == 6
    assert isinstance(sched["next_due"], str)
    assert len(sched["next_due"]) == 10  # YYYY-MM-DD


def test_calculate_cohens_d():
    a = [80.0, 85.0, 90.0, 75.0, 80.0]
    assert calculate_cohens_d(a, a) == 0.0

    b = [90.0, 95.0, 100.0, 85.0, 90.0]
    d = calculate_cohens_d(a, b)
    assert d > 0


def test_analyze_experiment_results():
    records = [
        {"condition": "Condition A (Linear Notes)", "immediate_score": 60.0, "study_time": 120.0, "satisfaction": 3},
        {"condition": "Condition A (Linear Notes)", "immediate_score": 65.0, "study_time": 115.0, "satisfaction": 3},
        {"condition": "Condition A (Linear Notes)", "immediate_score": 70.0, "study_time": 110.0, "satisfaction": 4},
        {"condition": "Condition B (LociLoom Memory Palace)", "immediate_score": 85.0, "study_time": 95.0, "satisfaction": 5},
        {"condition": "Condition B (LociLoom Memory Palace)", "immediate_score": 90.0, "study_time": 90.0, "satisfaction": 5},
        {"condition": "Condition B (LociLoom Memory Palace)", "immediate_score": 95.0, "study_time": 85.0, "satisfaction": 5},
    ]
    res = analyze_experiment_results(records)
    assert res["has_data"] is True
    assert res["mean_score_a"] < res["mean_score_b"]
    assert res["cohens_d"] > 0
    assert "power_warning" in res
    assert "interpretation" in res
