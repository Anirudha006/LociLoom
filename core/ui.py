"""
LociLoom UI & Theme Helper (core/ui.py)
Provides unified CSS loading, custom sidebar rendering, accessible theme controls,
and Loci ID sanitization matching assets/website_home.html.
"""
import os
import re
import uuid
from typing import Optional, Dict, Any, List
import streamlit as st
from core.db import get_or_create_user, authenticate_user, register_account
from core.i18n import t

CSS_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets", "style.css")


def format_loci_id(raw_id: Optional[str]) -> str:
    """
    Cleans and formats a Loci ID or user ID.
    Strips any stray ISO timezone or timestamp suffixes like '-0:00', '+00:00', ':00', or fractions.
    Guarantees clean presentation (e.g., 'LL-LOCI-6C25-D9', never 'LL-LOCI-6C25-D9-0:00').
    """
    if not raw_id:
        return "LL-ANON-0000"
    s = str(raw_id).strip()
    # Remove timezone offset suffixes like -0:00, +00:00, -05:00
    s = re.sub(r'[-+][0-9]{1,2}:[0-9]{2}$', '', s)
    # Remove minute/second offsets like :00:00 or :00
    s = re.sub(r':[0-9]{2}(:[0-9]{2})?$', '', s)
    # Remove fraction seconds like .123456
    s = re.sub(r'\.[0-9]+$', '', s)
    # Remove trailing dashes or colons or whitespace
    s = s.rstrip("-: ")
    return s.upper()


def get_or_init_anon_id() -> str:
    """Generates and persists an anonymous student ID (e.g. LL-ABCD-1234)."""
    if "anon_id" not in st.session_state:
        raw = uuid.uuid4().hex[:8].upper()
        anon_id = f"LL-{raw[:4]}-{raw[4:]}"
        st.session_state["anon_id"] = anon_id
        get_or_create_user(anon_id)
    return st.session_state["anon_id"]


def init_accessibility_state():
    """Initializes user customization and accessibility preferences in session state."""
    defaults = {
        "language": "en",
        "font_size": 16,
        "dyslexia_font": False,
        "high_contrast": False,
        "reduced_motion": False,
        "text_only_mode": False,
        "voice_speed": 1.0,
        "use_llm": False,
        "audio_enabled": True
    }
    for k, v in defaults.items():
        if k not in st.session_state:
            st.session_state[k] = v


