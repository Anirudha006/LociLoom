"""
LociLoom Page 5: Adaptive Learning Analytics Dashboard
Displays performance metrics, retrieval trends, and cognitive retention graphs:
- Score progression over time (Plotly Light Theme)
- Accuracy breakdown per academic subject
- Most-missed vulnerable concepts & forgotten topics table
- Study streaks, response times, and review history
- Multi-dimensional filters (by palace and date range)
- Private CSV export of student's own recall logs
"""
import io
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from datetime import datetime, timezone
from core.ui_helper import setup_page, render_disclaimer
from core.db import get_quiz_attempts, get_palaces

setup_page(title="Dashboard", icon="📊")
anon_id = st.session_state.get("anon_id", "LL-GUEST")

st.markdown("## 📊 Learning Analytics & Retention Dashboard")
st.caption("Inspect your cognitive retrieval trends, response latencies, and vulnerable concepts.")

attempts = get_quiz_attempts(anon_id)
palaces = get_palaces(anon_id)

if not attempts:
    st.info("No practice attempts recorded yet! Complete a practice quiz to view your learning analytics.")
    # Show friendly empty-state mock charts or prompt
    empty_col1, empty_col2 = st.columns(2)
    with empty_col1:
        st.markdown("""
        <div class="lociloom-card" style="text-align: center; padding: 30px;">
            <h3>🎯 Take a Practice Quiz</h3>
            <p style="color: #6B7280; font-size: 0.9rem;">
                Your accuracy trends, response speed, and topic mastery will appear here automatically.
            </p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("Start Practice Quiz", type="primary"):
            st.switch_page("pages/3_Practice_Quiz.py")
    render_disclaimer()
    st.stop()

# Convert attempts to DataFrame
df = pd.DataFrame(attempts)
df["date"] = pd.to_datetime(df["timestamp"]).dt.date
df["correct_int"] = df["correct"].astype(int)

# --- FILTER SECTION ---
with st.expander("🔍 Filter Dashboard Data", expanded=False):
    f_c1, f_c2 = st.columns(2)
    with f_c1:
        palace_options = ["All Palaces"] + list(df["palace_title"].unique())
        selected_palace_filter = st.selectbox("Filter by Palace", palace_options)
    with f_c2:
        min_date = df["date"].min()
        max_date = df["date"].max()
        selected_dates = st.date_input("Date Range", [min_date, max_date])

# Apply filters
filtered_df = df.copy()
if selected_palace_filter != "All Palaces":
    filtered_df = filtered_df[filtered_df["palace_title"] == selected_palace_filter]

if isinstance(selected_dates, (list, tuple)) and len(selected_dates) == 2:
    start_d, end_d = selected_dates
    filtered_df = filtered_df[(filtered_df["date"] >= start_d) & (filtered_df["date"] <= end_d)]

if filtered_df.empty:
    st.warning("No records match the selected filters.")
    st.stop()

# --- TOP METRIC CARDS ---
total_attempts = len(filtered_df)
overall_acc = (filtered_df["correct_int"].mean()) * 100
avg_time = filtered_df["response_time"].mean()
unique_concepts_tested = filtered_df["concept_id"].nunique()

m_col1, m_col2, m_col3, m_col4 = st.columns(4)
with m_col1:
    st.metric("Total Retrieval Attempts", total_attempts)
with m_col2:
    st.metric("Overall Accuracy", f"{overall_acc:.1f}%")
with m_col3:
    st.metric("Avg Response Time", f"{avg_time:.2f}s")
with m_col4:
    st.metric("Unique Loci Tested", unique_concepts_tested)

st.markdown("<br>", unsafe_allow_html=True)

# --- PLOTLY CHARTS (LIGHT THEME) ---
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    # 1. Retrieval Accuracy Over Time
    time_series = filtered_df.groupby("date")["correct_int"].agg(["mean", "count"]).reset_index()
    time_series["accuracy_pct"] = time_series["mean"] * 100
    
    fig_time = px.line(
        time_series,
        x="date",
        y="accuracy_pct",
        markers=True,
        title="<b>Recall Accuracy Over Time (%)</b>",
        labels={"accuracy_pct": "Accuracy (%)", "date": "Date"},
        color_discrete_sequence=["#5B6CFF"]
    )
    fig_time.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        yaxis=dict(range=[0, 105], gridcolor="#E2E8F0"),
        xaxis=dict(gridcolor="#E2E8F0"),
        height=320,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_time, use_container_width=True)

with chart_col2:
    # 2. Accuracy per Topic Domain
    topic_perf = filtered_df.groupby("topic")["correct_int"].agg(["mean", "count"]).reset_index()
    topic_perf["accuracy_pct"] = topic_perf["mean"] * 100

    fig_topic = px.bar(
        topic_perf,
        x="topic",
        y="accuracy_pct",
        color="topic",
        text_auto=".1f",
        title="<b>Accuracy per Academic Discipline (%)</b>",
        labels={"accuracy_pct": "Accuracy (%)", "topic": "Discipline"},
        color_discrete_sequence=["#5B6CFF", "#14B8A6", "#F59E0B", "#22C55E", "#8B5CF6", "#EC4899", "#3B82F6"]
    )
    fig_topic.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        yaxis=dict(range=[0, 105], gridcolor="#E2E8F0"),
        xaxis=dict(gridcolor="#E2E8F0"),
        showlegend=False,
        height=320,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_topic, use_container_width=True)

# --- SECOND ROW OF CHARTS ---
row2_col1, row2_col2 = st.columns(2)

with row2_col1:
    # 3. Response Latency by Question Type
    qtype_perf = filtered_df.groupby("question_type")["response_time"].mean().reset_index()
    fig_rt = px.bar(
        qtype_perf,
        x="question_type",
        y="response_time",
        title="<b>Average Response Latency by Question Format</b>",
        labels={"response_time": "Time (Seconds)", "question_type": "Format"},
        color_discrete_sequence=["#14B8A6"],
        text_auto=".2f"
    )
    fig_rt.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        yaxis=dict(gridcolor="#E2E8F0"),
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_rt, use_container_width=True)

with row2_col2:
    # 4. Difficulty Breakdown
    diff_perf = filtered_df.groupby("difficulty")["correct_int"].agg(["mean", "count"]).reset_index()
    diff_perf["accuracy_pct"] = diff_perf["mean"] * 100
    fig_diff = px.bar(
        diff_perf,
        x="difficulty",
        y="accuracy_pct",
        color="difficulty",
        title="<b>Recall Accuracy by Concept Difficulty</b>",
        labels={"accuracy_pct": "Accuracy (%)", "difficulty": "Difficulty"},
        color_discrete_map={"Easy": "#22C55E", "Medium": "#F59E0B", "Hard": "#EF4444"},
        text_auto=".1f"
    )
    fig_diff.update_layout(
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        yaxis=dict(range=[0, 105], gridcolor="#E2E8F0"),
        showlegend=False,
        height=300,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    st.plotly_chart(fig_diff, use_container_width=True)

# --- MOST MISSED / VULNERABLE CONCEPTS TABLE ---
st.markdown("### ⚠️ Most-Missed & Vulnerable Loci Concepts")
missed = filtered_df.groupby(["concept_text", "location_name", "topic", "difficulty"]).agg(
    total_tries=("correct_int", "count"),
    correct_tries=("correct_int", "sum"),
    avg_speed=("response_time", "mean"),
    avg_hints=("hints_used", "mean")
).reset_index()

missed["miss_count"] = missed["total_tries"] - missed["correct_tries"]
missed["error_rate_pct"] = (missed["miss_count"] / missed["total_tries"]) * 100
most_vulnerable = missed.sort_values(by=["miss_count", "error_rate_pct"], ascending=False).head(8)

st.dataframe(
    most_vulnerable[[
        "concept_text", "location_name", "topic", "difficulty",
        "total_tries", "miss_count", "error_rate_pct", "avg_speed"
    ]].rename(columns={
        "concept_text": "Concept",
        "location_name": "Locus Station",
        "topic": "Discipline",
        "difficulty": "Difficulty",
        "total_tries": "Total Attempts",
        "miss_count": "Mistakes",
        "error_rate_pct": "Error Rate (%)",
        "avg_speed": "Avg Latency (s)"
    }),
    use_container_width=True,
    hide_index=True
)

# --- DATA EXPORT BUTTON ---
st.markdown("<br>", unsafe_allow_html=True)
csv_buffer = io.StringIO()
filtered_df.to_csv(csv_buffer, index=False)
st.download_button(
    label="📥 Export My Retrieval Data as CSV",
    data=csv_buffer.getvalue(),
    file_name=f"LociLoom_Student_Data_{anon_id}.csv",
    mime="text/csv",
    use_container_width=True
)

render_disclaimer()
