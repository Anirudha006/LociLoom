"""
LociLoom Page 6: Scientific Evaluation & Experiment Mode
Enables empirical A/B experimentation to evaluate learning efficacy:
- Condition A: Standard Note Reading (Linear concept list)
- Condition B: LociLoom Memory Palace (Ordered loci + visual mnemonics + story)
Counterbalanced concept lists, timed study phase, immediate recall assessment,
24-hour delayed test recording, paired t-test / Wilcoxon statistics, Cohen's d effect size,
honest interpretation, and CSV data export.
"""
import io
import time
import random
import pandas as pd
import plotly.express as px
import streamlit as st
from datetime import datetime, timezone
from core.ui_helper import setup_page, render_disclaimer
from core.db import save_experiment_record, get_experiment_records, update_experiment_delayed_score
from core.stats import analyze_experiment_results
from core.quiz_engine import evaluate_typed_answer

setup_page(title="Experiment Mode", icon="🔬")

st.markdown("## 🔬 Scientific Experiment Mode")
st.caption("Empirically test whether the Method of Loci improves concept retention compared to standard linear notes.")

# --- RESEARCH CONSENT NOTICE ---
with st.expander("📋 Participant Information & Ethical Consent", expanded=False):
    st.markdown("""
    **Participant Notice & Voluntary Consent:**
    - **Purpose:** This experimental protocol evaluates immediate and delayed recall performance between standard linear study notes and LociLoom's spatial memory palace technique.
    - **Privacy:** No personally identifiable information (PII), names, or emails are collected. You are identified solely by a randomized anonymous participant code.
    - **Voluntary:** Participation is entirely voluntary. You may stop or exit at any time.
    - **Data Handling:** All experimental logs are stored locally in your SQLite database and can be exported as a CSV file for college project analysis.
    """)

# Define two counterbalanced, balanced concept lists of equivalent difficulty
LIST_1 = [
    {"concept": "Mitochondria", "desc": "Powerhouse organelle generating cellular ATP currency through aerobic respiration.", "vis": "🔋 Humming electric generator battery", "loc": "Front Porch"},
    {"concept": "Ribosome", "desc": "Molecular protein factory translating mRNA transcripts into polypeptide chains.", "vis": "🏭 Miniature protein assembly factory", "loc": "Main Entrance"},
    {"concept": "Chloroplast", "desc": "Specialized plant organelle containing thylakoids that conduct photosynthetic reactions.", "vis": "🍳 Green solar frying pan", "loc": "Living Room Sofa"},
    {"concept": "Nucleus", "desc": "Fortified control center enclosing DNA chromatin behind a nuclear envelope.", "vis": "🏛️ Marble fortress control tower", "loc": "Dining Table"},
    {"concept": "Lysosome", "desc": "Acidic hydrolytic enzyme vesicle breaking down cellular debris and waste.", "vis": "🗑️ Acidic recycling disposal bin", "loc": "Kitchen Counter"},
    {"concept": "Endoplasmic Reticulum", "desc": "Extensive folded membrane network synthesizing lipids and modifying proteins.", "vis": "🛣️ Folded labyrinth highway ribbon", "loc": "Bedroom Desk"}
]

LIST_2 = [
    {"concept": "Kinetic Energy", "desc": "Energy possessed by a body due to its translational or rotational motion.", "vis": "🎢 Zooming downhill roller coaster", "loc": "Classroom Door"},
    {"concept": "Momentum", "desc": "Product of mass and velocity that is conserved in isolated collision systems.", "vis": "🎳 Heavy rolling bowling ball", "loc": "Teacher Podium"},
    {"concept": "Electromagnetism", "desc": "Coupled fundamental interaction between electric currents and magnetic fields.", "vis": "🧲 Horseshoe magnet sparking blue arcs", "loc": "Smart Projector"},
    {"concept": "Refraction", "desc": "Deflection of wave propagation velocity passing between media of different density.", "vis": "📐 Triangular glass prism", "loc": "Lab Equipment Cart"},
    {"concept": "Entropy", "desc": "Thermodynamic measure of unavailable energy and molecular microscopic disorder.", "vis": "💥 Shattering porcelain teacup", "loc": "Center Desk"},
    {"concept": "Centripetal Force", "desc": "Inward orthogonal force directing an object along a curved circular trajectory.", "vis": "🎡 Tetherball spinning on tight string", "loc": "Window Sill"}
]