def load_css():
    """
    Loads assets/style.css, Google Fonts link, and applies dynamic accessibility rules.
    This fulfills the requirement to load styles once from a helper without large inline blocks.
    """
    font_link = (
        "<link rel='preconnect' href='https://fonts.googleapis.com'>"
        "<link rel='preconnect' href='https://fonts.gstatic.com' crossorigin>"
        "<link href='https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&"
        "family=Plus+Jakarta+Sans:wght@400;500;600;700&family=Noto+Sans+Devanagari:wght@500;600;700&"
        "family=Noto+Sans+Kannada:wght@500;600;700&family=Material+Symbols+Rounded:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&"
        "family=Material+Symbols+Outlined:opsz,wght,FILL,GRAD@20..48,100..700,0..1,-50..200&display=swap' rel='stylesheet'>"
    )
    st.markdown(font_link, unsafe_allow_html=True)

    css_content = ""
    if os.path.exists(CSS_PATH):
        with open(CSS_PATH, "r", encoding="utf-8") as f:
            css_content = f.read()

    font_size = st.session_state.get("font_size", 16)
    dyslexia = st.session_state.get("dyslexia_font", False)
    contrast = st.session_state.get("high_contrast", False)
    motion = st.session_state.get("reduced_motion", False)

    dynamic_rules = [f"html, body, p, span:not([data-testid*='Icon']):not([class*='material']) {{ font-size: {font_size}px !important; }}"]
    if dyslexia:
        dynamic_rules.append(
            "body, p, h1, h2, h3, h4, label, input, textarea, select, button, "
            "[data-testid='stMarkdownContainer'] p, span:not([data-testid*='Icon']):not([class*='material']) "
            "{ font-family: 'OpenDyslexic', 'Comic Sans MS', Verdana, sans-serif !important; "
            "letter-spacing: 0.04em !important; word-spacing: 0.08em !important; }"
        )
    if contrast:
        dynamic_rules.append(
            "* { color: #000000 !important; border-color: #000000 !important; } "
            ".lociloom-card, .location-card, .hm-tile { border: 2px solid #000000 !important; box-shadow: none !important; }"
        )
    if motion:
        dynamic_rules.append(
            "*, *::before, *::after, .hm-march, .hm-stop, .hm-ring, .hm-pill, .ll-route, .ll-ring, .ll-pill "
            "{ animation: none !important; transition: none !important; } "
            ".hm-walker, .ll-walker { display: none !important; } "
            ".hm-pill { opacity: 1 !important; transform: none !important; }"
        )

    dynamic_rules.append(
        "[data-testid='stExpanderIcon'], [data-testid='stIconMaterial'], [data-testid*='Icon'], "
        "[data-testid*='icon'], [data-testid='stExpanderToggleIcon'], .material-symbols-rounded, "
        ".material-symbols-outlined, .material-icons, span.material-symbols-rounded, "
        "span.material-symbols-outlined, details summary span[data-testid*='Icon'], "
        "[data-testid='stFileUploader'] [data-testid*='Icon'], [data-testid='stStatusWidget'] [data-testid*='Icon'] { "
        "font-family: 'Material Symbols Rounded', 'Material Symbols Outlined', 'Material Icons', sans-serif !important; "
        "font-weight: normal !important; font-style: normal !important; display: inline-block !important; "
        "white-space: nowrap !important; line-height: 1 !important; letter-spacing: normal !important; "
        "-webkit-font-feature-settings: 'liga' 1 !important; font-feature-settings: 'liga' 1 !important; }"
    )

    full_css = f"<style>{css_content} {' '.join(dynamic_rules)}</style>"
    safe_css = " ".join([line.strip() for line in full_css.splitlines() if line.strip()])
    st.markdown(safe_css, unsafe_allow_html=True)


def inject_theme_css():
    """Alias for load_css() for backwards compatibility with existing pages."""
    load_css()


def setup_page(title: str, icon: str = "🏛️", hide_sidebar: bool = False):
    """Global page initializer called at top of each page."""
    try:
        st.set_page_config(
            page_title=f"{title} | LociLoom",
            page_icon=icon,
            layout="wide",
            initial_sidebar_state="collapsed" if hide_sidebar else "expanded"
        )
    except Exception:
        pass

    get_or_init_anon_id()
    init_accessibility_state()
    load_css()

    if not hide_sidebar:
        render_sidebar()
    else:
        sb_hide_css = (
            "<style>"
            "[data-testid='stSidebar'], [data-testid='stSidebarNav'], [data-testid='collapsedControl'], "
            "[data-testid='stSidebarCollapsedControl'], [data-testid='stSidebarCollapseButton'], "
            "section[data-testid='stSidebar'], button[data-testid='stSidebarCollapseButton'], "
            "button[kind='header'] { display: none !important; visibility: hidden !important; width: 0 !important; "
            "min-width: 0 !important; max-width: 0 !important; opacity: 0 !important; pointer-events: none !important; "
            "position: fixed !important; left: -9999px !important; top: -9999px !important; } "
            ".main, [data-testid='stAppViewContainer'] > .main, [data-testid='stMain'] { margin-left: 0 !important; "
            "padding-left: 0 !important; width: 100% !important; } "
            "</style>"
        )
        st.markdown(sb_hide_css, unsafe_allow_html=True)


def sign_out_user():
    """
    Completely logs out the current user:
    - Clears authenticated session state
    - Generates a fresh anonymous guest ID
    - Clears active in-progress memory palaces and quizzes
    - Switches page directly to app.py (the Login / Onboarding portal)
    """
    if "auth_user" in st.session_state:
        del st.session_state["auth_user"]
    st.session_state["anon_id"] = f"LL-GUEST-{uuid.uuid4().hex[:4].upper()}"
    for k in ["current_palace", "quiz_palace", "quiz_deck", "quiz_idx", "answered_current"]:
        if k in st.session_state:
            del st.session_state[k]
    try:
        st.switch_page("app.py")
    except Exception:
        st.rerun()


