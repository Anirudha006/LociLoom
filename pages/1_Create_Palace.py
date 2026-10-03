"""
LociLoom Page 1: Create Memory Palace
Orchestrates the entire cognitive pipeline:
Input Notes -> NLP Extraction -> Topic Classification -> Difficulty Prediction
-> Visual Mnemonic Mapping -> Palace Route Assignment -> Vivid Story Generation
-> 2D Interactive Animated Map -> Editable Preview -> SQLite Persistence
"""
import re
import streamlit as st
from core.ui_helper import setup_page, render_disclaimer
from core.nlp_extract import extract_key_concepts, sanitize_text
from core.topic_classifier import classify_topic
from core.difficulty_model import predict_difficulty
from core.visual_mapper import (
    map_concept_to_visual, generate_ai_photo_prompt, generate_mnemonic_photo_card
)
from core.palace_builder import (
    assign_concepts_to_palace, create_2d_route_figure, get_text_route_summary,
    render_infographic_storyboard_html, generate_infographic_image_bytes,
    format_palace_summary_text, create_palace_mindmap_figure
)
from core.story_generator import generate_palace_story
from core.tts import generate_speech_audio, get_browser_speech_html
from core.db import save_palace, get_palace_by_id
from core.i18n import t

setup_page(title="Create Palace", icon="✨")
lang = st.session_state.get("language", "en")
anon_id = st.session_state.get("anon_id", "LL-GUEST")

st.markdown("## ✨ Weave a New Memory Palace")
st.caption("Enter your study notes or select a curriculum example to generate an ordered, visual memory palace.")

# --- PRESET NOTES SAMPLES ---
PRESETS = {
    "Photosynthesis": (
        "Photosynthesis is the biological process used by green plants to convert light energy into chemical energy. "
        "Chlorophyll in the chloroplasts absorbs radiant sunlight while roots draw up water through xylem vessels. "
        "Carbon dioxide enters via microscopic stomata pores on leaves. "
        "Inside the thylakoid membrane, light reactions produce ATP and oxygen as a byproduct. "
        "The Calvin cycle then utilizes carbon dioxide and ATP to synthesize energy-rich glucose sugar."
    ),
    "Machine Learning": (
        "Machine Learning is a branch of artificial intelligence that enables computers to learn from data and make decisions without explicit programming. "
        "In the classroom, algorithms identify patterns in existing data and use them to solve new problems and make predictions. "
        "Three foundational paradigms exist: Supervised Learning from labeled examples, Unsupervised Learning finding hidden clusters, and Reinforcement Learning driven by reward feedback. "
        "Common algorithms include Linear Regression, Decision Trees, K-Nearest Neighbors, Support Vector Machines, and Neural Networks. "
        "Applications span recommendation systems, spam detection, image recognition, fraud detection, and self-driving vehicles. "
        "The standard process follows systematic steps: collect data, preprocess features, train a model, test and evaluate, and make predictions."
    ),
    "Water Cycle": (
        "The water cycle describes the continuous movement of water on, above, and below the surface of the Earth. "
        "Thermal energy from solar radiation causes evaporation from oceans, rivers, and lakes into invisible water vapor. "
        "Plants simultaneously release moisture into the atmosphere through transpiration. "
        "As warm vapor ascends into higher altitudes, cooling causes condensation into clouds of water droplets. "
        "When clouds become saturated, precipitation falls under gravity as rain, snow, or hail. "
        "Water then flows via surface runoff into streams and rivers, returning to collection reservoirs and groundwater aquifers."
    ),
    "TCP/IP Model": (
        "The TCP/IP model is the foundational four-layer architectural framework powering the modern internet. "
        "The Application layer interacts directly with software applications, handling protocols like HTTP, DNS, and SMTP. "
        "The Transport layer provides end-to-end communication services, sequencing packets using reliable TCP or connectionless UDP. "
        "The Internet layer handles logical IP addressing and packet routing across heterogeneous networks using the Internet Protocol. "
        "Finally, the Network-Access layer controls hardware data transmission across physical media like Ethernet cables and Wi-Fi radio frequencies."
    ),
    "Newton's Laws": (
        "Sir Isaac Newton formulated three fundamental physical laws governing classical mechanics and motion. "
        "Newton's First Law, known as the Law of Inertia, states that an object remains at rest or moves with constant velocity unless acted upon by a net external force. "
        "Newton's Second Law establishes that the acceleration of an object is directly proportional to net force and inversely proportional to its mass, summarized by F = ma. "
        "Newton's Third Law states that for every action force, there is an equal and opposite reaction force acting on interacting bodies."
    )
}