# Tabs: Conduct Experiment vs Statistical Analysis
tab_run, tab_analysis, tab_delayed = st.tabs(["🧪 Run Participant Trial", "📊 Statistical Analysis", "⏰ 24-Hour Delayed Test"])

with tab_run:
    st.markdown("### Participant Trial Setup")
    
    # Generate participant code
    if "exp_participant_id" not in st.session_state:
        st.session_state["exp_participant_id"] = f"P-{random.randint(100, 999)}"

    p_col1, p_col2, p_col3 = st.columns(3)
    with p_col1:
        part_id = st.text_input("Anonymous Participant Code", value=st.session_state["exp_participant_id"])
    with p_col2:
        condition_choice = st.selectbox(
            "Experimental Condition",
            ["Condition A: Standard Linear Notes", "Condition B: LociLoom Memory Palace"],
            help="Counterbalanced: Alternate conditions across participants."
        )
    with p_col3:
        list_choice = st.selectbox(
            "Concept Study Material",
            ["List 1: Cell Biology (6 concepts)", "List 2: Classical Physics (6 concepts)"],
            help="Counterbalanced curriculum lists of matched difficulty."
        )

    active_list = LIST_1 if "1" in list_choice else LIST_2
    is_palace_mode = ("Condition B" in condition_choice)

    # Initialize Trial State
    if "exp_phase" not in st.session_state:
        st.session_state["exp_phase"] = "READY"
        st.session_state["exp_study_start"] = 0
        st.session_state["exp_study_time"] = 0

    # Phase 1: Ready to study
    if st.session_state["exp_phase"] == "READY":
        st.markdown("""
        <div class="lociloom-card">
            <h4>Instructions for the Participant:</h4>
            <ol>
                <li>Click <strong>Start Study Phase</strong> when ready. A timer will record your learning duration.</li>
                <li>Study the concepts carefully using the provided presentation format.</li>
                <li>When confident, click <strong>Proceed to Recall Test</strong>.</li>
                <li>You will then be prompted to recall the concepts from memory without looking back.</li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

        if st.button("⏱️ Start Study Phase", type="primary"):
            st.session_state["exp_phase"] = "STUDYING"
            st.session_state["exp_study_start"] = time.time()
            st.rerun()

    # Phase 2: Active Study Phase
    elif st.session_state["exp_phase"] == "STUDYING":
        st.markdown(f"### 📖 Study Phase: `{condition_choice}`")
        st.caption("Timer running... Study the items below thoroughly.")

        if is_palace_mode:
            st.markdown(f"""
            <div class="lociloom-card-highlight">
                <h4 style="margin: 0 0 6px 0;">🏛️ Spatial Route Story (Condition B)</h4>
                Walk through this route in order: 
                First at the <strong>{active_list[0]['loc']}</strong> you see a {active_list[0]['vis']} for {active_list[0]['concept']}.
                Next entering the <strong>{active_list[1]['loc']}</strong>, you find a {active_list[1]['vis']} representing {active_list[1]['concept']}.
                Moving into the <strong>{active_list[2]['loc']}</strong>, a {active_list[2]['vis']} anchors {active_list[2]['concept']}.
                Continuing to the <strong>{active_list[3]['loc']}</strong>, an ancient {active_list[3]['vis']} marks {active_list[3]['concept']}.
                Passing the <strong>{active_list[4]['loc']}</strong>, a {active_list[4]['vis']} embodies {active_list[4]['concept']}.
                Finally at the <strong>{active_list[5]['loc']}</strong>, a {active_list[5]['vis']} concludes {active_list[5]['concept']}.
            </div>
            """, unsafe_allow_html=True)

            g_cols = st.columns(3)
            for idx, item in enumerate(active_list):
                col = g_cols[idx % 3]
                with col:
                    st.markdown(f"""
                    <div class="location-card">
                        <div style="font-size: 0.75rem; color: #5B6CFF; font-weight: 700;">Stop #{idx+1}: {item['loc']}</div>
                        <h4 style="margin: 4px 0;">{item['concept']}</h4>
                        <div style="color: #14B8A6; font-weight: 600; font-size: 0.9rem;">{item['vis']}</div>
                        <p style="color: #6B7280; font-size: 0.8rem; margin-top: 6px;">{item['desc']}</p>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            # Standard Linear Notes (Condition A)
            st.markdown("""
            <div class="lociloom-card">
                <h4 style="margin: 0 0 10px 0;">📄 Standard Text Notes (Condition A)</h4>
            """, unsafe_allow_html=True)
            for idx, item in enumerate(active_list):
                st.markdown(f"**{idx+1}. {item['concept']}**: {item['desc']}")
            st.markdown("</div>", unsafe_allow_html=True)

        if st.button("✅ I Am Finished Studying - Proceed to Recall Test", type="primary"):
            st.session_state["exp_study_time"] = round(time.time() - st.session_state["exp_study_start"], 1)
            st.session_state["exp_phase"] = "TESTING"
            st.session_state["exp_test_answers"] = {}
            st.rerun()

    # Phase 3: Immediate Recall Test
    elif st.session_state["exp_phase"] == "TESTING":
        st.markdown("### ❓ Immediate Retrieval Test")
        st.markdown(f"**Recorded Study Duration:** `{st.session_state['exp_study_time']:.1f} seconds`")
        st.caption("Please recall and type each concept defined below from memory:")

        user_responses = {}
        for idx, item in enumerate(active_list):
            prompt = f"What was the concept located at Stop #{idx+1} ({item['loc']})?" if is_palace_mode else f"Concept #{idx+1} defined as: '{item['desc'][:50]}...'"
            user_responses[idx] = st.text_input(prompt, key=f"exp_q_{idx}")

        st.markdown("<br>", unsafe_allow_html=True)
        satis = st.slider("Participant subjective satisfaction with study technique (1 to 5)", 1, 5, 4)

        if st.button("Submit Recall Test & Record Trial", type="primary"):
            correct_count = 0
            for idx, item in enumerate(active_list):
                ans = user_responses.get(idx, "")
                is_corr, _ = evaluate_typed_answer(ans, item["concept"], threshold=75.0)
                if is_corr:
                    correct_count += 1

            immediate_score = round((correct_count / len(active_list)) * 100, 1)

            # Save in SQLite
            cond_label = "Condition B (LociLoom)" if is_palace_mode else "Condition A (Standard Notes)"
            record_id = save_experiment_record(
                participant_id=part_id,
                condition=cond_label,
                list_id="List 1" if "1" in list_choice else "List 2",
                study_time=st.session_state["exp_study_time"],
                immediate_score=immediate_score,
                satisfaction=satis
            )

            st.session_state["exp_last_result"] = {
                "record_id": record_id,
                "score": immediate_score,
                "correct": correct_count,
                "total": len(active_list),
                "study_time": st.session_state["exp_study_time"],
                "condition": cond_label
            }
            st.session_state["exp_phase"] = "RESULTS"
            st.rerun()

    # Phase 4: Trial Completed Results
    elif st.session_state["exp_phase"] == "RESULTS":
        res = st.session_state.get("exp_last_result", {})
        st.markdown(f"""
        <div class="lociloom-card" style="text-align: center; padding: 24px;">
            <h2 style="color: #5B6CFF; margin: 0;">Trial Recorded!</h2>
            <h1 style="color: #1F2937; margin: 6px 0;">{res.get('score', 0)}%</h1>
            <p style="color: #6B7280; font-size: 0.95rem;">
                Participant scored <strong>{res.get('correct', 0)} / {res.get('total', 6)}</strong> in {res.get('study_time', 0)}s under <strong>{res.get('condition', '')}</strong>.
            </p>
            <p style="color: #14B8A6; font-size: 0.85rem; font-weight: 600;">
                Trial ID #{res.get('record_id', 0)} stored in experiment database.
            </p>
        </div>
        """, unsafe_allow_html=True)

        if st.button("🧪 Run Another Participant Trial", type="primary"):
            st.session_state["exp_phase"] = "READY"
            st.session_state["exp_participant_id"] = f"P-{random.randint(100, 999)}"
            st.rerun()

# --- STATISTICAL ANALYSIS TAB ---
with tab_analysis:
    st.markdown("### 📈 Scientific Evaluation & Statistical Hypothesis Testing")
    records = get_experiment_records()
    analysis = analyze_experiment_results(records)

    if not analysis.get("has_data", False):
        st.info(analysis.get("message", "Insufficient participant trials to run analysis."))
        st.caption("Tip: Run at least 2 trials under Condition A and 2 trials under Condition B in the first tab.")
    else:
        # Metrics summary
        c1, c2, c3, c4 = st.columns(4)
        with c1:
            st.metric("Condition A Mean Recall", f"{analysis['mean_score_a']}%", f"N = {analysis['n_a']}")
        with c2:
            st.metric("Condition B Mean Recall", f"{analysis['mean_score_b']}%", f"N = {analysis['n_b']}")
        with c3:
            st.metric("Effect Size (Cohen's d)", f"{analysis['cohens_d']:.2f}", analysis["effect_magnitude"])
        with c4:
            st.metric("p-Value", f"{analysis['p_value']:.4f}", "Significant" if analysis["is_significant"] else "Not Sig")

        # Bar chart comparison
        comp_df = pd.DataFrame([
            {"Condition": "Condition A (Standard Notes)", "Recall Score (%)": analysis["mean_score_a"], "Study Time (s)": analysis["mean_time_a"]},
            {"Condition": "Condition B (LociLoom Palace)", "Recall Score (%)": analysis["mean_score_b"], "Study Time (s)": analysis["mean_time_b"]}
        ])
        fig_exp = px.bar(
            comp_df,
            x="Condition",
            y="Recall Score (%)",
            color="Condition",
            text_auto=".1f",
            title="<b>Mean Recall Accuracy by Experimental Condition</b>",
            color_discrete_sequence=["#6B7280", "#5B6CFF"]
        )
        fig_exp.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#F8FAFC",
            yaxis=dict(range=[0, 105], gridcolor="#E2E8F0"),
            height=340,
            showlegend=False
        )
        st.plotly_chart(fig_exp, use_container_width=True)

        # Plain language scientific interpretation box
        st.markdown(f"""
        <div class="lociloom-card" style="border-left: 4px solid #5B6CFF;">
            <h4 style="margin: 0 0 6px 0; color: #1F2937;">Statistical Test: {analysis['test_name']}</h4>
            <p style="color: #4B5563; font-size: 0.92rem; line-height: 1.6; margin: 0 0 8px 0;">
                {analysis['interpretation']}
            </p>
            <div style="font-size: 0.82rem; color: #B45309; background: #FEF3C7; padding: 8px 12px; border-radius: 6px;">
                {analysis['power_warning']}
            </div>
        </div>
        """, unsafe_allow_html=True)

        # Raw Table & CSV Export
        st.markdown("#### 📋 Raw Empirical Trial Logs")
        rec_df = pd.DataFrame(records)
        st.dataframe(rec_df, use_container_width=True, hide_index=True)

        csv_exp = io.StringIO()
        rec_df.to_csv(csv_exp, index=False)
        st.download_button(
            label="📥 Export Experiment Data as CSV",
            data=csv_exp.getvalue(),
            file_name="LociLoom_Experiment_Trials.csv",
            mime="text/csv",
            use_container_width=True
        )

