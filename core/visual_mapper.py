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
import textwrap
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


def get_card_font(size: int, bold: bool = False):
    """Safely loads TrueType fonts for high-res PNG card rendering across Windows and Linux."""
    candidates = [
        "arialbd.ttf" if bold else "arial.ttf",
        "DejaVuSans-Bold.ttf" if bold else "DejaVuSans.ttf",
        "segoeuib.ttf" if bold else "segoeui.ttf",
        "calibrib.ttf" if bold else "calibri.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
    ]
    for c in candidates:
        try:
            return ImageFont.truetype(c, size)
        except Exception:
            continue
    try:
        return ImageFont.load_default(size=size)
    except Exception:
        return ImageFont.load_default()


def draw_mnemonic_illustration(draw: ImageDraw.ImageDraw, cx: int, cy: int, concept: str, visual_object: str):
    """
    Draws recognizable, colorful cartoon-style vector illustrations for memory palace anchors.
    Replaces generic placeholders with vivid visual scenes.
    """
    text = (concept + " " + visual_object).lower()

    if any(k in text for k in ["laptop", "code", "program", "python", "sql", "comput", "software", "screen", "digital lab", "data science"]):
        # 💻 Modern Laptop Workstation with Glowing Code
        draw.rounded_rectangle([cx - 75, cy - 60, cx + 75, cy + 25], radius=8, fill="#0F172A", outline="#38BDF8", width=2)
        draw.line([(cx - 60, cy - 40), (cx - 15, cy - 40)], fill="#22C55E", width=4)
        draw.line([(cx - 60, cy - 25), (cx + 35, cy - 25)], fill="#38BDF8", width=4)
        draw.line([(cx - 40, cy - 10), (cx + 10, cy - 10)], fill="#FBBF24", width=4)
        draw.line([(cx - 60, cy + 5), (cx - 5, cy + 5)], fill="#A855F7", width=4)
        draw.polygon([(cx - 95, cy + 40), (cx + 95, cy + 40), (cx + 75, cy + 25), (cx - 75, cy + 25)], fill="#CBD5E1", outline="#94A3B8")
        draw.rounded_rectangle([cx - 20, cy + 28, cx + 20, cy + 36], radius=2, fill="#94A3B8")
    elif any(k in text for k in ["puzzle", "pattern", "jigsaw", "match", "cluster"]):
        # 🧩 Snapping Colorful Puzzle Pieces
        draw.rounded_rectangle([cx - 48, cy - 48, cx - 6, cy - 6], radius=6, fill="#EF4444")
        draw.rounded_rectangle([cx + 6, cy - 48, cx + 48, cy - 6], radius=6, fill="#3B82F6")
        draw.rounded_rectangle([cx - 48, cy + 6, cx - 6, cy + 48], radius=6, fill="#10B981")
        draw.rounded_rectangle([cx + 6, cy + 6, cx + 48, cy + 48], radius=6, fill="#F59E0B")
        draw.ellipse([cx - 14, cy - 14, cx + 14, cy + 14], fill="#FFFFFF", outline="#CBD5E1", width=2)
        draw.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill="#4553E8")
    elif any(k in text for k in ["chart", "graph", "visual", "plot", "statistic", "analy", "metric", "trend"]):
        # 📊 Vibrant 3D Rising Bar Chart with Growth Arrow
        draw.rectangle([cx - 60, cy + 32, cx + 60, cy + 36], fill="#94A3B8")
        draw.rectangle([cx - 50, cy + 8, cx - 28, cy + 32], fill="#6366F1")
        draw.rectangle([cx - 20, cy - 15, cx + 2, cy + 32], fill="#14B8A6")
        draw.rectangle([cx + 10, cy - 35, cx + 32, cy + 32], fill="#F59E0B")
        draw.rectangle([cx + 40, cy - 58, cx + 62, cy + 32], fill="#10B981")
        draw.line([(cx - 40, cy + 8), (cx - 9, cy - 15), (cx + 21, cy - 35), (cx + 51, cy - 68)], fill="#EF4444", width=4)
        draw.polygon([(cx + 51, cy - 75), (cx + 43, cy - 64), (cx + 59, cy - 66)], fill="#EF4444")
    elif any(k in text for k in ["box", "crate", "raw data", "data", "datum", "record", "document"]):
        # 📦 3D Delivery Crate with popping documents
        draw.polygon([(cx, cy - 50), (cx + 50, cy - 25), (cx, cy), (cx - 50, cy - 25)], fill="#FBBF24", outline="#D97706", width=2)
        draw.polygon([(cx - 50, cy - 25), (cx, cy), (cx, cy + 45), (cx - 50, cy + 20)], fill="#D97706", outline="#B45309", width=2)
        draw.polygon([(cx, cy), (cx + 50, cy - 25), (cx + 50, cy + 20), (cx, cy + 45)], fill="#B45309", outline="#92400E", width=2)
        draw.rectangle([cx - 22, cy - 48, cx + 22, cy - 15], fill="#FFFFFF", outline="#CBD5E1")
        draw.line([(cx - 14, cy - 38), (cx + 14, cy - 38)], fill="#64748B", width=2)
        draw.line([(cx - 14, cy - 30), (cx + 10, cy - 30)], fill="#64748B", width=2)
    elif any(k in text for k in ["sign", "decision", "choice", "road", "path", "solution"]):
        # 🧭 Crossroads Directional Signpost
        draw.rectangle([cx - 8, cy - 65, cx + 8, cy + 50], fill="#78350F")
        draw.polygon([(cx - 80, cy - 50), (cx + 15, cy - 50), (cx + 25, cy - 30), (cx + 15, cy - 10), (cx - 80, cy - 10), (cx - 90, cy - 30)], fill="#22C55E", outline="#15803D", width=2)
        draw.polygon([(cx - 15, cy - 10), (cx + 80, cy - 10), (cx + 90, cy + 10), (cx + 80, cy + 30), (cx - 15, cy + 30), (cx - 25, cy + 10)], fill="#3B82F6", outline="#1D4ED8", width=2)
    elif any(k in text for k in ["crystal", "future", "predict", "ball", "forecast", "orb"]):
        # 🔮 Mystical Glowing Crystal Ball
        draw.ellipse([cx - 45, cy - 55, cx + 45, cy + 35], fill="#818CF8", outline="#4338CA", width=3)
        draw.ellipse([cx - 28, cy - 38, cx + 8, cy], fill="#C7D2FE")
        draw.polygon([(cx - 35, cy + 48), (cx + 35, cy + 48), (cx + 20, cy + 32), (cx - 20, cy + 32)], fill="#F59E0B", outline="#B45309", width=2)
        draw.ellipse([cx - 25, cy + 28, cx + 25, cy + 38], fill="#FCD34D")
    elif any(k in text for k in ["robot", "machine learning", "ai", "neural", "autom"]):
        # 🤖 Friendly Modern Robot Head
        draw.line([(cx, cy - 45), (cx, cy - 65)], fill="#64748B", width=3)
        draw.ellipse([cx - 6, cy - 75, cx + 6, cy - 63], fill="#EF4444")
        draw.rounded_rectangle([cx - 45, cy - 45, cx + 45, cy + 25], radius=10, fill="#E2E8F0", outline="#64748B", width=2)
        draw.rounded_rectangle([cx - 35, cy - 35, cx + 35, cy + 5], radius=6, fill="#0F172A")
        draw.ellipse([cx - 25, cy - 25, cx - 10, cy - 10], fill="#38BDF8")
        draw.ellipse([cx + 10, cy - 25, cx + 25, cy - 10], fill="#38BDF8")
        draw.line([(cx - 15, cy + 15), (cx + 15, cy + 15)], fill="#10B981", width=3)
    elif any(k in text for k in ["science", "method", "experiment", "flask", "lab", "beaker", "chemist"]):
        # 🧪 Laboratory Conical Flask with Bubbles
        draw.polygon([(cx - 12, cy - 55), (cx + 12, cy - 55), (cx + 12, cy - 25), (cx + 45, cy + 35), (cx - 45, cy + 35), (cx - 12, cy - 25)], fill="#06B6D4", outline="#0E7490", width=2)
        draw.polygon([(cx - 8, cy - 55), (cx + 8, cy - 55), (cx + 8, cy - 25), (cx - 8, cy - 25)], fill="#FFFFFF", outline="#0E7490")
        draw.ellipse([cx - 12, cy + 5, cx - 4, cy + 13], fill="#FFFFFF")
        draw.ellipse([cx + 14, cy - 5, cx + 20, cy + 1], fill="#FFFFFF")
        draw.ellipse([cx - 4, cy - 15, cx + 4, cy - 7], fill="#FFFFFF")
    else:
        # 💡 Radiant Glowing Lightbulb with Energy Rays
        draw.ellipse([cx - 35, cy - 55, cx + 35, cy + 10], fill="#FBBF24", outline="#F59E0B", width=2)
        draw.rectangle([cx - 18, cy + 8, cx + 18, cy + 28], fill="#94A3B8", outline="#64748B")
        draw.ellipse([cx - 12, cy + 24, cx + 12, cy + 34], fill="#64748B")
        draw.line([(cx - 50, cy - 22), (cx - 65, cy - 22)], fill="#F59E0B", width=3)
        draw.line([(cx + 50, cy - 22), (cx + 65, cy - 22)], fill="#F59E0B", width=3)
        draw.line([(cx, cy - 65), (cx, cy - 80)], fill="#F59E0B", width=3)