# Example buttons bar
st.markdown("**Try a verified curriculum example:**")
ex_col1, ex_col2, ex_col3, ex_col4, ex_col5 = st.columns(5)
default_text = ""

if "input_notes_text" not in st.session_state:
    st.session_state["input_notes_text"] = PRESETS["Photosynthesis"]

with ex_col1:
    if st.button("🌱 Photosynthesis", use_container_width=True):
        st.session_state["input_notes_text"] = PRESETS["Photosynthesis"]
        st.rerun()

with ex_col2:
    if st.button("🤖 Machine Learning", use_container_width=True):
        st.session_state["input_notes_text"] = PRESETS["Machine Learning"]
        st.rerun()

with ex_col3:
    if st.button("🌧️ Water Cycle", use_container_width=True):
        st.session_state["input_notes_text"] = PRESETS["Water Cycle"]
        st.rerun()

with ex_col4:
    if st.button("🌐 TCP/IP Model", use_container_width=True):
        st.session_state["input_notes_text"] = PRESETS["TCP/IP Model"]
        st.rerun()

with ex_col5:
    if st.button("🍎 Newton's Laws", use_container_width=True):
        st.session_state["input_notes_text"] = PRESETS["Newton's Laws"]
        st.rerun()

# --- INPUT AREA ---
col_in, col_opts = st.columns([1.6, 1.0])

with col_in:
    notes_input = st.text_area(
        "Primary Study Notes or Topic Text",
        value=st.session_state.get("input_notes_text", ""),
        height=160,
        max_chars=5000,
        help="Paste lecture slides, revision summaries, or textbook sections (up to 5,000 characters)."
    )

    extra_paragraph = st.text_area(
        "➕ Additional Paragraph / New Text Box (Optional)",
        value="",
        height=90,
        placeholder="Type or paste any extra paragraph or second section here to weave together...",
        help="Use this separate box to insert an additional paragraph or topic notes without erasing your primary notes."
    )
    
    # Optional file upload
    uploaded_file = st.file_uploader("Or upload notes from a plain text (.txt) file", type=["txt"])
    if uploaded_file is not None:
        try:
            file_text = uploaded_file.read().decode("utf-8")
            if file_text.strip():
                clean_f = sanitize_text(file_text)
                st.info(f"📄 File uploaded: {len(clean_f)} characters detected.")
                u_col1, u_col2 = st.columns(2)
                with u_col1:
                    if st.button("📥 Replace Primary Notes with File", use_container_width=True):
                        st.session_state["input_notes_text"] = clean_f
                        st.rerun()
                with u_col2:
                    if st.button("➕ Append File to Notes", use_container_width=True):
                        current_t = st.session_state.get("input_notes_text", "")
                        st.session_state["input_notes_text"] = (current_t.strip() + "\n\n" + clean_f).strip()
                        st.rerun()
        except Exception as e:
            st.error(f"Could not read text file: {e}")

    # Optional Voice Input (Browser SpeechRecognition API)
    with st.expander("🎙️ Voice Input (Dictate notes)"):
        st.markdown("""
        <div style="font-size: 0.85rem; color: #4B5563; margin-bottom: 8px;">
            Click <strong>Start Listening</strong> to dictate directly into your browser using Web Speech recognition:
        </div>
        <button id="voice-rec-btn" onclick="startDictation()" style="
            background-color: #14B8A6; color: white; border: none; padding: 6px 14px;
            font-size: 13px; font-weight: 600; border-radius: 6px; cursor: pointer;">
            🎤 Start Listening
        </button>
        <span id="voice-status" style="margin-left: 10px; font-size: 0.82rem; color: #6B7280;"></span>
        <script>
            function startDictation() {
                if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                    document.getElementById('voice-status').innerText = 'Speech recognition not supported in this browser.';
                    return;
                }
                const SpeechRec = window.SpeechRecognition || window.webkitSpeechRecognition;
                const rec = new SpeechRec();
                rec.lang = 'en-US';
                rec.interimResults = false;
                document.getElementById('voice-status').innerText = 'Listening... Speak clearly.';
                rec.onresult = function(event) {
                    const text = event.results[0][0].transcript;
                    document.getElementById('voice-status').innerText = 'Captured: ' + text;
                };
                rec.onerror = function(event) {
                    document.getElementById('voice-status').innerText = 'Microphone access denied or error.';
                };
                rec.start();
            }
        </script>
        """, unsafe_allow_html=True)
        st.caption("You can copy captured text into the main notes area above.")

