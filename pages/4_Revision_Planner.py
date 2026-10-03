"""
LociLoom Page 4: Spaced Repetition Revision Planner
Orchestrates adaptive scheduling via:
1. SuperMemo-2 (SM-2) algorithm (Interval, Ease Factor, Repetitions)
2. Machine Learning Forgetting Predictor (24h, 3-day, 7-day risk forecasting)
Categorizes concepts into:
- 🚨 Revise Today (Due now or overdue)
- ⏰ Revise Tomorrow
- 🗓️ Later (Upcoming revision windows)
Includes honest scientific comparison against the fixed-interval baseline.
"""
from datetime import datetime, timezone
import streamlit as st
from core.ui_helper import setup_page, render_disclaimer
from core.db import get_all_reviews_due, get_palace_by_id
from core.forgetting_model import predict_forgetting_risk, get_forgetting_bundle

setup_page(title="Revision Planner", icon="📅")
anon_id = st.session_state.get("anon_id", "LL-GUEST")

st.markdown("## 📅 Adaptive Revision Planner")
st.caption("Combining mathematical SM-2 interval scheduling with machine learning forgetting probability estimates.")

reviews = get_all_reviews_due(anon_id)

if not reviews:
    st.info("No concepts are currently tracked in your revision planner. Create a palace to begin scheduling!")
    if st.button("✨ Create a Palace"):
        st.switch_page("pages/1_Create_Palace.py")
    render_disclaimer()
    st.stop()

# Group concepts by urgency
today_str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
revise_today = []
revise_tomorrow = []
revise_later = []

for r in reviews:
    due = r.get("next_due") or today_str
    # Calculate days overdue or remaining
    try:
        due_dt = datetime.fromisoformat(due[:10])
        now_dt = datetime.fromisoformat(today_str)
        diff_days = (due_dt - now_dt).days
    except Exception:
        diff_days = 0

    r["diff_days"] = diff_days

    # Predict forgetting probabilities via trained ML model
    risk_info = predict_forgetting_risk(
        days_since_last_review=max(0.1, float(r.get("interval_days", 1))),
        num_reviews=r.get("repetitions", 0),
        past_accuracy=0.8,
        avg_response_time=5.0,
        hints_used=0,
        difficulty=r.get("difficulty", "Medium"),
        topic=r.get("topic", "General")
    )
    r["risk_info"] = risk_info

    if diff_days <= 0:
        revise_today.append(r)
    elif diff_days == 1:
        revise_tomorrow.append(r)
    else:
        revise_later.append(r)

# Top Status Metrics
m1, m2, m3, m4 = st.columns(4)
with m1:
    st.metric("🚨 Due Today", len(revise_today), delta=f"{len(revise_today)} due" if revise_today else "All clear!")
with m2:
    st.metric("⏰ Due Tomorrow", len(revise_tomorrow))
with m3:
    st.metric("🗓️ Scheduled Later", len(revise_later))
with m4:
    st.metric("📚 Total Tracked Loci", len(reviews))

# --- REVISION TABS ---
tab1, tab2, tab3 = st.tabs(["🚨 Revise Today", "⏰ Revise Tomorrow", "🗓️ Later Revisions"])

def render_concept_revision_card(item: dict, show_quiz_btn: bool = True):
    risk = item["risk_info"]
    cur_p = int(risk["current_forgetting_prob"] * 100)
    p_24h = int(risk["horizon_24h"] * 100)
    p_3d = int(risk["horizon_3d"] * 100)
    p_7d = int(risk["horizon_7d"] * 100)

    risk_badge = "badge-easy" if cur_p < 35 else "badge-medium" if cur_p < 65 else "badge-hard"

    card_html = (
        f'<div class="lociloom-card" style="margin-bottom: 12px;">'
        f'<div style="display: flex; justify-content: space-between; align-items: flex-start;">'
        f'<div>'
        f'<span class="badge badge-primary">{item["topic"]}</span>'
        f'<span style="font-size: 0.8rem; color: #6B7280; margin-left: 8px;">'
        f'Palace: <strong>{item["palace_title"]}</strong> &nbsp;|&nbsp; Station: <strong>{item["location_name"]}</strong>'
        f'</span>'
        f'<h3 style="margin: 6px 0 2px 0; color: #1F2937;">{item["concept_text"]}</h3>'
        f'<div style="font-size: 0.9rem; color: #14B8A6; font-weight: 600;">{item["visual_object"]}</div>'
        f'</div>'
        f'<div style="text-align: right;">'
        f'<span class="badge {risk_badge}">{risk["risk_category"]}</span>'
        f'<div style="font-size: 0.78rem; color: #6B7280; margin-top: 4px;">Forgetting Risk: <strong>{cur_p}%</strong></div>'
        f'</div>'
        f'</div>'
        f'<div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 10px; margin-top: 12px; background: #F8FAFC; padding: 10px; border-radius: 8px; font-size: 0.82rem;">'
        f'<div>📈 <strong>SM-2 Interval:</strong> {item.get("interval_days", 1)} day(s)</div>'
        f'<div>⚡ <strong>Ease Factor:</strong> {item.get("ease_factor", 2.5):.2f}</div>'
        f'<div>🔄 <strong>Repetitions:</strong> {item.get("repetitions", 0)}</div>'
        f'</div>'
        f'<div style="margin-top: 10px; font-size: 0.82rem; color: #4B5563;">'
        f'<strong>Forgetting Probability Horizon:</strong><br>'
        f'<div style="display: flex; gap: 15px; margin-top: 4px;">'
        f'<span>24 Hours: <strong>{p_24h}%</strong></span>'
        f'<span>3 Days: <strong>{p_3d}%</strong></span>'
        f'<span>7 Days: <strong>{p_7d}%</strong></span>'
        f'</div>'
        f'</div>'
        f'</div>'
    )
    st.markdown(card_html, unsafe_allow_html=True)

