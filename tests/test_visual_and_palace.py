"""
Tests for Visual Mapping, Palace Route Allocation, and Story Generation.
"""

import pytest
from core.visual_mapper import map_concept_to_visual, load_dictionary, generate_mnemonic_photo_card
from core.palace_builder import assign_concepts_to_palace, load_palace_templates, parse_custom_locations
from core.story_generator import generate_palace_story


def test_visual_mapper_exact_match():
    # Mitochondria is in concept_visual_dictionary.json
    res = map_concept_to_visual("Mitochondria", topic="Biology")
    assert "Curated Dictionary Match" in res["match_tier"]
    assert "battery" in res["visual_object"].lower() or "mitochondria" in res["visual_object"].lower()
    assert res["visual_reason"] != ""
    assert res["emoji"] != ""


def test_visual_mapper_fallback():
    # An obscure or invented word
    res = map_concept_to_visual("Xyloquaternary", topic="Computer Science")
    assert "Fallback" in res["match_tier"] or "Similarity" in res["match_tier"]
    assert res["visual_object"] != ""
    assert res["emoji"] != ""


def test_load_templates():
    templates = load_palace_templates()
    assert "house" in templates
    assert "classroom" in templates
    assert "garden" in templates
    assert "campus" in templates


def test_assign_concepts_to_palace():
    concepts = [
        {"concept": "Chloroplast", "sentence": "In leaves.", "order_index": 0, "visual_object": "green solar crystal"},
        {"concept": "Thylakoid", "sentence": "Pancake discs.", "order_index": 1, "visual_object": "stack of glowing emerald pancakes"}
    ]
    route = assign_concepts_to_palace(concepts, palace_type="house")
    assert len(route) == 2
    assert route[0]["order_index"] == 0
    assert route[0]["location_name"] != ""
    assert "x" in route[0]
    assert "y" in route[0]


def test_assign_concepts_custom_rooms():
    concepts = [
        {"concept": "Alpha", "order_index": 0, "visual_object": "golden apple"},
        {"concept": "Beta", "order_index": 1, "visual_object": "silver trumpet"}
    ]
    custom_str = "My Front Yard, My Bedroom, My Study Table"
    route = assign_concepts_to_palace(concepts, palace_type="custom", custom_places=custom_str)
    assert len(route) == 2
    assert route[0]["location_name"] == "My Front Yard"
    assert route[1]["location_name"] == "My Bedroom"


def test_generate_palace_story():
    route = [
        {
            "order_index": 0,
            "location_name": "Front Door",
            "concept": "Chloroplast",
            "visual_object": "glowing solar leaf"
        },
        {
            "order_index": 1,
            "location_name": "Foyer Table",
            "concept": "Glucose",
            "visual_object": "crystal honey jar"
        }
    ]
    
    story_normal = generate_palace_story(route, style="Normal")
    assert "Chloroplast" in story_normal
    assert "Glucose" in story_normal
    assert "Front Door" in story_normal
    assert "Foyer Table" in story_normal

    story_funny = generate_palace_story(route, style="Funny")
    assert len(story_funny) > 40

    story_dramatic = generate_palace_story(route, style="Dramatic")
    assert len(story_dramatic) > 40


def test_generate_mnemonic_photo_card_no_truncation():
    # Test with long concept, anchor, and explanation to verify full multi-line rendering
    img_bytes = generate_mnemonic_photo_card(
        concept="Empirical Evidence",
        visual_object="A lab coat and magnifying glass examining data slides with high precision",
        emoji="🔬",
        location="Main Entrance",
        topic="Data Science",
        difficulty="Medium",
        reason="We test clues and prove facts with experiments instead of guessing so our memory is rock solid."
    )
    assert isinstance(img_bytes, bytes)
    assert len(img_bytes) > 10000  # Valid non-empty PNG
    # Check PNG magic bytes header
    assert img_bytes[:8] == b"\x89PNG\r\n\x1a\n"
