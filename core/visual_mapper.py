"""
LociLoom Concept-to-Visual-Object Mapper
Converts abstract academic concepts into tangible, memorable visual mnemonics.
Three-Tier Strategy:
1. Exact & lemmatized lookup in 240+ curated dictionary (Biology, Physics, CS, etc.)
2. TF-IDF Cosine Similarity semantic search against curated dictionary concepts
3. Concrete noun extraction + phonetic sound-alike associative rule fallback
   (marked as 'auto-suggested, please review')
"""
import os
import io
import re
import json
from typing import Dict, Any, Optional, Tuple, List
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from PIL import Image, ImageDraw, ImageFont

DICT_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "concept_visual_dictionary.json")

_DICT_CACHE = None
_TFIDF_CACHE = None
_VECTORIZER = None
_DICT_KEYS = []

# Phonetic & Prefix rules for associative fallback mnemonics
PREFIX_MNEMONICS = {
    "bio": ("🧬", "Glowing bio-hazard emerald flask", "Bio- prefix represents living biological energy"),
    "neuro": ("💡", "Branching fiber-optic neuron lamp", "Neuro- represents neural brain signaling"),
    "poly": ("📿", "Interlocking rainbow beaded necklace", "Poly- signifies multiple repeating subunits"),
    "tele": ("☎️", "Vintage red telephone booth", "Tele- represents distant communication"),
    "trans": ("🛸", "Teleportation beam platform", "Trans- signifies moving across boundaries"),
    "micro": ("🔬", "Brass high-power microscope", "Micro- represents microscopic miniature structures"),
    "crypto": ("🔐", "Engraved titanium cryptex puzzle cylinder", "Crypto- represents encrypted concealment"),
    "thermo": ("🌡️", "Digital thermometer glowing crimson", "Thermo- represents thermal heat regulation"),
    "hydro": ("🚒", "High-pressure fire hydrant shooting water", "Hydro- represents water fluid dynamics"),
    "electro": ("⚡", "Humming plasma spark orb", "Electro- represents electrical potential flow"),
    "photo": ("📸", "Golden vintage camera flash", "Photo- represents illumination by photons"),
    "chrono": ("⏱️", "Golden pocket stopwatch ticking", "Chrono- represents temporal sequence"),
    "geo": ("🌍", "Carved topographic stone globe", "Geo- represents planetary earth surfaces"),
    "astro": ("🔭", "Brass star-gazing telescope", "Astro- represents astronomical cosmic bodies")
}

# Phonetic Initial Sound Fallback Table
INITIAL_LETTER_FALLBACK = {
    "a": ("⚓", "Golden naval anchor", "Starts with 'A', anchoring this memory strongly"),
    "b": ("🔔", "Resonant brass bell", "Starts with 'B', ringing clear in your memory"),
    "c": ("🧭", "Ornate brass compass", "Starts with 'C', charting your conceptual route"),
    "d": ("🥁", "Booming tribal drum", "Starts with 'D', beating out the rhythm of this concept"),
    "e": ("⚡", "Crackling electric crystal", "Starts with 'E', energizing this key idea"),
    "f": ("🪶", "Luminous peacock feather", "Starts with 'F', floating gracefully at this spot"),
    "g": ("🏆", "Gleaming golden goblet", "Starts with 'G', celebrating this important term"),
    "h": ("🪖", "Polished knight helmet", "Starts with 'H', safeguarding this concept"),
    "i": ("🧊", "Glowing ice prism", "Starts with 'I', illuminating cold rational thought"),
    "j": ("🏺", "Ancient carved jade jar", "Starts with 'J', storing precious knowledge"),
    "k": ("🔑", "Heavy iron skeleton key", "Starts with 'K', unlocking this secret idea"),
    "l": ("🏮", "Hanging crimson paper lantern", "Starts with 'L', lighting up this station"),
    "m": ("🪞", "Gilded magic mirror", "Starts with 'M', reflecting this concept clearly"),
    "n": ("🧭", "Polished navigation dial", "Starts with 'N', navigating your mind's eye"),
    "o": ("🦉", "Carved wise stone owl", "Starts with 'O', observing this key point"),
    "p": ("🎭", "Duality theatre mask", "Starts with 'P', portraying this dramatic idea"),
    "q": ("👑", "Gilded royal queen scepter", "Starts with 'Q', ruling over this memory"),
    "r": ("🚀", "Silver retro rocket ship", "Starts with 'R', launching this concept high"),
    "s": ("⚔️", "Crossed silver broadswords", "Starts with 'S', striking this memory firmly"),
    "t": ("🔭", "Sturdy bronze telescope", "Starts with 'T', bringing distant details into focus"),
    "u": ("☂️", "Rainbow umbrella canopy", "Starts with 'U', sheltering this delicate idea"),
    "v": ("🎻", "Vibrating concert violin", "Starts with 'V', sounding a memorable note"),
    "w": ("🎡", "Spinning carnival Ferris wheel", "Starts with 'W', turning smoothly in thought"),
    "x": ("📦", "Wooden treasure crate stamped with an X", "Starts with 'X', marking the exact mental spot"),
    "y": ("🧶", "Vibrant yellow yarn ball", "Starts with 'Y', weaving through your memory fabric"),
    "z": ("⚡", "Z-shaped jagged lightning bolt", "Starts with 'Z', zapping this memory into place")
}