def render_sidebar():
    """
    Renders custom sidebar matching assets/website_home.html:
    - Logo + 'Adaptive Memory Palace Generator' subtitle
    - Green-tinted STUDENT PORTAL card with clean ID (no '-0:00' suffix)
    - Prominent Sign out button directly visible without scrolling
    - Navigation list using st.page_link with icons (active highlighted in light indigo)
    - Language selector with i18n
    - Concept extraction hint
    - Secondary Sign out button at bottom
    """
    with st.sidebar:
        # 1. Header Brand & Subtitle
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 12px; padding: 10px 4px 18px 4px;">
            <svg width="40" height="40" viewBox="0 0 40 40" role="img" aria-label="LociLoom logo">
                <rect width="40" height="40" rx="12" fill="#4553E8"/>
                <path d="M11 28 C11 20 18 22 20 17 C22 12 29 14 29 12" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="1 5"/>
                <circle cx="11" cy="28" r="3.5" fill="#FFFFFF"/>
                <circle cx="29" cy="12" r="3.5" fill="#FBBF24"/>
            </svg>
            <div style="display: flex; flex-direction: column;">
                <span style="font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 22px; letter-spacing: -0.02em; line-height: 1.1; color: #1F2937;">LociLoom</span>
                <span style="font-size: 12px; color: #4B5563;">Adaptive Memory Palace Generator</span>
            </div>
        </div>
        """, unsafe_allow_html=True)

        # 2. Green-tinted STUDENT PORTAL card
        auth_user = st.session_state.get("auth_user")
        is_admin = bool(auth_user and auth_user.get("role") == "admin")
        portal_label = "ADMINISTRATOR PORTAL" if is_admin else "STUDENT PORTAL"

        if auth_user:
            display_user = auth_user.get("username", "Student")
            raw_id = auth_user.get("user_id", "")
        else:
            anon_id = st.session_state.get("anon_id", "LL-GUEST")
            display_user = "guest"
            raw_id = anon_id

        clean_id = format_loci_id(raw_id)

        st.markdown(f"""
        <div style="background: #ECFDF9; border: 1.5px solid #99E6D8; border-radius: 16px; padding: 14px 16px; display: flex; flex-direction: column; gap: 4px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 11px; font-weight: 700; letter-spacing: 0.1em; color: #0B5F57;">{portal_label}</span>
                <span style="font-size: 11px; color: #0D9488; font-weight: 600;">Active</span>
            </div>
            <span style="font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 20px; letter-spacing: 0.04em; color: #1F2937;">{display_user}</span>
            <span style="font-size: 12px; color: #4B5563;">ID: {clean_id}</span>
        </div>
        """, unsafe_allow_html=True)

        # Prominent Top Sign Out Button (always visible without scrolling)
        if st.button("🚪 Sign out", key="sb_top_signout_btn", use_container_width=True):
            sign_out_user()

        # 3. Navigation List using st.page_link
        st.markdown("<nav aria-label='Main navigation' style='margin-top: 10px;'>", unsafe_allow_html=True)
        nav_items = [
            ("app.py", "Home", "🏠"),
            ("pages/1_Create_Palace.py", "Create Palace", "✨"),
            ("pages/2_My_Palaces.py", "My Palaces", "🏛️"),
            ("pages/3_Practice_Quiz.py", "Practice Quiz", "🎯"),
            ("pages/4_Revision_Planner.py", "Revision Planner", "📅"),
            ("pages/5_Dashboard.py", "Dashboard", "📊"),
            ("pages/6_Experiment_Mode.py", "Experiment Mode", "🧪"),
            ("pages/7_Settings_Accessibility.py", "Settings & Accessibility", "⚙️"),
            ("pages/8_About_and_Help.py", "About & Help", "ℹ️"),
        ]
        if is_admin:
            nav_items.append(("pages/9_Admin_Portal.py", "Admin Portal", "🛡️"))

        for page_path, label, icon in nav_items:
            st.page_link(page_path, label=label, icon=icon)
        st.markdown("</nav>", unsafe_allow_html=True)

        # 4. Bottom Controls: Language selector + Info note + Bottom Sign out
        st.markdown("<div style='margin-top: 16px;'></div>", unsafe_allow_html=True)
        st.markdown("<label style='font-size: 13px; font-weight: 600; color: #1F2937; margin-bottom: 4px;'>Interface language</label>", unsafe_allow_html=True)
        lang_options = {"en": "English", "hi": "हिन्दी (Hindi)", "kn": "ಕನ್ನಡ (Kannada)"}
        curr_lang = st.session_state.get("language", "en")
        selected_lang = st.selectbox(
            "Interface language",
            options=list(lang_options.keys()),
            format_func=lambda x: lang_options[x],
            index=list(lang_options.keys()).index(curr_lang) if curr_lang in lang_options else 0,
            key="sb_ui_lang",
            label_visibility="collapsed"
        )
        if selected_lang != curr_lang:
            st.session_state["language"] = selected_lang
            st.rerun()

        st.markdown("<p style='margin: 6px 0 12px 0; font-size: 12px; line-height: 1.5; color: #4B5563;'>Concept extraction works best for English input.</p>", unsafe_allow_html=True)

        if st.button("🚪 Sign out", key="sb_signout_btn", use_container_width=True):
            sign_out_user()

        st.markdown(
            "<div style='text-align: center; margin-top: 14px; font-size: 11px; color: #9CA3AF;'>"
            "🚀 <strong>LociLoom v1.2</strong> • Gemini 3.x Flash"
            "</div>",
            unsafe_allow_html=True
        )


def get_animated_sample_map_html(reduced_motion: bool = False) -> str:
    """
    Renders the sample palace floor-plan route map matching assets/website_home.html.
    Disables walking animation and marker when reduced_motion is True.
    """
    motion_css = ""
    if reduced_motion:
        motion_css = """
        .hm-march, .hm-stop, .hm-ring, .hm-pill { animation: none !important; }
        .hm-pill { opacity: 1 !important; transform: none !important; }
        .hm-walker { display: none !important; }
        """

    return f"""<!doctype html>