with col_opts:
    st.markdown("#### Configuration")
    palace_type = st.selectbox(
        "Palace Architecture",
        options=["House", "Classroom", "Garden", "Campus", "Custom"],
        index=0,
        help="Select a familiar spatial layout or define your own real personal loci."
    )

    custom_places_text = ""
    if palace_type == "Custom":
        custom_places_text = st.text_area(
            "Your Custom Route Locations",
            value="Front Gate, Security Cabin, Main Corridor, Dean Office, Library Lobby, Canteen Terrace",
            help="Enter real places in your house or campus in sequential order, separated by commas or new lines."
        )

    story_style = st.selectbox(
        "Story Encoding Style",
        options=["Normal", "Funny", "Dramatic"],
        index=0,
        help="Vivid and unusual associations significantly improve recall."
    )

    topic_choice = st.selectbox(
        "Academic Discipline / Subject",
        options=["Auto-Detect by AI", "Computer Science", "Physics", "Chemistry", "Biology", "Maths", "History", "General"],
        index=0,
        help="Choose a specific discipline or leave as Auto-Detect."
    )

    max_concepts = st.slider(
        "Target Number of Concepts",
        min_value=5,
        max_value=12,
        value=7,
        help="Recommended: 5 to 9 concepts per palace for optimal working memory chunking."
    )

# --- GENERATION PIPELINE ---
generate_btn = st.button("🚀 Generate Memory Palace & 2D Storyboard", type="primary", use_container_width=True)

