"""
LociLoom Google Gemini Client (core/gemini_client.py)
Provides zero-dependency HTTP integration with Google Gemini 1.5 Flash
for generating vivid Method of Loci associative memory palace narratives.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"


def get_gemini_api_key() -> str:
    """
    Discovers Gemini API key in order of priority:
    1. streamlit session state ('gemini_api_key')
    2. os.environ ('GEMINI_API_KEY')
    3. streamlit secrets ('GEMINI_API_KEY')
    """
    try:
        import streamlit as st
        if "gemini_api_key" in st.session_state and st.session_state["gemini_api_key"]:
            return str(st.session_state["gemini_api_key"]).strip()
    except Exception:
        pass

    env_key = os.environ.get("GEMINI_API_KEY", "").strip()
    if env_key:
        return env_key

    try:
        import streamlit as st
        if hasattr(st, "secrets") and "GEMINI_API_KEY" in st.secrets:
            return str(st.secrets["GEMINI_API_KEY"]).strip()
    except Exception:
        pass

    return ""


def test_gemini_connection(api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Tests connectivity to Google Gemini API with a minimal ping prompt.
    Returns (True, message) on success, or (False, error_description) on failure.
    """
    key = (api_key or get_gemini_api_key()).strip()
    if not key:
        return False, "No API key provided. Please paste your Google Gemini API key."

    url = f"{GEMINI_API_URL}?key={key}"
    payload = {
        "contents": [{
            "parts": [{"text": "Reply with 'OK' only."}]
        }],
        "generationConfig": {
            "maxOutputTokens": 10,
            "temperature": 0.1
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=8)
        if resp.status_code == 200:
            return True, "Connection successful! Google Gemini 1.5 Flash is ready."
        elif resp.status_code == 400:
            return False, "Invalid API request (400). Please check your API key format."
        elif resp.status_code in (401, 403):
            return False, "Invalid or unauthorized API key (403). Please verify your Google AI Studio key."
        elif resp.status_code == 429:
            return False, "Rate limit reached (429). Please wait a moment and try again."
        else:
            return False, f"Gemini API returned status code {resp.status_code}: {resp.text[:120]}"
    except requests.exceptions.Timeout:
        return False, "Connection timed out. Please check your internet connection."
    except Exception as e:
        return False, f"Network error connecting to Gemini API: {str(e)}"


def build_story_prompt(assigned_concepts: List[Dict[str, Any]], style: str = "Normal") -> str:
    """Builds a prompt tailored for Method of Loci narrative generation."""
    route_details = []
    for idx, c in enumerate(assigned_concepts, 1):
        loc = c.get("location_name", f"Station {idx}")
        obj = c.get("visual_object", "symbolic token")
        concept = c.get("concept", f"Concept {idx}")
        route_details.append(f"{idx}. Station: '{loc}' | Visual Object: '{obj}' | Concept to Remember: '{concept}'")

    route_str = "\n".join(route_details)

    style_instructions = {
        "Normal": "Write a cohesive, logical, sensory-rich walkthrough exploring each station in exact sequential order.",
        "Funny": "Write an absurd, slapstick, whimsical, and hilarious journey connecting each station in exact sequential order.",
        "Dramatic": "Write an epic, high-stakes, cinematic, and mythological journey connecting each station in exact sequential order."
    }
    style_desc = style_instructions.get(style, style_instructions["Normal"])

    return f"""You are an expert cognitive memory coach creating a Method of Loci (Memory Palace) associative walk.
Task: Write a vivid, memorable story guiding the student through the following spatial stations in exact order.
Style: {style} ({style_desc})

Stations and Mnemonics:
{route_str}

Guidelines:
1. Guide the learner sequentially through every single station in the exact order listed.
2. In each station, create an active, unforgettable interaction between the student, the location, and the visual object representing the concept.
3. Keep the total narrative between 120 and 220 words (1-2 engaging paragraphs).
4. Write in second person ('You enter... you see... you reach...').
5. Return ONLY the story text, with no headers, markdown bullet points, or introductory chatter.
"""


def generate_gemini_palace_story(assigned_concepts: List[Dict[str, Any]],
                                 style: str = "Normal",
                                 api_key: Optional[str] = None) -> Optional[str]:
    """
    Calls Google Gemini 1.5 Flash to generate a vivid associative memory palace story.
    Returns the generated story string, or None if the request fails (enabling fallback).
    """
    if not assigned_concepts:
        return None

    key = (api_key or get_gemini_api_key()).strip()
    if not key:
        logger.warning("No Gemini API key available; fallback to rule-based templates.")
        return None

    prompt = build_story_prompt(assigned_concepts, style=style)
    url = f"{GEMINI_API_URL}?key={key}"
    payload = {
        "contents": [{
            "parts": [{"text": prompt}]
        }],
        "generationConfig": {
            "temperature": 0.75,
            "maxOutputTokens": 600
        }
    }

    try:
        resp = requests.post(url, json=payload, timeout=14)
        if resp.status_code == 200:
            data = resp.json()
            candidates = data.get("candidates", [])
            if candidates:
                parts = candidates[0].get("content", {}).get("parts", [])
                if parts:
                    story = parts[0].get("text", "").strip()
                    if story:
                        return story
            logger.warning(f"Gemini response did not contain text parts: {data}")
            return None
        else:
            logger.warning(f"Gemini API error {resp.status_code}: {resp.text[:200]}")
            return None
    except Exception as e:
        logger.warning(f"Gemini call exception: {e}")
        return None