<html>
<head>
<meta charset="utf-8">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Bricolage+Grotesque:opsz,wght@12..96,600;12..96,700&family=Plus+Jakarta+Sans:wght@500;600;700&display=swap" rel="stylesheet">
<style>
:root {{
    --primary: #4553E8;
    --primary-dark: #3441CF;
    --ink: #1F2937;
    --muted: #4B5563;
    --line: #D5D9E6;
    --bg: #F7F8FC;
}}
* {{ box-sizing: border-box; }}
body {{
    margin: 0;
    padding: 6px;
    background: transparent;
    font-family: 'Plus Jakarta Sans', system-ui, sans-serif;
    color: var(--ink);
}}
aside {{
    background: #EEF0FF;
    border-radius: 24px;
    padding: 22px 20px;
    display: flex;
    flex-direction: column;
    gap: 14px;
    justify-content: center;
}}
.chip {{
    align-self: flex-start;
    padding: 5px 12px;
    border-radius: 999px;
    background: #FFFFFF;
    color: var(--primary-dark);
    font-size: 12px;
    font-weight: 700;
}}
h2 {{
    margin: 4px 0 0;
    font-family: 'Bricolage Grotesque', system-ui, sans-serif;
    font-weight: 700;
    font-size: 20px;
    line-height: 1.18;
    letter-spacing: -0.02em;
    color: #1F2937;
}}
.map {{
    background: #FFFFFF;
    border-radius: 18px;
    padding: 10px;
    box-shadow: 0 8px 24px rgba(69,83,232,0.10);
}}
.map svg {{
    display: block;
    width: 100%;
    height: auto;
}}
p.story {{
    margin: 0;
    font-size: 13px;
    line-height: 1.55;
    color: #374151;
}}