def load_dictionary() -> Dict[str, Any]:
    """Loads and caches the curated concept-to-visual dictionary."""
    global _DICT_CACHE, _TFIDF_CACHE, _VECTORIZER, _DICT_KEYS
    if _DICT_CACHE is not None:
        return _DICT_CACHE

    if os.path.exists(DICT_PATH):
        with open(DICT_PATH, "r", encoding="utf-8-sig") as f:
            _DICT_CACHE = json.load(f)
    else:
        _DICT_CACHE = {}

    # Initialize TF-IDF index over dictionary concepts
    _DICT_KEYS = list(_DICT_CACHE.keys())
    if _DICT_KEYS:
        _VECTORIZER = TfidfVectorizer(ngram_range=(1, 2), analyzer="char_wb")
        _TFIDF_CACHE = _VECTORIZER.fit_transform(_DICT_KEYS)

    return _DICT_CACHE

def normalize_concept_key(concept: str) -> str:
    """Normalizes concept string by lowercasing, stripping punctuation, and basic stemming."""
    clean = re.sub(r'[^a-zA-Z0-9\s]', '', concept.lower()).strip()
    return clean

def map_concept_to_visual(concept: str, topic: Optional[str] = None) -> Dict[str, Any]:
    """
    Maps an academic concept into an evocative visual mnemonic object.
    
    Returns dict:
    {
        "concept": concept,
        "emoji": "🌱",
        "visual_object": "Solar-powered emerald plant",
        "visual_reason": "Plants absorbing radiant sunlight to make nourishment",
        "match_tier": "Exact Dictionary" | "Semantic Similarity" | "Phonetic / Rule Fallback",
        "auto_suggested": bool
    }
    """
    dictionary = load_dictionary()
    clean_key = normalize_concept_key(concept)

    # -------------------------------------------------------------
    # TIER 1: Exact Dictionary Match
    # -------------------------------------------------------------
    if clean_key in dictionary:
        item = dictionary[clean_key]
        return {
            "concept": concept,
            "emoji": item["emoji"],
            "visual_object": item["object"],
            "visual_reason": item["reason"],
            "match_tier": "Curated Dictionary Match",
            "auto_suggested": False
        }

    # Try singular/plural inflection check (e.g. "plants" -> "plant", "enzymes" -> "enzyme")
    if clean_key.endswith("s") and clean_key[:-1] in dictionary:
        item = dictionary[clean_key[:-1]]
        return {
            "concept": concept,
            "emoji": item["emoji"],
            "visual_object": item["object"],
            "visual_reason": item["reason"],
            "match_tier": "Curated Dictionary Match (Inflected)",
            "auto_suggested": False
        }
    if clean_key.endswith("es") and clean_key[:-2] in dictionary:
        item = dictionary[clean_key[:-2]]
        return {
            "concept": concept,
            "emoji": item["emoji"],
            "visual_object": item["object"],
            "visual_reason": item["reason"],
            "match_tier": "Curated Dictionary Match (Inflected)",
            "auto_suggested": False
        }

    # -------------------------------------------------------------
    # TIER 2: Semantic / Substring TF-IDF Similarity
    # -------------------------------------------------------------
    # First check if any multi-word substring directly matches a dictionary key
    words = clean_key.split()
    for w in words:
        if len(w) > 3 and w in dictionary:
            item = dictionary[w]
            return {
                "concept": concept,
                "emoji": item["emoji"],
                "visual_object": item["object"],
                "visual_reason": f"Derived from '{w}': {item['reason']}",
                "match_tier": "Keyword Association",
                "auto_suggested": True
            }

    # TF-IDF Cosine Similarity against all curated dictionary entries
    if _TFIDF_CACHE is not None and _VECTORIZER is not None and _DICT_KEYS:
        query_vec = _VECTORIZER.transform([clean_key])
        sims = cosine_similarity(query_vec, _TFIDF_CACHE)[0]
        best_idx = int(np.argmax(sims))
        best_sim = float(sims[best_idx])

        # If similarity threshold is met (e.g. >= 0.40)
        if best_sim >= 0.40:
            nearest_key = _DICT_KEYS[best_idx]
            item = dictionary[nearest_key]
            return {
                "concept": concept,
                "emoji": item["emoji"],
                "visual_object": item["object"],
                "visual_reason": f"Associatively mapped via '{nearest_key}': {item['reason']}",
                "match_tier": "Similarity Association",
                "auto_suggested": True
            }

    # -------------------------------------------------------------
    # TIER 3: Rule-based & Phonetic Sound-Alike Fallback
    # -------------------------------------------------------------
    # Check Greek / Latin / scientific prefixes
    for prefix, (em, obj, reas) in PREFIX_MNEMONICS.items():
        if clean_key.startswith(prefix) or any(w.startswith(prefix) for w in words):
            return {
                "concept": concept,
                "emoji": em,
                "visual_object": obj,
                "visual_reason": f"{reas} (auto-suggested, please review)",
                "match_tier": "Prefix Rule Association",
                "auto_suggested": True
            }

    # Phonetic initial sound fallback
    first_char = clean_key[0] if clean_key else "m"
    if first_char in INITIAL_LETTER_FALLBACK:
        em, obj, reas = INITIAL_LETTER_FALLBACK[first_char]
        return {
            "concept": concept,
            "emoji": em,
            "visual_object": f"{obj} bearing the label '{concept[:15]}'",
            "visual_reason": f"{reas} (auto-suggested, please review)",
            "match_tier": "Phonetic Sound-Alike Fallback",
            "auto_suggested": True
        }

    # Default universal fallback
    return {
        "concept": concept,
        "emoji": "💡",
        "visual_object": f"Glowing neon sign inscribed with '{concept}'",
        "visual_reason": "Visual landmark to mentally anchor this unfamiliar topic (auto-suggested, please review)",
        "match_tier": "Default Fallback",
        "auto_suggested": True
    }


