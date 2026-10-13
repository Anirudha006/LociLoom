"""
LociLoom Google Gemini Client (core/gemini_client.py)
Provides resilient HTTP integration with Google Gemini Flash models
for generating vivid Method of Loci associative memory palace narratives.
Dynamically resolves available active models to prevent 404 deprecation errors.
"""
import os
import logging
from typing import List, Dict, Any, Optional, Tuple
import requests

logger = logging.getLogger(__name__)

CANDIDATE_MODELS = [
    "gemini-3-flash-preview",
    "gemini-3.8-flash",
    "gemini-3.1-flash-lite",
    "gemini-3.5-flash",
    "gemini-flash-latest",
    "gemini-2.5-flash",
]


def get_headers(api_key: str) -> Dict[str, str]:
    """Builds required HTTP headers including x-goog-api-key for standard and AQ authorization keys."""
    return {
        "x-goog-api-key": api_key.strip(),
        "Content-Type": "application/json"
    }


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


def resolve_working_model(api_key: str) -> str:
    """
    Dynamically discovers active models for the user's API key.
    Queries /v1beta/models and prioritizes active, non-deprecated flash models.
    """
    key = api_key.strip()
    if not key:
        return CANDIDATE_MODELS[0]

    try:
        models_url = f"https://generativelanguage.googleapis.com/v1beta/models?key={key}"
        resp = requests.get(models_url, headers=get_headers(key), timeout=6)
        if resp.status_code == 200:
            data = resp.json()
            models_list = data.get("models", [])
            supported = [
                m.get("name", "").replace("models/", "")
                for m in models_list
                if "generateContent" in m.get("supportedGenerationMethods", [])
            ]
            # Exclude known-deprecated models
            deprecated_prefixes = ("gemini-1.5", "gemini-2.0", "gemini-pro")
            active_supported = [
                s for s in supported
                if not any(s.startswith(p) for p in deprecated_prefixes)
            ]
            for cand in CANDIDATE_MODELS:
                if cand in active_supported:
                    return cand
            for s in active_supported:
                if "flash" in s:
                    return s
            if active_supported:
                return active_supported[0]
    except Exception:
        pass

    return CANDIDATE_MODELS[0]


def test_gemini_connection(api_key: Optional[str] = None) -> Tuple[bool, str]:
    """
    Tests connectivity to Google Gemini API.
    Attempts model resolution and resilient fallback across active candidate models.
    """
    key = (api_key or get_gemini_api_key()).strip()
    if not key:
        return False, "No API key provided. Please paste your Google Gemini API key."

    target_model = resolve_working_model(key)
    models_to_try = [target_model] + [m for m in CANDIDATE_MODELS if m != target_model]

    headers = get_headers(key)
    payload = {
        "contents": [{"parts": [{"text": "Reply with 'OK' only."}]}],
        "generationConfig": {
            "maxOutputTokens": 100,
            "temperature": 0.1,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }

    last_error = ""
    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=12)
            if resp.status_code == 200:
                try:
                    import streamlit as st
                    st.session_state["gemini_active_model"] = model
                except Exception:
                    pass
                return True, f"Connection successful! Connected to Google {model}."
            elif resp.status_code in (401, 403):
                return False, "Invalid or unauthorized API key (403). Please verify your Google AI Studio key."
            elif resp.status_code == 404:
                last_error = f"Model {model} is not available (404), checking alternatives..."
                continue
            elif resp.status_code == 503:
                last_error = f"Model {model} is experiencing temporary high demand (503), checking alternatives..."
                continue
            elif resp.status_code == 429:
                last_error = f"Rate limit reached on {model} (429), checking alternatives..."
                continue
            else:
                last_error = f"Gemini API returned status code {resp.status_code}: {resp.text[:120]}"
        except requests.exceptions.Timeout:
            last_error = f"Timeout connecting to {model}, checking alternatives..."
            continue
        except Exception as e:
            last_error = f"Network error connecting to Gemini API: {str(e)}"

    return False, last_error or "Could not find a supported Gemini model for this API key."


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
    Calls Google Gemini to generate a vivid associative memory palace story.
    Returns the generated story string, or None if the request fails (enabling fallback).
    """
    if not assigned_concepts:
        return None

    key = (api_key or get_gemini_api_key()).strip()
    if not key:
        logger.warning("No Gemini API key available; fallback to rule-based templates.")
        return None

    prompt = build_story_prompt(assigned_concepts, style=style)
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "temperature": 0.75,
            "maxOutputTokens": 800,
            "thinkingConfig": {"thinkingBudget": 0}
        }
    }

    headers = get_headers(key)

    # Determine which model to target
    active_model = None
    try:
        import streamlit as st
        active_model = st.session_state.get("gemini_active_model")
    except Exception:
        pass

    if not active_model:
        active_model = resolve_working_model(key)

    models_to_try = [active_model] + [m for m in CANDIDATE_MODELS if m != active_model]

    for model in models_to_try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}"
        try:
            resp = requests.post(url, headers=headers, json=payload, timeout=20)
            if resp.status_code == 200:
                data = resp.json()
                candidates = data.get("candidates", [])
                if candidates:
                    parts = candidates[0].get("content", {}).get("parts", [])
                    if parts:
                        story = parts[0].get("text", "").strip()
                        if story:
                            return story
                continue
            elif resp.status_code in (404, 503, 429):
                logger.info(f"Model {model} returned status {resp.status_code}, trying next candidate...")
                continue
            else:
                logger.warning(f"Gemini error {resp.status_code}: {resp.text[:150]}")
                continue
        except Exception as e:
            logger.warning(f"Gemini call exception with {model}: {e}")
            continue

    return None