if generate_btn:
    combined_raw = notes_input.strip()
    if extra_paragraph and extra_paragraph.strip():
        combined_raw = f"{combined_raw}\n\n{extra_paragraph.strip()}".strip()

    clean_notes = sanitize_text(combined_raw)
    if not clean_notes or len(clean_notes.split()) < 4:
        st.warning("Please enter at least a sentence or two of notes to generate a memory palace.")
    else:
        with st.status("🏗️ Weaving your cognitive memory palace...", expanded=True) as status:
            # 1. NLP Key-point Extraction
            st.write("🔍 Extracting salient concepts with spaCy noun chunks & TF-IDF ranking...")
            extracted = extract_key_concepts(clean_notes, max_concepts=max_concepts)
            
            # 2. Topic Classification
            if topic_choice != "Auto-Detect by AI":
                topic_pred = topic_choice
                topic_conf = 1.0
                st.write(f"📚 Discipline selected: **{topic_pred}**")
            else:
                st.write("📚 Classifying academic discipline with scikit-learn model...")
                topic_pred, topic_conf = classify_topic(clean_notes)

            # 3. Difficulty Scoring & Visual Mapping
            st.write("🎨 Synthesizing concrete visual mnemonics & predicting cognitive difficulty...")
            mapped_concepts = []
            for item in extracted:
                c_name = item["concept"]
                sent = item["supporting_sentence"]
                
                # Predict difficulty
                diff_label, diff_conf, feats = predict_difficulty(c_name, sent, topic_pred)
                
                # Visual mapping
                vis_bundle = map_concept_to_visual(c_name, topic_pred)
                
                mapped_concepts.append({
                    "concept": c_name,
                    "concept_text": c_name,
                    "supporting_sentence": sent,
                    "score": item["score"],
                    "difficulty": diff_label,
                    "diff_confidence": diff_conf,
                    "visual_object": vis_bundle["visual_object"],
                    "visual_reason": vis_bundle["visual_reason"],
                    "emoji": vis_bundle["emoji"],
                    "match_tier": vis_bundle["match_tier"],
                    "user_edited": False
                })

            # 4. Route Loci Allocation
            st.write("📍 Allocating concepts to spatial route stations...")
            assigned_route = assign_concepts_to_palace(
                mapped_concepts,
                palace_type=palace_type.lower(),
                custom_places=custom_places_text
            )

            # 5. Vivid Narrative Generation
            st.write("📖 Writing associative story across route...")
            story = generate_palace_story(
                assigned_route,
                style=story_style,
                use_llm=st.session_state.get("use_llm", False)
            )

            # Store in session state for editing and saving
            first_c = extracted[0]['concept'] if extracted else 'Notes'
            clean_first = re.sub(r'(?i)\s+palace.*$', '', first_c).strip()
            clean_first = re.sub(r'(?i)^[a-z]+:\s*', '', clean_first).strip()
            palace_title = f"{topic_pred}: {clean_first} Palace"

            st.session_state["current_palace"] = {
                "title": palace_title,
                "topic": topic_pred,
                "topic_confidence": topic_conf,
                "palace_type": palace_type,
                "story_style": story_style,
                "language": lang,
                "story_text": story,
                "concepts": assigned_route
            }
            status.update(label="✅ Memory Palace Generated Successfully!", state="complete", expanded=False)

