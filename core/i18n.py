"""
LociLoom Internationalization (i18n) Engine
Loads and serves interface strings in English (en), Hindi (hi), and Kannada (kn).
Provides seamless fallback to English for any missing keys.
"""
import os
import json
from typing import Dict, Any

TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "translations")

_CACHE: Dict[str, Dict[str, str]] = {}

def load_language_strings(lang_code: str) -> Dict[str, str]:
    """Loads translations from disk and caches in memory."""
    global _CACHE
    clean_code = "en"
    if lang_code.lower().startswith("hi"):
        clean_code = "hi"
    elif lang_code.lower().startswith("kn"):
        clean_code = "kn"

    if clean_code in _CACHE:
        return _CACHE[clean_code]

    file_path = os.path.join(TRANSLATIONS_DIR, f"{clean_code}.json")
    if os.path.exists(file_path):
        try:
            with open(file_path, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
                _CACHE[clean_code] = data
                return data
        except Exception:
            pass

    # Fallback to English
    en_path = os.path.join(TRANSLATIONS_DIR, "en.json")
    if os.path.exists(en_path):
        with open(en_path, "r", encoding="utf-8") as f:
            data = json.load(f)
            _CACHE["en"] = data
            return data

    return {}

def t(key: str, lang_code: str = "en") -> str:
    """Translates a key into the specified target language with graceful fallback."""
    strings = load_language_strings(lang_code)
    if key in strings:
        return strings[key]
    
    # Try English fallback
    en_strings = load_language_strings("en")
    return en_strings.get(key, key)