def generate_mnemonic_photo_card(concept: str, visual_object: str, emoji: str, location: str, topic: str, difficulty: str = "Medium", reason: str = "") -> bytes:
    """
    Generates a standalone, high-res illustrated visual mnemonic photo card (1000x680) in PNG format.
    Works 100% offline with zero external dependencies, providing vivid spatial cards.
    Fully wraps all anchor descriptions and memory explanations so no sentences are truncated.
    """
    width, height = 1000, 680
    img = Image.new("RGB", (width, height), color="#FFFFFF")
    draw = ImageDraw.Draw(img)

    # 1. Subtle Background Gradient & Border
    for y in range(height):
        r = int(248 - (y / height) * 10)
        g = int(250 - (y / height) * 8)
        b = int(252 + (y / height) * 3)
        draw.line([(0, y), (width, y)], fill=(r, g, b))

    # Outer decorative card border
    draw.rounded_rectangle([15, 15, width - 15, height - 15], radius=24, outline="#CBD5E1", width=3)

    # Fonts
    f_header = get_card_font(26, bold=True)
    f_subhead = get_card_font(20, bold=False)
    f_concept = get_card_font(36, bold=True)
    f_object = get_card_font(22, bold=True)
    f_reason = get_card_font(19, bold=False)
    f_footer = get_card_font(17, bold=False)

    # 2. Top Location Banner (Clean text header, no missing emoji glyph box)
    draw.rounded_rectangle([40, 36, width - 40, 110], radius=16, fill="#4553E8")
    draw.text((65, 54), f"LOCUS STATION: {location.upper()}", fill="#FFFFFF", font=f_header)
    draw.text((width - 65, 73), f"DISCIPLINE: {topic.upper()}", fill="#E0E7FF", font=f_subhead, anchor="rm")

    # 3. Central Focal Frame
    draw.rounded_rectangle([40, 126, width - 40, 545], radius=18, fill="#FFFFFF", outline="#E2E8F0", width=2)

    # Decorative spotlight background
    draw.ellipse([width // 2 - 110, 138, width // 2 + 110, 328], fill="#F8FAFC", outline="#E2E8F0", width=2)

    # Themed Vector Illustration
    draw_mnemonic_illustration(draw, width // 2, 233, concept, visual_object)

    # Concept Title (Large, clear, prominent)
    clean_concept = str(concept).strip()
    draw.text((width // 2, 352), clean_concept, fill="#1F2937", font=f_concept, anchor="mm")

    # Visual Anchor Token - Multi-line wrap so nothing is truncated
    clean_obj = f"Anchor: {visual_object}"
    obj_lines = textwrap.wrap(clean_obj, width=50) or [clean_obj]
    cur_y = 388
    for line in obj_lines:
        draw.text((width // 2, cur_y), line, fill="#0D9488", font=f_object, anchor="mm")
        cur_y += 28

    # Meaning / Explanation - Multi-line wrap so complete sentence is preserved
    display_reason = reason.strip() if reason else f"Mental landmark to fix {clean_concept} in memory."
    quote_text = f'"{display_reason}"'
    reason_lines = textwrap.wrap(quote_text, width=58) or [quote_text]
    cur_y += 6
    for line in reason_lines:
        draw.text((width // 2, cur_y), line, fill="#4B5563", font=f_reason, anchor="mm")
        cur_y += 25

    # 4. Bottom Concept Details
    draw.rounded_rectangle([40, 565, width - 40, 650], radius=16, fill="#F8FAFC", outline="#E2E8F0", width=1)
    diff_color = "#DC2626" if difficulty == "Hard" else ("#D97706" if difficulty == "Medium" else "#16A34A")
    draw.text((70, 584), f"Cognitive Difficulty: {difficulty}", fill=diff_color, font=f_footer)
    draw.text((70, 614), "Method of Loci (Memory Palace) Associative Anchor", fill="#4B5563", font=f_footer)

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    return buffer.getvalue()