def generate_ai_photo_prompt(concept: str, visual_object: str, location: str, style: str = "Cinematic") -> str:
    """
    Synthesizes an ultra-detailed text-to-image prompt optimized for Midjourney / DALL-E 3 / Gemini Imagen.
    Encodes spatial realism, dramatic lighting, and vivid mnemonic composition.
    """
    return (
        f"A cinematic high-resolution 8k photograph taken with a 35mm f/1.4 lens inside a {location.lower()}. "
        f"In the center foreground, a vivid, physical {visual_object.lower()} stands prominently, serving as a mnemonic anchor for '{concept}'. "
        f"Dramatic volumetric golden hour lighting, rich tactile textures, shallow depth of field, architectural elegance, "
        f"hyper-realistic detailing, educational and surreal atmosphere."
    )


def generate_mnemonic_photo_card(concept: str, visual_object: str, emoji: str, location: str, topic: str, difficulty: str = "Medium") -> bytes:
    """
    Generates a standalone, high-res illustrated visual mnemonic photo card (1000x650) in PNG format.
    Works 100% offline with zero external dependencies, providing vivid spatial cards.
    """
    width, height = 1000, 650
    # Clean gradient background
    img = Image.new("RGB", (width, height), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # 1. Subtle Background Gradient & Border
    for y in range(height):
        # Soft Indigo-tinted gradient from #F8FAFC down to #EEF2FF
        r = int(248 - (y / height) * 10)
        g = int(250 - (y / height) * 8)
        b = int(252 + (y / height) * 3)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Outer decorative card border
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=24, outline="#CBD5E1", width=3)

    # 2. Top Location Banner
    draw.rounded_rectangle([40, 40, width - 40, 110], radius=16, fill="#5B6CFF")
    draw.text((65, 58), f"📍 LOCUS STATION: {location.upper()}", fill="#FFFFFF")
    draw.text((width - 240, 58), f"DISCIPLINE: {topic.upper()}", fill="#E0E7FF")

    # 3. Central Focal Frame
    draw.rounded_rectangle([40, 130, width - 40, 480], radius=18, fill="#FFFFFF", outline="#E2E8F0", width=2)

    # Inner decorative spotlight circle
    draw.ellipse([width // 2 - 120, 160, width // 2 + 120, 400], fill="#F4F6FB", outline="#5B6CFF", width=3)

    # Visual Mnemonic Title in Center
    draw.text((width // 2, 280), f"[{emoji}]", fill="#1F2937", anchor="mm")
    draw.text((width // 2, 435), f"{visual_object}", fill="#1E1B4B", anchor="mm")

    # 4. Bottom Concept Details
    draw.rounded_rectangle([40, 500, width - 40, 605], radius=16, fill="#F8FAFC", outline="#E2E8F0", width=1)
    draw.text((70, 525), f"Target Concept Anchor: {concept}", fill="#111827")
    draw.text((70, 560), f"Cognitive Difficulty: {difficulty}  |  Method of Loci Spatial Anchor", fill="#64748B")

    # Save to memory buffer
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