# --- 24-HOUR DELAYED TEST TAB ---
with tab_delayed:
    st.markdown("### ⏰ 24-Hour Delayed Retention Assessment")
    st.markdown("""
    In memory science, immediate recall measures initial encoding, but **delayed retention** (24+ hours later)
    measures true synaptic consolidation. Return to this screen 24 hours after a trial to record delayed recall scores.
    """)
    records = get_experiment_records()
    if not records:
        st.info("No experiment trials on record.")
    else:
        pending = [r for r in records if r.get("delayed_score") is None]
        if not pending:
            st.success("All current participant trials have completed their 24-hour delayed assessments!")
        else:
            st.markdown(f"**{len(pending)} trial(s) awaiting 24-hour delayed recall score:**")
            for p in pending:
                p_c1, p_c2, p_c3 = st.columns([1.5, 1.5, 1.0])
                with p_c1:
                    st.write(f"**ID #{p['id']}** ({p['participant_id']}) — {p['condition']}")
                    st.caption(f"Initial: {p['immediate_score']}% | Recorded: {p['created_at'][:16]}")
                with p_c2:
                    del_score = st.number_input("Delayed Score (%)", min_value=0.0, max_value=100.0, value=float(p['immediate_score']), key=f"del_in_{p['id']}")
                with p_c3:
                    if st.button("Save Delayed Score", key=f"save_del_{p['id']}"):
                        update_experiment_delayed_score(p["id"], del_score)
                        st.success("Updated delayed retention score!")
                        st.rerun()

render_disclaimer()
