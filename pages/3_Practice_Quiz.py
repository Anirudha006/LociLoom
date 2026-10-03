"""
LociLoom Page 3: Spatial Retrieval Practice Quiz
Tests recall along the method of loci route using active retrieval testing.
Features:
- Answers hidden until student responds
- 4 Question Types:
  1. Free-Text Concept Typing (with forgiving rapidfuzz typo tolerance)
  2. Multiple Choice Recognition (4 options)
  3. Reverse Locus Location (Concept -> Where along route)
  4. Sequence Ordering Question (Which location came earlier)
- 2-Step Graduated Hint System (first letter mask -> visual mnemonic token)
- Exact response time & attempt logging in SQLite
- Updates SM-2 spaced repetition schedules automatically
- Final score report with per-concept performance breakdown
"""
import time
import streamlit as st
from core.ui_helper import setup_page, render_disclaimer
from core.db import get_palaces, get_palace_by_id, log_quiz_attempt, get_sm2_review, save_sm2_review
from core.quiz_engine import generate_quiz_deck, evaluate_typed_answer
from core.spaced_repetition import score_to_sm2_quality, schedule_next_review

setup_page(title="Practice Quiz", icon="🎯")
anon_id = st.session_state.get("anon_id", "LL-GUEST")

st.markdown("## 🎯 Spatial Retrieval Practice")
st.caption("Active recall strengthens neural synaptic pathways. Walk through your palace stations from memory!")

palaces = get_palaces(anon_id)

# Palace selection
selected_palace = None
if "quiz_palace" in st.session_state and st.session_state["quiz_palace"]:
    p_candidate = st.session_state["quiz_palace"]
    p_id = p_candidate.get("id")
    if p_id:
        selected_palace = get_palace_by_id(p_id)
    if not selected_palace and p_candidate.get("concepts"):
        from core.db import save_palace
        new_id = save_palace(
            user_id=anon_id,
            title=p_candidate.get("title", "My Palace"),
            topic=p_candidate.get("topic", "General"),
            palace_type=p_candidate.get("palace_type", "house"),
            story_style=p_candidate.get("story_style", "Normal"),
            language=p_candidate.get("language", "en"),
            story_text=p_candidate.get("story_text", ""),
            concepts_list=p_candidate.get("concepts", [])
        )
        selected_palace = get_palace_by_id(new_id)
        st.session_state["quiz_palace"] = selected_palace

if not selected_palace:
    if not palaces:
        st.warning("You don't have any saved palaces yet. Please create a palace first!")
        if st.button("✨ Go to Create Palace"):
            st.switch_page("pages/1_Create_Palace.py")
        st.stop()
    else:
        palace_titles = {p["id"]: f"{p['title']} ({p['concept_count']} stops)" for p in palaces}
        chosen_id = st.selectbox(
            "Select a Palace to Practice",
            options=list(palace_titles.keys()),
            format_func=lambda x: palace_titles[x]
        )
        selected_palace = get_palace_by_id(chosen_id)

# Initialize Quiz Session State
if "quiz_deck" not in st.session_state or st.session_state.get("quiz_palace_id") != selected_palace.get("id"):
    concepts = selected_palace.get("concepts", [])
    st.session_state["quiz_deck"] = generate_quiz_deck(concepts)
    st.session_state["quiz_palace_id"] = selected_palace.get("id")
    st.session_state["quiz_idx"] = 0
    st.session_state["quiz_score"] = 0
    st.session_state["quiz_log"] = []
    st.session_state["hint_level"] = 0
    st.session_state["q_start_time"] = time.time()
    st.session_state["answered_current"] = False
    st.session_state["last_eval"] = None

deck = st.session_state["quiz_deck"]
q_idx = st.session_state["quiz_idx"]
total_q = len(deck)

