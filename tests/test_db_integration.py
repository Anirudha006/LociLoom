"""
Tests for SQLite Database integration and Quiz Engine.
"""

import pytest
from core.db import (
    init_db,
    get_or_create_user,
    save_palace,
    get_palaces,
    get_palace_by_id,
    delete_palace,
    log_quiz_attempt,
    get_quiz_attempts,
    save_sm2_review,
    get_sm2_review,
    get_all_reviews_due,
    save_experiment_record,
    get_experiment_records
)
from core.quiz_engine import evaluate_typed_answer, get_hints, generate_quiz_deck


@pytest.fixture(autouse=True)
def setup_database():
    init_db()


def test_fuzzy_matching_threshold():
    # Fuzzy match threshold is 75%
    correct_exact, score_exact = evaluate_typed_answer("Mitochondria", "Mitochondria")
    assert correct_exact is True
    assert score_exact == 100.0

    correct_typo, score_typo = evaluate_typed_answer("Mitochondra", "Mitochondria")
    assert correct_typo is True
    assert score_typo >= 75.0

    correct_case, score_case = evaluate_typed_answer("mitochondria", "Mitochondria")
    assert correct_case is True
    assert score_case >= 80.0

    correct_wrong, score_wrong = evaluate_typed_answer("Ribosome", "Mitochondria")
    assert correct_wrong is False
    assert score_wrong < 50.0


def test_quiz_hints_generation():
    hint1, hint2 = get_hints("Photosynthesis", "Glowing green leaf", "🌿")
    assert "P" in hint1
    assert "_" in hint1
    assert "Glowing green leaf" in hint2


def test_quiz_deck_generation():
    concepts = [
        {"id": 1, "concept_text": "Chloroplast", "location_name": "Front Door", "visual_object": "Solar leaf"},
        {"id": 2, "concept_text": "Thylakoid", "location_name": "Hallway", "visual_object": "Green pancake stack"},
        {"id": 3, "concept_text": "Stroma", "location_name": "Living Room", "visual_object": "Thick fluid tub"}
    ]
    deck = generate_quiz_deck(concepts, count=3)
    assert len(deck) == 3
    for q in deck:
        assert "question_type" in q
        assert "prompt" in q
        assert "correct_answer" in q


def test_palace_crud_cycle():
    user_id = "test-user-999"
    get_or_create_user(user_id)
    test_concepts = [
        {
            "order_index": 0,
            "location_name": "Entryway",
            "concept_text": "Nucleus",
            "supporting_sentence": "Holds genetic info.",
            "difficulty": "Easy",
            "visual_object": "golden orb with blueprint maps",
            "visual_reason": "pulsing with harmonic hum"
        }
    ]
    
    # 1. Save
    palace_id = save_palace(
        user_id=user_id,
        title="Test Biology Palace",
        topic="Biology",
        palace_type="house",
        story_style="Normal",
        language="en",
        story_text="At the Entryway, a golden orb sits proudly.",
        concepts_list=test_concepts
    )
    assert palace_id > 0

    # 2. Read All
    palaces = get_palaces(user_id)
    assert any(p["id"] == palace_id for p in palaces)

    # 3. Read Single
    single = get_palace_by_id(palace_id)
    assert single is not None
    assert single["title"] == "Test Biology Palace"
    assert len(single["concepts"]) == 1
    assert single["concepts"][0]["concept_text"] == "Nucleus"

    # 4. Clean up
    delete_palace(palace_id)
    deleted = get_palace_by_id(palace_id)
    assert deleted is None


def test_quiz_and_review_lifecycle():
    user_id = "test-quiz-user"
    get_or_create_user(user_id)
    test_concepts = [
        {
            "order_index": 0,
            "location_name": "Front Porch",
            "concept_text": "Chloroplast",
            "supporting_sentence": "Contains chlorophyll.",
            "difficulty": "Easy",
            "visual_object": "solar crystal",
            "visual_reason": "green light capture"
        }
    ]
    palace_id = save_palace(
        user_id=user_id,
        title="Quiz Test Palace",
        topic="Biology",
        palace_type="house",
        story_style="Normal",
        language="en",
        story_text="On the front porch sits a solar crystal.",
        concepts_list=test_concepts
    )
    palace = get_palace_by_id(palace_id)
    concept_id = palace["concepts"][0]["id"]

    # Log attempt
    log_id = log_quiz_attempt(
        user_id=user_id,
        concept_id=concept_id,
        question_type="type_concept",
        correct=True,
        response_time=1.85,
        hints_used=0
    )
    assert log_id > 0
    
    history = get_quiz_attempts(user_id)
    assert len(history) > 0
    assert history[0]["concept_id"] == concept_id
    assert history[0]["correct"] == 1

    # Save review update
    save_sm2_review(
        concept_id=concept_id,
        ease_factor=2.6,
        interval_days=6,
        repetitions=2,
        next_due="2026-10-07"
    )
    
    rev = get_sm2_review(concept_id)
    assert rev is not None
    assert rev["repetitions"] == 2
    assert rev["interval_days"] == 6

    # Due reviews query
    due_list = get_all_reviews_due(user_id)
    assert isinstance(due_list, list)

    # Clean up
    delete_palace(palace_id)


def test_experiment_record_save_and_retrieve():
    user_id = "test-exp-user"
    rec_id = save_experiment_record(
        participant_id=user_id,
        condition="Condition B (LociLoom Memory Palace)",
        list_id="curriculum_biology",
        study_time=120.0,
        immediate_score=90.0,
        satisfaction=5,
        delayed_score=85.0
    )
    assert rec_id > 0

    records = get_experiment_records()
    assert len(records) > 0
    assert any(r["participant_id"] == user_id for r in records)
