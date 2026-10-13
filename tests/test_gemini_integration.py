"""
Unit tests for Google Gemini client and LLM integration in LociLoom.
"""
import os
import pytest
from unittest.mock import patch, MagicMock
from core.gemini_client import (
    get_gemini_api_key,
    test_gemini_connection as check_gemini_connection,
    build_story_prompt,
    generate_gemini_palace_story
)
from core.story_generator import generate_palace_story


def test_get_gemini_api_key_from_env(monkeypatch):
    """Verify discovery of GEMINI_API_KEY from environment."""
    monkeypatch.setenv("GEMINI_API_KEY", "TEST_ENV_KEY_123")
    assert get_gemini_api_key() == "TEST_ENV_KEY_123"


def test_build_story_prompt_contains_stations_and_concepts():
    """Verify prompt builder formats Method of Loci concepts and sequential guidelines."""
    concepts = [
        {"location_name": "Front Porch", "visual_object": "Solar Lantern", "concept": "Chloroplast"},
        {"location_name": "Living Room", "visual_object": "Water Fountain", "concept": "Xylem"}
    ]
    prompt = build_story_prompt(concepts, style="Dramatic")
    assert "Front Porch" in prompt
    assert "Solar Lantern" in prompt
    assert "Chloroplast" in prompt
    assert "Dramatic" in prompt
    assert "Method of Loci" in prompt


def test_test_gemini_connection_empty_key():
    """Verify check_gemini_connection handles missing key gracefully."""
    ok, msg = check_gemini_connection(api_key="")
    assert not ok
    assert "No API key" in msg


@patch("requests.post")
def test_test_gemini_connection_success(mock_post):
    """Verify check_gemini_connection returns True on 200 OK."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_post.return_value = mock_resp

    ok, msg = check_gemini_connection(api_key="VALID_MOCK_KEY")
    assert ok
    assert "successful" in msg.lower()


@patch("requests.post")
def test_test_gemini_connection_invalid_key(mock_post):
    """Verify check_gemini_connection handles 403 unauthorized."""
    mock_resp = MagicMock()
    mock_resp.status_code = 403
    mock_post.return_value = mock_resp

    ok, msg = check_gemini_connection(api_key="INVALID_KEY")
    assert not ok
    assert "unauthorized" in msg.lower() or "403" in msg


@patch("requests.post")
def test_generate_gemini_palace_story_success(mock_post):
    """Verify generate_gemini_palace_story parses candidates and parts correctly."""
    mock_resp = MagicMock()
    mock_resp.status_code = 200
    mock_resp.json.return_value = {
        "candidates": [{
            "content": {
                "parts": [{"text": "You enter the front porch where a solar lantern glows, fixing the chloroplast in memory."}]
            }
        }]
    }
    mock_post.return_value = mock_resp

    concepts = [{"location_name": "Front Porch", "visual_object": "Solar Lantern", "concept": "Chloroplast"}]
    story = generate_gemini_palace_story(concepts, api_key="VALID_MOCK_KEY")
    assert story is not None
    assert "solar lantern" in story.lower()


@patch("core.gemini_client.generate_gemini_palace_story", return_value=None)
def test_generate_palace_story_fallback_on_gemini_failure(mock_gemini):
    """Verify generate_palace_story cleanly falls back to rule-based templates if Gemini returns None."""
    concepts = [
        {"location_name": "Front Porch", "visual_object": "Solar Lantern", "concept": "Chloroplast"},
        {"location_name": "Living Room", "visual_object": "Water Fountain", "concept": "Xylem"}
    ]
    # use_llm is True, but Gemini returns None (simulating network error / rate limit)
    story = generate_palace_story(concepts, style="Normal", use_llm=True, llm_api_key="MOCK_KEY")
    assert story is not None
    assert "Front Porch" in story
    assert "Solar Lantern" in story
