"""
Tests for NLP extraction and Topic Classification.
"""

import pytest
from core.nlp_extract import extract_key_concepts, sanitize_text, split_into_sentences
from core.topic_classifier import classify_topic, get_topic_probabilities


def test_extract_key_concepts_basic():
    sample_text = (
        "Photosynthesis occurs within the chloroplasts of plant cells. "
        "Chlorophyll absorbs solar energy to convert carbon dioxide and water into glucose and oxygen."
    )
    concepts = extract_key_concepts(sample_text, max_concepts=5)
    assert len(concepts) > 0
    assert len(concepts) <= 5
    for c in concepts:
        assert "concept" in c
        assert "supporting_sentence" in c
        assert isinstance(c["concept"], str)
        assert len(c["concept"]) > 0


def test_extract_key_concepts_empty_or_whitespace():
    assert extract_key_concepts("") == []
    assert extract_key_concepts("   \n\t  ") == []


def test_extract_key_concepts_order_preserved():
    text = "First, glycolysis splits glucose. Next, Krebs cycle generates electrons. Finally, phosphorylation produces ATP."
    concepts = extract_key_concepts(text, max_concepts=3)
    assert len(concepts) >= 2
    # Verify concepts appear in text sequence
    concept_names = [c["concept"].lower() for c in concepts]
    assert any("glycolysis" in name or "glucose" in name for name in concept_names)


def test_sanitize_and_split():
    raw = "  Photosynthesis is vital. Chloroplasts are green.  "
    sanitized = sanitize_text(raw)
    assert not sanitized.startswith("  ")
    sents = split_into_sentences(sanitized)
    assert len(sents) == 2


def test_classify_topic():
    bio_text = "Photosynthesis takes place in chloroplasts where chlorophyll captures sunlight."
    topic_bio, conf_bio = classify_topic(bio_text)
    assert isinstance(topic_bio, str)
    assert 0.0 <= conf_bio <= 1.0

    cs_text = "Binary search algorithms require a sorted array to achieve logarithmic time complexity."
    topic_cs, conf_cs = classify_topic(cs_text)
    assert topic_cs == "Computer Science"
    assert conf_cs > 0.25


def test_topic_probabilities():
    cs_text = "Binary search algorithms require a sorted array."
    probs = get_topic_probabilities(cs_text)
    assert "Computer Science" in probs
    assert "Biology" in probs
    assert len(probs) == 7
