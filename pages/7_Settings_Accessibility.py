"""
LociLoom Page 7: Settings & Accessibility Controls
Provides comprehensive accessibility accommodations and personalization:
- Font size adjustments (12px to 24px)
- High-contrast light mode toggle
- Dyslexia-friendly typography toggle (OpenDyslexic / Comic Sans MS fallback)
- Reduced motion toggle (disables animations and transitions)
- Non-visual Text-Only Route Mode for aphantasic students or screen-reader users
- Interface language selector (English, Hindi, Kannada)
- Audio narration preferences (voice speed, enable/disable)
- Optional, disabled-by-default LLM setting
- Complete local database reset with confirmation
"""
import streamlit as st
from core.ui_helper import setup_page, render_disclaimer
from core.db import reset_all_data, update_user_settings
from core.i18n import t

setup_page(title="Settings & Accessibility", icon="⚙️")
anon_id = st.session_state.get("anon_id", "LL-GUEST")
lang = st.session_state.get("language", "en")

st.markdown("## ⚙️ Settings & Inclusive Accessibility")
st.caption("Personalize readability, visual accommodations, auditory narration, and privacy controls.")

# --- ACCESSIBILITY CONTROLS ---
st.markdown("### 👁️ Visual & Cognitive Accommodations")
acc_col1, acc_col2 = st.columns(2)

with acc_col1:
    font_size = st.slider(
        "Base Font Size (px)",
        min_value=12,
        max_value=24,
        value=st.session_state.get("font_size", 16),
        step=1,
        help="Adjusts reading text size across all pages."
    )
    if font_size != st.session_state.get("font_size"):
        st.session_state["font_size"] = font_size
        st.rerun()

    dyslexia = st.checkbox(
        "📖 Dyslexia-Friendly Typography",
        value=st.session_state.get("dyslexia_font", False),
        help="Applies high-legibility weighted typography with increased letter and word spacing."
    )
    if dyslexia != st.session_state.get("dyslexia_font"):
        st.session_state["dyslexia_font"] = dyslexia
        st.rerun()

with acc_col2:
    high_contrast = st.checkbox(
        "🌓 High-Contrast Light Mode",
        value=st.session_state.get("high_contrast", False),
        help="Maximizes text-to-background contrast with crisp borders (WCAG AAA compliant)."
    )
    if high_contrast != st.session_state.get("high_contrast"):
        st.session_state["high_contrast"] = high_contrast
        st.rerun()

    reduced_motion = st.checkbox(
        "⏸️ Reduced Motion (Disable Animations)",
        value=st.session_state.get("reduced_motion", False),
        help="Turns off CSS transitions and route path animations for vestibular sensitivity."
    )
    if reduced_motion != st.session_state.get("reduced_motion"):
        st.session_state["reduced_motion"] = reduced_motion
        st.rerun()

# --- NON-VISUAL & TEXT-ONLY MODE ---
st.markdown("### 🦻 Non-Visual & Aphantasia Mode")
st.markdown("""
<div class="lociloom-card">
    <p style="margin: 0 0 8px 0; font-size: 0.92rem; color: #4B5563;">
        Some learners experience <em>aphantasia</em> (the inability to voluntarily visualize mental imagery) 
        or navigate via screen readers. <strong>Text-Only Route Mode</strong> replaces visual map diagrams 
        with rich verbal acoustic and descriptive textual guides.
    </p>
</div>
""", unsafe_allow_html=True)

text_only = st.checkbox(
    "📝 Enable Text-Only Route Mode",
    value=st.session_state.get("text_only_mode", False),
    help="Displays sequential textual descriptions and audio narration instead of 2D floorplans."
)
if text_only != st.session_state.get("text_only_mode"):
    st.session_state["text_only_mode"] = text_only
    st.rerun()

# --- AUDIO & NARRATION SETTINGS ---
st.markdown("### 🔊 Audio & Speech Settings")
aud_col1, aud_col2 = st.columns(2)

with aud_col1:
    audio_enabled = st.checkbox(
        "Enable Audio Features",
        value=st.session_state.get("audio_enabled", True),
        help="Enables MP3 generation and browser speech synthesis buttons."
    )
    st.session_state["audio_enabled"] = audio_enabled

with aud_col2:
    voice_speed = st.slider(
        "Narration Speed",
        min_value=0.75,
        max_value=1.5,
        value=float(st.session_state.get("voice_speed", 1.0)),
        step=0.05,
        help="Adjusts speech rate for browser voice read-aloud."
    )
    st.session_state["voice_speed"] = voice_speed

# --- LANGUAGE PREFERENCES ---
st.markdown("### 🌐 Language & Localization")
lang_col1, lang_col2 = st.columns([1, 1])

with lang_col1:
    lang_map = {"en": "English", "hi": "Hindi (हिंदी)", "kn": "Kannada (ಕನ್ನಡ)"}
    curr_l = st.session_state.get("language", "en")
    new_lang = st.selectbox(
        "Application Interface Language",
        options=list(lang_map.keys()),
        format_func=lambda x: lang_map[x],
        index=list(lang_map.keys()).index(curr_l) if curr_l in lang_map else 0
    )
    if new_lang != curr_l:
        st.session_state["language"] = new_lang
        st.rerun()

with lang_col2:
    st.info("ℹ️ " + t("nlp_note", st.session_state.get("language", "en")))

# --- OPTIONAL DISABLED-BY-DEFAULT LLM SETTING ---
st.markdown("### 🤖 Cognitive AI Engine Mode")
st.markdown("""
<div class="lociloom-card">
    <div style="font-weight: 700; color: #1F2937; margin-bottom: 4px;">Generation Engine Architecture:</div>
    <p style="color: #6B7280; font-size: 0.88rem; margin: 0 0 10px 0;">
        By default, LociLoom operates <strong>100% offline</strong> using transparent, deterministic rule-based NLP,
        curated psycholinguistic dictionaries, and scikit-learn models. No remote API keys or GPU hardware are required.
    </p>
</div>
""", unsafe_allow_html=True)

llm_opt_in = st.checkbox(
    "Opt-in: Enable Experimental LLM Generation Hook (Disabled by default)",
    value=st.session_state.get("use_llm", False),
    help="Default is unchecked. Keeps all processing offline and deterministic."
)
st.session_state["use_llm"] = llm_opt_in

if llm_opt_in:
    st.warning("⚠️ LLM Mode is currently set to experimental simulation. The deterministic rule-based generator remains active.")

# --- DATA PRIVACY & RESET BUTTON ---
st.markdown("---")
st.markdown("### 🛡️ Privacy & Local Data Management")
st.markdown(f"""
Your anonymous identifier is **`{anon_id}`**. All generated memory palaces, quiz logs, and SM-2 schedules
are strictly contained in your local SQLite file (`data/lociloom.db`). No cloud databases or tracking analytics are used.
""")

with st.popover("🗑️ Reset All Local Data"):
    st.markdown("⚠️ **Are you sure?** This will permanently delete all saved palaces, quiz logs, and spaced repetition schedules.")
    if st.button("Confirm: Reset Everything", type="primary"):
        reset_all_data()
        st.success("All local database records have been wiped clean.")
        st.rerun()

render_disclaimer()