# --- QUIZ COMPLETE SCREEN ---
if q_idx >= total_q:
    st.markdown("### 🏆 Retrieval Practice Complete!")
    final_score = st.session_state["quiz_score"]
    pct = int((final_score / total_q) * 100) if total_q > 0 else 0

    st.markdown(f"""
    <div class="lociloom-card" style="text-align: center; padding: 30px;">
        <h1 style="color: #5B6CFF; margin: 0; font-size: 3rem;">{pct}%</h1>
        <h3 style="margin: 8px 0; color: #1F2937;">You recalled {final_score} out of {total_q} concepts correctly!</h3>
        <p style="color: #6B7280; font-size: 0.95rem;">
            Your SM-2 spaced repetition intervals have been automatically recalculated and scheduled.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Concept breakdown table
    st.markdown("#### 📋 Performance Breakdown by Station")
    log_entries = st.session_state.get("quiz_log", [])
    
    for entry in log_entries:
        corr = entry["correct"]
        icon = "✅" if corr else "❌"
        badge = "badge-easy" if corr else "badge-hard"
        status = "Correct" if corr else "Needs Review"
        st.markdown(f"""
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-left: 4px solid {'#22C55E' if corr else '#EF4444'}; border-radius: 8px; padding: 12px 16px; margin-bottom: 8px;">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <div>
                    <strong>{icon} Stop: {entry['location']}</strong> &nbsp;|&nbsp; 
                    Concept: <strong>{entry['concept']}</strong>
                </div>
                <span class="badge {badge}">{status}</span>
            </div>
            <div style="font-size: 0.8rem; color: #6B7280; margin-top: 4px;">
                Mnemonic Token: {entry['visual_object']} &nbsp;|&nbsp; 
                Response Time: {entry['response_time']:.1f}s &nbsp;|&nbsp; 
                Hints Used: {entry['hints_used']}
            </div>
        </div>
        """, unsafe_allow_html=True)

    c_btn1, c_btn2, c_btn3 = st.columns(3)
    with c_btn1:
        if st.button("🔄 Retake Quiz", type="primary", use_container_width=True):
            del st.session_state["quiz_deck"]
            st.rerun()
    with c_btn2:
        if st.button("📅 View Revision Planner", use_container_width=True):
            st.switch_page("pages/4_Revision_Planner.py")
    with c_btn3:
        if st.button("📊 Open Dashboard", use_container_width=True):
            st.switch_page("pages/5_Dashboard.py")

    render_disclaimer()
    st.stop()

# --- ACTIVE QUESTION DISPLAY ---
curr_q = deck[q_idx]

# Progress Bar
progress = (q_idx) / total_q
st.progress(progress, text=f"Question {q_idx + 1} of {total_q}")

st.markdown(f"#### 🏛️ Station: `{curr_q['location_name']}`")
st.markdown(f"### {curr_q['prompt']}")

q_type = curr_q["question_type"]
user_answer = None

# Question Input Forms
if not st.session_state["answered_current"]:
    if q_type == "type_concept":
        typed_val = st.text_input("Type the concept name:", key=f"typed_{q_idx}", placeholder="e.g. Photosynthesis")
        submit_btn = st.button("✅ Submit Answer", type="primary", key=f"submit_btn_typed_{q_idx}")
        if submit_btn:
            user_answer = typed_val

    elif q_type in ["mcq", "reverse", "ordering"]:
        options = curr_q.get("options", [])
        chosen = st.radio("Choose the correct option:", options=options, key=f"radio_{q_idx}", index=None)
        submit_btn = st.button("✅ Submit Answer", type="primary", key=f"submit_btn_mcq_{q_idx}")
        if submit_btn:
            user_answer = chosen

    # Hint Buttons
    st.markdown("<br>", unsafe_allow_html=True)
    h_col1, h_col2, h_space = st.columns([1.3, 1.5, 3])
    with h_col1:
        if st.button("💡 Hint 1: Letter Mask", key=f"h1_{q_idx}"):
            st.session_state["hint_level"] = max(st.session_state["hint_level"], 1)
    with h_col2:
        if st.button("🎨 Hint 2: Visual Token", key=f"h2_{q_idx}"):
            st.session_state["hint_level"] = 2

    # Render Active Hints
    hint_lvl = st.session_state.get("hint_level", 0)
    if hint_lvl >= 1:
        st.info(f"💡 **Hint 1:** {curr_q['tier1_hint']}")
    if hint_lvl >= 2:
        st.warning(f"🎨 **Hint 2:** {curr_q['tier2_hint']}")

# Process Submission
if user_answer is not None and not st.session_state["answered_current"]:
    elapsed = max(0.8, round(time.time() - st.session_state["q_start_time"], 2))
    correct = False
    sim_score = 100.0

    if q_type == "type_concept":
        correct, sim_score = evaluate_typed_answer(user_answer, curr_q["correct_answer"], threshold=75.0)
    else:
        correct = (str(user_answer).strip().lower() == str(curr_q["correct_answer"]).strip().lower())

    hints_used = st.session_state.get("hint_level", 0)

    # Log attempt in SQLite
    log_quiz_attempt(
        user_id=anon_id,
        concept_id=curr_q["concept_id"],
        question_type=q_type,
        correct=correct,
        response_time=elapsed,
        hints_used=hints_used
    )

    # Update SM-2 Review Schedule
    current_review = get_sm2_review(curr_q["concept_id"])
    prev_ef = current_review["ease_factor"] if current_review else 2.5
    prev_interval = current_review["interval_days"] if current_review else 1
    prev_reps = current_review["repetitions"] if current_review else 0

    sm2_quality = score_to_sm2_quality(correct, hints_used=hints_used, response_time=elapsed)
    next_sched = schedule_next_review(
        quality=sm2_quality,
        repetitions=prev_reps,
        previous_interval=prev_interval,
        previous_ease_factor=prev_ef
    )
    save_sm2_review(
        concept_id=curr_q["concept_id"],
        ease_factor=next_sched["ease_factor"],
        interval_days=next_sched["interval_days"],
        repetitions=next_sched["repetitions"],
        next_due=next_sched["next_due"]
    )

    # Update session score & log
    if correct:
        st.session_state["quiz_score"] += 1

    st.session_state["quiz_log"].append({
        "concept": curr_q["concept_name"],
        "location": curr_q["location_name"],
        "visual_object": curr_q["visual_object"],
        "correct": correct,
        "response_time": elapsed,
        "hints_used": hints_used
    })

    st.session_state["answered_current"] = True
    st.session_state["last_eval"] = {
        "correct": correct,
        "user_answer": user_answer,
        "correct_answer": curr_q["correct_answer"],
        "sim_score": sim_score,
        "feedback_story": curr_q["feedback_story"]
    }
    st.rerun()

# Feedback Banner when answered
if st.session_state.get("answered_current", False):
    res = st.session_state["last_eval"]
    if res["correct"]:
        st.success(f"🎉 **Correct!** Your answer: `{res['user_answer']}` (Target: `{res['correct_answer']}`)")
    else:
        st.error(f"❌ **Not quite.** You entered: `{res['user_answer']}`. Correct answer: **{res['correct_answer']}**")

    st.markdown(f"""
    <div class="lociloom-card-highlight">
        <strong>Mnemonic Anchor Feedback:</strong><br>
        {res['feedback_story']}
    </div>
    """, unsafe_allow_html=True)

    if st.button("Next Question ➡️", type="primary"):
        st.session_state["quiz_idx"] += 1
        st.session_state["answered_current"] = False
        st.session_state["hint_level"] = 0
        st.session_state["q_start_time"] = time.time()
        st.session_state["last_eval"] = None
        st.rerun()

render_disclaimer()