with tab1:
    if not revise_today:
        st.success("🎉 Great job! You have no concepts overdue or scheduled for revision today.")
    else:
        st.markdown(f"**{len(revise_today)} concept(s) require active retrieval practice today:**")
        for item in revise_today:
            render_concept_revision_card(item)

        if st.button("🎯 Launch Practice Quiz for Today's Due Loci", type="primary", use_container_width=True):
            p = get_palace_by_id(revise_today[0]["palace_id"])
            st.session_state["quiz_palace"] = p
            st.switch_page("pages/3_Practice_Quiz.py")

with tab2:
    if not revise_tomorrow:
        st.info("No concepts scheduled specifically for tomorrow.")
    else:
        st.markdown(f"**{len(revise_tomorrow)} concept(s) upcoming tomorrow:**")
        for item in revise_tomorrow:
            render_concept_revision_card(item)

with tab3:
    if not revise_later:
        st.info("No later concepts scheduled.")
    else:
        st.markdown(f"**{len(revise_later)} concept(s) securely consolidated in longer intervals:**")
        for item in revise_later:
            render_concept_revision_card(item)

# --- SCIENTIFIC MODEL BENCHMARK COMPARISON ---
st.markdown("---")
st.markdown("### 🔬 Adaptive ML vs. Fixed-Interval Baseline Comparison")
st.caption("How our machine learning forgetting predictor compares against standard fixed-interval Leitner scheduling:")

bundle = get_forgetting_bundle()
base = bundle["baseline_metrics"]
champ = bundle["champion_metrics"]
c_name = bundle["champion_name"]

comp_col1, comp_col2 = st.columns([1.5, 1.0])

with comp_col1:
    st.markdown(f"""
    <table style="width: 100%; border-collapse: collapse; text-align: left; font-size: 0.9rem; background: #FFFFFF; border-radius: 8px; overflow: hidden; border: 1px solid #E5E7EB;">
        <thead style="background: #F4F6FB; color: #1F2937;">
            <tr>
                <th style="padding: 10px 14px;">Metric</th>
                <th style="padding: 10px 14px;">Fixed-Interval Baseline</th>
                <th style="padding: 10px 14px; color: #5B6CFF;">Adaptive {c_name} (ML)</th>
            </tr>
        </thead>
        <tbody>
            <tr style="border-top: 1px solid #E5E7EB;">
                <td style="padding: 9px 14px;"><strong>ROC-AUC</strong></td>
                <td style="padding: 9px 14px;">{base['auc']:.4f}</td>
                <td style="padding: 9px 14px; color: #15803D; font-weight: 700;">{champ['auc']:.4f}</td>
            </tr>
            <tr style="border-top: 1px solid #E5E7EB; background: #FBFBFE;">
                <td style="padding: 9px 14px;"><strong>Accuracy</strong></td>
                <td style="padding: 9px 14px;">{base['accuracy']:.4f}</td>
                <td style="padding: 9px 14px; color: #15803D; font-weight: 700;">{champ['accuracy']:.4f}</td>
            </tr>
            <tr style="border-top: 1px solid #E5E7EB;">
                <td style="padding: 9px 14px;"><strong>Precision</strong></td>
                <td style="padding: 9px 14px;">{base['precision']:.4f}</td>
                <td style="padding: 9px 14px; color: #15803D; font-weight: 700;">{champ['precision']:.4f}</td>
            </tr>
            <tr style="border-top: 1px solid #E5E7EB; background: #FBFBFE;">
                <td style="padding: 9px 14px;"><strong>Recall</strong></td>
                <td style="padding: 9px 14px;">{base['recall']:.4f}</td>
                <td style="padding: 9px 14px; color: #15803D; font-weight: 700;">{champ['recall']:.4f}</td>
            </tr>
            <tr style="border-top: 1px solid #E5E7EB;">
                <td style="padding: 9px 14px;"><strong>F1-Score</strong></td>
                <td style="padding: 9px 14px;">{base['f1']:.4f}</td>
                <td style="padding: 9px 14px; color: #15803D; font-weight: 700;">{champ['f1']:.4f}</td>
            </tr>
        </tbody>
    </table>
    """, unsafe_allow_html=True)

with comp_col2:
    st.markdown(f"""
    <div class="lociloom-card" style="height: 100%;">
        <h4 style="margin: 0 0 6px 0; color: #1F2937;">Scientific Calibration Note</h4>
        <p style="font-size: 0.85rem; color: #6B7280; line-height: 1.5; margin: 0 0 8px 0;">
            The ML predictor incorporates student response times, past accuracy, question difficulty, and hints used in addition to elapsed days.
        </p>
        <p style="font-size: 0.82rem; color: #B45309; line-height: 1.4; background: #FEF3C7; padding: 8px; border-radius: 6px;">
            ⚠️ <em>Honest Disclosure:</em> Initial model weights are bootstrapped on simulated Ebbinghaus decay logs ({bundle['trained_samples']} samples). Probabilities indicate relative memory vulnerability.
        </p>
    </div>
    """, unsafe_allow_html=True)

render_disclaimer()
