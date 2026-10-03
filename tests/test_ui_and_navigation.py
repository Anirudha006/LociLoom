"""
Tests for UI helper functions, Loci ID sanitization, animation configs, and palaces integration.
"""
import os
import pytest
from core.ui import format_loci_id, get_animated_sample_map_html, CSS_PATH
from core.db import get_palaces, save_palace, get_connection


def test_format_loci_id_clean():
    """Verify that a clean Loci ID remains unchanged and uppercase."""
    assert format_loci_id("LL-LOCI-6C25-D9") == "LL-LOCI-6C25-D9"
    assert format_loci_id("LL-GUEST-A1B2") == "LL-GUEST-A1B2"
    assert format_loci_id("loci-6c25-d9") == "LOCI-6C25-D9"


def test_format_loci_id_strips_timezone_and_time_suffixes():
    """Verify that stray timestamp / timezone artifacts like '-0:00' or '+00:00' are stripped."""
    assert format_loci_id("LL-LOCI-6C25-D9-0:00") == "LL-LOCI-6C25-D9"
    assert format_loci_id("LL-LOCI-6C25-D9+00:00") == "LL-LOCI-6C25-D9"
    assert format_loci_id("LL-LOCI-6C25-D9-05:00") == "LL-LOCI-6C25-D9"
    assert format_loci_id("LL-LOCI-6C25-D9:00") == "LL-LOCI-6C25-D9"
    assert format_loci_id("LL-STUDENT-0:00") == "LL-STUDENT"


def test_format_loci_id_empty_or_none():
    """Verify fallback handling for empty or None ID."""
    assert format_loci_id("") == "LL-ANON-0000"
    assert format_loci_id(None) == "LL-ANON-0000"


def test_animated_sample_map_html():
    """Verify the sample palace map HTML output and reduced motion toggle."""
    html_normal = get_animated_sample_map_html(reduced_motion=False)
    assert "Photosynthesis" in html_normal
    assert "hm-walker" in html_normal
    assert "animateMotion" in html_normal
    assert "FRONT GATE" in html_normal
    assert "GARDEN" in html_normal

    html_reduced = get_animated_sample_map_html(reduced_motion=True)
    assert ".hm-walker { display: none !important; }" in html_reduced
    assert "animation: none !important;" in html_reduced


def test_style_css_rules_present():
    """Verify that style.css contains the required website_home navigation and tile rules."""
    assert os.path.exists(CSS_PATH)
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert ".hm-tile" in content
    assert ".hm-bento" in content
    assert '[data-testid="stSidebarNav"]' in content
    assert "st-key-tile_" in content


def test_get_palaces_returns_expected_fields():
    """Verify that get_palaces returns concept_count, last_practised, and next_revision_due."""
    from core.db import get_or_create_user
    test_user = "TEST_UI_USER_999"
    get_or_create_user(test_user)
    # Ensure fresh test user palace
    palace_id = save_palace(
        user_id=test_user,
        title="Test Palace for UI",
        topic="Machine Learning",
        palace_type="Library",
        story_style="Descriptive",
        language="en",
        story_text="A simple test story",
        concepts_list=[{"concept_text": "Overfitting", "visual_object": "Rubber band", "location_name": "Living Room"}]
    )
    assert palace_id > 0

    palaces = get_palaces(test_user)
    assert len(palaces) >= 1
    p = palaces[0]
    assert p["title"] == "Test Palace for UI"
    assert "concept_count" in p
    assert p["concept_count"] == 1
    assert "last_practised" in p
    assert "next_revision_due" in p


def test_icon_font_protection_rules():
    """Verify that style.css protects Streamlit icons from ligature-breaking font overrides."""
    with open(CSS_PATH, "r", encoding="utf-8") as f:
        content = f.read()
    assert "Material Symbols Rounded" in content
    assert "stExpanderIcon" in content
    assert "stIconMaterial" in content
    # Ensure blanket span selector with !important is NOT present
    assert "p, span, label," not in content


def test_sign_out_user(monkeypatch):
    """Verify that sign_out_user clears authentication, active state, and redirects to app.py."""
    import streamlit as st
    from core.ui import sign_out_user

    st.session_state["auth_user"] = {"user_id": "LL-USER-1", "username": "Tester"}
    st.session_state["current_palace"] = {"title": "Active Palace"}
    st.session_state["quiz_palace"] = {"title": "Quiz Palace"}

    redirected = []
    monkeypatch.setattr(st, "switch_page", lambda page: redirected.append(page))

    sign_out_user()

    assert "auth_user" not in st.session_state
    assert "current_palace" not in st.session_state
    assert "quiz_palace" not in st.session_state
    assert st.session_state["anon_id"].startswith("LL-GUEST-")
    assert redirected == ["app.py"]