# --- RESULTS & EDITABLE PREVIEW ---
if "current_palace" in st.session_state and st.session_state["current_palace"]:
    palace = st.session_state["current_palace"]
    concepts = palace["concepts"]

    st.markdown("---")
    st.markdown(f"### 🏰 {palace['title']}")
    
    col_t1, col_t2, col_t3 = st.columns(3)
    with col_t1:
        st.markdown(f"**Discipline:** `{palace['topic']}` *(Confidence: {int(palace['topic_confidence']*100)}%)*")
    with col_t2:
        st.markdown(f"**Architecture:** `{palace['palace_type']}` | **Style:** `{palace['story_style']}`")
    with col_t3:
        st.markdown(f"**Total Stations:** `{len(concepts)} Loci`")

    # --- LOCATION CARDS (WITH USER EDITING) ---
    st.markdown("#### 📍 Ordered Loci Stations (Review & Customize)")
    st.caption("Personalized mnemonics work best! You can edit any visual object or station name before saving.")

    with st.expander("✏️ Click to customize any station's mnemonic or location", expanded=False):
        for idx, c in enumerate(concepts):
            c1, c2, c3 = st.columns([1.2, 1.6, 2.0])
            with c1:
                new_loc = st.text_input(f"Stop #{idx+1} Locus", value=c["location_name"], key=f"loc_edit_{idx}")
            with c2:
                new_obj = st.text_input(f"Visual Object", value=c["visual_object"], key=f"obj_edit_{idx}")
            with c3:
                new_reason = st.text_input(f"Associative Meaning", value=c["visual_reason"], key=f"reas_edit_{idx}")
            
            # Apply edits
            if new_loc != c["location_name"] or new_obj != c["visual_object"] or new_reason != c["visual_reason"]:
                c["location_name"] = new_loc
                c["visual_object"] = new_obj
                c["visual_reason"] = new_reason
                c["user_edited"] = True

    # Render Clean Location Cards Grid
    grid_cols = st.columns(min(4, len(concepts)))
    for idx, c in enumerate(concepts):
        col = grid_cols[idx % len(grid_cols)]
        diff_class = f"badge-{c.get('difficulty', 'Medium').lower()}"
        with col:
            st.markdown(f"""
            <div class="location-card">
                <div style="font-size: 0.75rem; font-weight: 700; color: #5B6CFF; text-transform: uppercase;">
                    Stop {idx+1}: {c['location_name']}
                </div>
                <h4 style="margin: 4px 0; color: #1F2937;">{c['emoji']} {c['concept']}</h4>
                <div style="font-weight: 600; color: #14B8A6; font-size: 0.92rem; margin-bottom: 6px;">
                    {c['visual_object']}
                </div>
                <span class="badge {diff_class}">{c.get('difficulty', 'Medium')}</span>
                <p style="color: #6B7280; font-size: 0.8rem; margin: 8px 0 0 0; line-height: 1.4;">
                    {c['visual_reason']}
                </p>
            </div>
            """, unsafe_allow_html=True)

    # --- VIVID STORY SECTION ---
    st.markdown("#### 📖 The Associative Walk Story")
    st.markdown(f"""
    <div class="lociloom-card-highlight">
        <p style="margin: 0; font-size: 1.05rem; line-height: 1.7; color: #1F2937;">
            {palace['story_text']}
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Audio Narration & Browser Voice
    col_aud1, col_aud2 = st.columns([1, 1])
    with col_aud1:
        if st.button("🔊 Read Aloud (Generate MP3)"):
            with st.spinner("Generating natural speech narration..."):
                audio_bytes, msg = generate_speech_audio(palace["story_text"], lang=lang)
                if audio_bytes:
                    st.audio(audio_bytes, format="audio/mp3")
                else:
                    st.info(msg)
                    st.markdown(get_browser_speech_html(palace["story_text"], lang=lang), unsafe_allow_html=True)
    with col_aud2:
        st.markdown(get_browser_speech_html(palace["story_text"], lang=lang), unsafe_allow_html=True)

    # --- 2D VISUAL ROUTE PRESENTATION ---
    st.markdown("#### 🗺️ 2D Palace Route & Visual Storyboard")
    reduced_motion = st.session_state.get("reduced_motion", False)
    text_only = st.session_state.get("text_only_mode", False)

    if text_only:
        st.info("ℹ️ Text-Only Route Mode is enabled in Accessibility Settings.")
        st.markdown(get_text_route_summary(concepts))
    else:
        tab_infographic, tab_mindmap, tab_ai_photos, tab_floorplan, tab_text_guide = st.tabs([
            "🎨 2D Storyboard Picture (Comic)",
            "🧠 Interactive Mind Map",
            "📸 AI Photo Cards (LLM Mode)",
            "📐 2D Floorplan Route Walk",
            "📄 Accessible Text Table"
        ])

        with tab_infographic:
            st.html(render_infographic_storyboard_html(concepts, title=palace["title"]))
            
            # Download Infographic Image button
            try:
                img_bytes = generate_infographic_image_bytes(concepts, title=palace["title"])
                st.download_button(
                    label="📥 Download 2D Storyboard Picture (PNG)",
                    data=img_bytes,
                    file_name=f"{palace['title'].lower().replace(' ', '_')}_storyboard.png",
                    mime="image/png",
                    help="Save the illustrated multi-panel infographic as a PNG image.",
                    use_container_width=False
                )
            except Exception as e:
                pass

        with tab_mindmap:
            st.markdown("##### 🧠 Interactive Radial Mind Map")
            st.caption("Visual knowledge network connecting your palace hub, loci stations, and mnemonic anchors.")
            mindmap_fig = create_palace_mindmap_figure(palace["title"], palace["topic"], concepts)
            st.plotly_chart(mindmap_fig, use_container_width=True)

        with tab_ai_photos:
            st.markdown("##### 📸 AI Mnemonic Photo Cards & Image Generation Prompts")
            st.caption("Generate high-contrast visual photo cards offline, or copy generative prompts for Midjourney / DALL-E 3 / Gemini.")
            
            p_cols = st.columns(min(3, max(1, len(concepts))))
            for idx, c in enumerate(concepts):
                col = p_cols[idx % len(p_cols)]
                with col:
                    st.markdown(f"**Stop #{idx+1}: {c['location_name']}**")
                    st.caption(f"Anchor: *{c['concept']}*")
                    # Offline illustrated photo card
                    card_png = generate_mnemonic_photo_card(
                        concept=c['concept'],
                        visual_object=c['visual_object'],
                        emoji=c['emoji'],
                        location=c['location_name'],
                        topic=palace['topic'],
                        difficulty=c.get('difficulty', 'Medium')
                    )
                    st.image(card_png, use_column_width=True)
                    st.download_button(
                        label=f"📥 Download Station #{idx+1} Photo Card",
                        data=card_png,
                        file_name=f"station_{idx+1}_{c['concept'][:10].lower().replace(' ', '_')}.png",
                        mime="image/png",
                        key=f"dl_card_{idx}",
                        use_container_width=True
                    )
                    with st.expander("🤖 View AI Image Prompt"):
                        ai_prompt = generate_ai_photo_prompt(c['concept'], c['visual_object'], c['location_name'])
                        st.code(ai_prompt, language="text")

        with tab_floorplan:
            # Step-by-step walk simulation slider
            walk_step = st.slider("🚶 Step-by-Step Route Walk", min_value=1, max_value=len(concepts), value=1)
            active_idx = walk_step - 1
            active_c = concepts[active_idx]
            
            st.markdown(f"""
            <div style="background: #F4F6FB; border-left: 4px solid #F59E0B; padding: 8px 14px; border-radius: 6px; margin-bottom: 10px;">
                <strong>Currently at Stop {walk_step}:</strong> {active_c['location_name']} &nbsp;|&nbsp;
                <strong>Encounter:</strong> {active_c['emoji']} {active_c['visual_object']} &nbsp;|&nbsp;
                <strong>Anchor:</strong> <em>{active_c['concept']}</em>
            </div>
            """, unsafe_allow_html=True)

            fig = create_2d_route_figure(concepts, title=f"{palace['title']} Route Path", active_step=active_idx, reduced_motion=reduced_motion)
            st.plotly_chart(fig, use_container_width=True)

        with tab_text_guide:
            st.markdown(get_text_route_summary(concepts))

    # --- ACTION BUTTONS: SAVE, QUIZ, EXPORT ---
    st.markdown("<br>", unsafe_allow_html=True)
    act_col1, act_col2, act_col3 = st.columns(3)

    with act_col1:
        if st.button("💾 Save Palace to My Library", type="primary", use_container_width=True):
            palace_id = save_palace(
                user_id=anon_id,
                title=palace["title"],
                topic=palace["topic"],
                palace_type=palace["palace_type"],
                story_style=palace["story_style"],
                language=palace["language"],
                story_text=palace["story_text"],
                concepts_list=concepts
            )
            saved_p = get_palace_by_id(palace_id)
            if saved_p:
                palace["id"] = palace_id
                st.session_state["current_palace"] = saved_p
            st.success(f"Palace '{palace['title']}' saved successfully (ID: #{palace_id})!")

    with act_col2:
        if st.button("🎯 Practice Quiz on this Palace", use_container_width=True):
            palace_id = palace.get("id")
            if not palace_id:
                palace_id = save_palace(
                    user_id=anon_id,
                    title=palace["title"],
                    topic=palace["topic"],
                    palace_type=palace["palace_type"],
                    story_style=palace["story_style"],
                    language=palace["language"],
                    story_text=palace["story_text"],
                    concepts_list=concepts
                )
            saved_p = get_palace_by_id(palace_id)
            st.session_state["quiz_palace"] = saved_p
            if "quiz_deck" in st.session_state:
                del st.session_state["quiz_deck"]
            st.switch_page("pages/3_Practice_Quiz.py")

    with act_col3:
        # Download clean study summary text
        summary_text = format_palace_summary_text(palace, concepts)
        clean_file_topic = re.sub(r'[^a-zA-Z0-9_-]', '_', palace.get('topic', 'Topic'))
        st.download_button(
            label="📥 Download Summary Sheet (.txt)",
            data=summary_text,
            file_name=f"{clean_file_topic}_Study_Summary.txt",
            mime="text/plain",
            use_container_width=True
        )

render_disclaimer()