@keyframes hm-march {{ to {{ stroke-dashoffset: -22; }} }}
@keyframes hm-pop {{ 0%, 100% {{ transform: scale(1); }} 50% {{ transform: scale(1.18); }} }}
@keyframes hm-ring1 {{ 0% {{ r: 17; opacity: .55; }} 12% {{ r: 34; opacity: 0; }} 13%, 100% {{ r: 17; opacity: 0; }} }}
@keyframes hm-ring2 {{ 0%, 30% {{ r: 17; opacity: 0; }} 31% {{ opacity: .55; }} 43% {{ r: 34; opacity: 0; }} 44%, 100% {{ r: 17; opacity: 0; }} }}
@keyframes hm-ring3 {{ 0%, 57% {{ r: 17; opacity: 0; }} 58% {{ opacity: .55; }} 70% {{ r: 34; opacity: 0; }} 71%, 100% {{ r: 17; opacity: 0; }} }}
@keyframes hm-ring4 {{ 0%, 89% {{ r: 17; opacity: 0; }} 90% {{ opacity: .55; }} 100% {{ r: 36; opacity: 0; }} }}
@keyframes hm-pill2 {{ 0%, 29% {{ opacity: .18; transform: translateY(6px); }} 35%, 96% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: .18; transform: translateY(6px); }} }}
@keyframes hm-pill3 {{ 0%, 56% {{ opacity: .18; transform: translateY(6px); }} 62%, 96% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: .18; transform: translateY(6px); }} }}
@keyframes hm-pill4 {{ 0%, 88% {{ opacity: .18; transform: translateY(6px); }} 94%, 97% {{ opacity: 1; transform: translateY(0); }} 100% {{ opacity: .18; transform: translateY(6px); }} }}

.hm-march {{ stroke-dasharray: 2 9; animation: hm-march 1.2s linear infinite; }}
.hm-stop {{ transform-box: fill-box; transform-origin: center; animation: hm-pop 3s ease-in-out infinite; }}
.hm-ring {{ fill: #4553E8; opacity: 0; animation-duration: 9s; animation-iteration-count: infinite; animation-timing-function: ease-out; }}
.hm-ring1 {{ animation-name: hm-ring1; }}
.hm-ring2 {{ animation-name: hm-ring2; }}
.hm-ring3 {{ animation-name: hm-ring3; }}
.hm-ring4 {{ fill: #D97706; animation-name: hm-ring4; }}
.hm-pill {{ animation-duration: 9s; animation-iteration-count: infinite; animation-timing-function: ease-out; }}
.hm-pill2 {{ animation-name: hm-pill2; }}
.hm-pill3 {{ animation-name: hm-pill3; }}
.hm-pill4 {{ animation-name: hm-pill4; }}

@media (prefers-reduced-motion: reduce) {{
    .hm-march, .hm-stop, .hm-ring, .hm-pill {{ animation: none !important; }}
    .hm-pill {{ opacity: 1 !important; transform: none !important; }}
    .hm-walker {{ display: none !important; }}
}}
{motion_css}
</style>
</head>
<body>
<aside>
    <div>
        <span class="chip">Sample palace · Photosynthesis</span>
        <h2>Notes become a route you can walk in your mind.</h2>
    </div>
    <div class="map">
        <svg viewBox="0 0 520 400" width="100%" role="img" aria-label="Floor plan of a memory palace with four numbered stops: front gate, living room, kitchen and garden">
            <rect x="0" y="0" width="520" height="400" rx="14" fill="#FBFCFF"/>
            <rect x="28" y="236" width="146" height="140" rx="14" fill="#FEF3C7"/>
            <rect x="180" y="236" width="172" height="140" rx="14" fill="#E0E7FF"/>
            <rect x="180" y="92" width="172" height="138" rx="14" fill="#DBEAFE"/>
            <rect x="358" y="92" width="134" height="284" rx="14" fill="#CCFBEF"/>
            <g font-family="Plus Jakarta Sans, sans-serif" font-size="11" font-weight="700" fill="#374151" letter-spacing="0.08em">
                <text x="42" y="260">FRONT GATE</text>
                <text x="194" y="260">LIVING ROOM</text>
                <text x="194" y="116">KITCHEN</text>
                <text x="372" y="116">GARDEN</text>
            </g>
            <path class="hm-march" d="M100 304 L266 304 L266 164 L425 230" fill="none" stroke="#4553E8" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
            <circle class="hm-ring hm-ring1" cx="100" cy="304" r="17"/>
            <circle class="hm-ring hm-ring2" cx="266" cy="304" r="17"/>
            <circle class="hm-ring hm-ring3" cx="266" cy="164" r="17"/>
            <circle class="hm-ring hm-ring4" cx="425" cy="230" r="17"/>
            <g font-family="Plus Jakarta Sans, sans-serif" font-size="12" font-weight="600" fill="#1F2937" text-anchor="middle">
                <g><rect x="34" y="332" width="132" height="28" rx="14" fill="#FFFFFF"/><text x="100" y="351">Sunlight · sunglasses</text></g>
                <g class="hm-pill hm-pill2"><rect x="196" y="332" width="140" height="28" rx="14" fill="#FFFFFF"/><text x="266" y="351">Water · bottle</text></g>
                <g class="hm-pill hm-pill3"><rect x="196" y="186" width="140" height="28" rx="14" fill="#FFFFFF"/><text x="266" y="205">CO₂ · balloon</text></g>
                <g class="hm-pill hm-pill4"><rect x="364" y="256" width="122" height="28" rx="14" fill="#FFFFFF"/><text x="425" y="275">Glucose · sugar</text></g>
            </g>
            <g font-family="Bricolage Grotesque, sans-serif" font-size="15" font-weight="700" fill="#FFFFFF" text-anchor="middle">
                <circle cx="100" cy="304" r="17" fill="#4553E8"/><text x="100" y="310">1</text>
                <circle cx="266" cy="304" r="17" fill="#4553E8"/><text x="266" y="310">2</text>
                <circle cx="266" cy="164" r="17" fill="#4553E8"/><text x="266" y="170">3</text>
                <circle cx="425" cy="230" r="17" fill="#D97706"/><text x="425" y="236">4</text>
            </g>
            <g class="hm-walker">
                <circle r="11" fill="#FBBF24" stroke="#FFFFFF" stroke-width="3"/>
                <circle r="3.5" fill="#92400E"/>
                <animateMotion dur="9s" repeatCount="indefinite" path="M100 304 L266 304 L266 164 L425 230" keyPoints="0;1;1" keyTimes="0;0.9;1" calcMode="linear"/>
            </g>
        </svg>
    </div>
    <p class="story">
        <strong style="color: #1F2937;">The story:</strong> At the front gate, a plant in sunglasses waves at a water bottle. In the kitchen, a balloon floats in, and the garden fills with sugar cubes.
    </p>
</aside>
</body>
</html>"""


def get_animated_login_map_html() -> str:
    """Returns the animated route map used on the login screen."""
    motion = st.session_state.get("reduced_motion", False)
    return get_animated_sample_map_html(reduced_motion=motion)


def render_disclaimer():
    """Renders the standard research study disclaimer footer."""
    lang = st.session_state.get("language", "en")
    disc_text = t("disclaimer", lang)
    st.markdown(f"""
    <div class="disclaimer-box">
        <strong>⚠️ Important Notice:</strong> {disc_text}
    </div>
    """, unsafe_allow_html=True)


def page_header(title: str, subtitle: str = ""):
    """Renders standard page title and subtitle."""
    st.markdown(f"## {title}")
    if subtitle:
        st.caption(subtitle)


def card(content: str):
    """Renders a styled card container."""
    st.markdown(f"""
    <div class="lociloom-card" style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 12px; padding: 18px 24px; margin-bottom: 16px;">
        {content}
    </div>
    """, unsafe_allow_html=True)


def info_banner(text: str):
    """Renders an info banner."""
    st.info(text)


def footer():
    """Renders standard footer."""
    render_disclaimer()
