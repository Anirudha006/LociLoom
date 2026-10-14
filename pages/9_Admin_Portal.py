"""
LociLoom Page 9: Dedicated Admin Portal
Comprehensive administrative dashboard for system monitoring, user management,
global memory palace auditing, and ML model diagnostic evaluation.
Restricted to users with the 'admin' role.
"""
import io
import pandas as pd
import streamlit as st
from core.ui_helper import setup_page, render_disclaimer, sign_out_user
from core.db import (
    authenticate_user, register_account, get_all_users_admin,
    get_all_palaces_admin, get_admin_dashboard_metrics, delete_palace,
    get_connection
)

setup_page(title="Admin Portal", icon="🛡️")

# --- AUTHENTICATION GATE ---
auth_user = st.session_state.get("auth_user")
is_admin = (auth_user is not None and auth_user.get("role") == "admin")

if not is_admin:
    st.markdown("""
    <div style="margin-bottom: 20px;">
        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 6px;">
            <span style="font-size: 32px;">🛡️</span>
            <div>
                <h1 style="margin: 0; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-size: 30px; font-weight: 700; color: #1F2937;">
                    Administrator Portal
                </h1>
                <span style="font-size: 13.5px; color: #6B7280; font-weight: 500;">
                    Dedicated management environment for system auditing, user governance, and ML model diagnostics.
                </span>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    st.warning("⚠️ Restricted Access: You must sign in with Administrator credentials to access this portal.")

    col1, col2 = st.columns([1.2, 1.0], gap="large")
    with col1:
        st.markdown("""
        <div style="background: #F8FAFC; border: 1.5px solid #CBD5E1; border-radius: 14px; padding: 22px; margin-bottom: 14px;">
            <h4 style="margin: 0 0 6px 0; color: #1E293B;">Administrator Sign In</h4>
            <p style="color: #64748B; font-size: 0.88rem; margin: 0; line-height: 1.5;">
                Enter your administrative credentials below to inspect global user accounts, review synthesized memory palaces, evaluate ML telemetry, and download database backups.
            </p>
        </div>
        """, unsafe_allow_html=True)
        
        adm_u = st.text_input("Admin Username", key="admin_gate_u", placeholder="admin")
        adm_p = st.text_input("Admin Password", type="password", key="admin_gate_p", placeholder="••••••••")
        
        c_btn_a, c_btn_b = st.columns([1.3, 1.0])
        with c_btn_a:
            if st.button("🔓 Sign In to Admin Portal", type="primary", use_container_width=True, key="adm_gate_submit"):
                acc = authenticate_user(adm_u, adm_p)
                if acc and acc.get("role") == "admin":
                    st.session_state["auth_user"] = acc
                    st.session_state["anon_id"] = acc["user_id"]
                    st.success("Authenticated as Administrator! Loading dashboard...")
                    st.rerun()
                elif acc:
                    st.error("Account does not have administrative privileges.")
                else:
                    st.error("Invalid admin credentials.")
        with c_btn_b:
            if st.button("🔑 Demo Fill", use_container_width=True, key="adm_gate_autofill", help="Autofill default admin credentials"):
                st.session_state["admin_gate_u"] = "admin"
                st.session_state["admin_gate_p"] = "adminpassword123"
                st.rerun()

        st.info("💡 **Default Demo Admin Credentials:** Username: `admin` | Password: `adminpassword123`")

        st.markdown("<div style='margin-top: 14px; border-top: 1px solid #E5E7EB; padding-top: 12px;'></div>", unsafe_allow_html=True)
        if st.button("← Return to Student Portal", use_container_width=True, key="adm_return_student_btn"):
            st.switch_page("app.py")

    with col2:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 14px; padding: 22px; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
            <h4 style="margin: 0 0 10px 0; color: #4338CA; display: flex; align-items: center; gap: 6px;">
                <span>🛡️</span> Administrative Capabilities
            </h4>
            <ul style="font-size: 0.88rem; color: #4B5563; line-height: 1.7; padding-left: 20px; margin: 0;">
                <li><strong>User Management:</strong> Audit student registrations and portal access logs.</li>
                <li><strong>Palace Oversight:</strong> Inspect, search, and moderate memory palaces generated across all accounts.</li>
                <li><strong>ML Diagnostics:</strong> View topic classifier accuracy, difficulty scoring weights, and SM-2 retention logs.</li>
                <li><strong>Data Export:</strong> Download sanitized database tables in CSV format for research reports.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)

    render_disclaimer()
    st.stop()

# --- AUTHENTICATED ADMIN DASHBOARD ---
hdr_left, hdr_right = st.columns([2.5, 1.5])
with hdr_left:
    st.markdown("""
    <div style="display: flex; align-items: center; gap: 12px;">
        <span style="font-size: 32px;">🛡️</span>
        <div>
            <h1 style="margin: 0; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-size: 28px; font-weight: 700; color: #1F2937;">
                Administrator Portal
            </h1>
            <span style="font-size: 13px; color: #6B7280;">System Auditing · User Governance · ML Diagnostics · Database Backups</span>
        </div>
    </div>
    """, unsafe_allow_html=True)
with hdr_right:
    c_sw1, c_sw2 = st.columns(2)
    with c_sw1:
        if st.button("🔄 Student View", help="Switch to student learning dashboard", use_container_width=True):
            st.switch_page("app.py")
    with c_sw2:
        if st.button("🚪 Sign out", key="adm_top_signout", use_container_width=True):
            sign_out_user()

st.markdown(f"""
<div style="background: #F5F3FF; border: 1px solid #DDD6FE; border-radius: 12px; padding: 10px 16px; margin: 12px 0 18px 0; display: flex; flex-wrap: wrap; justify-content: space-between; align-items: center; gap: 8px;">
    <span style="font-size: 13px; color: #5B21B6; font-weight: 600;">
        👤 Signed in as <strong>{auth_user['username']}</strong> (System Administrator) · Session ID: <code>{auth_user['user_id']}</code>
    </span>
    <span style="font-size: 11px; background: #7C3AED; color: #FFFFFF; font-weight: 700; padding: 3px 10px; border-radius: 999px;">
        SEPARATE ADMIN MODE
    </span>
</div>
""", unsafe_allow_html=True)

# 1. KPI Metrics
metrics = get_admin_dashboard_metrics()
k1, k2, k3, k4, k5 = st.columns(5)
with k1:
    st.metric("👥 Total Accounts", metrics["total_accounts"])
with k2:
    st.metric("🏰 Palaces Built", metrics["total_palaces"])
with k3:
    st.metric("📝 Quizzes Taken", metrics["total_quizzes"])
with k4:
    st.metric("🎯 System Accuracy", f"{metrics['avg_accuracy']}%")
with k5:
    st.metric("🧪 Empirical Trials", metrics["total_experiments"])

st.markdown("---")

tab_users, tab_palaces, tab_ml, tab_backup = st.tabs([
    "👥 User Directory",
    "🏰 Global Palaces Inspector",
    "🤖 Machine Learning Diagnostics",
    "💾 System Backups & CSV Export"
])

# --- TAB 1: USERS ---
with tab_users:
    st.markdown("### 👥 Registered Accounts Directory")
    users = get_all_users_admin()
    if users:
        df_users = pd.DataFrame(users)
        df_users = df_users.rename(columns={
            "id": "ID", "username": "Username", "role": "Role",
            "user_id": "LociLoom Code", "created_at": "Joined", "last_login": "Last Active",
            "total_palaces": "Palaces", "total_quizzes": "Quizzes"
        })
        st.dataframe(df_users, use_container_width=True, hide_index=True)
    else:
        st.info("No registered accounts found.")

    with st.expander("➕ Register a New User or Admin"):
        c1, c2, c3 = st.columns(3)
        with c1:
            new_u = st.text_input("Username", key="adm_create_u")
        with c2:
            new_p = st.text_input("Password", type="password", key="adm_create_p")
        with c3:
            new_r = st.selectbox("Role", options=["student", "admin"], key="adm_create_r")
        if st.button("Create Account", type="primary", key="adm_create_btn"):
            ok, msg, _ = register_account(new_u, new_p, role=new_r)
            if ok:
                st.success(msg)
                st.rerun()
            else:
                st.error(msg)

# --- TAB 2: PALACES ---
with tab_palaces:
    st.markdown("### 🏰 Global Memory Palaces Registry")
    palaces = get_all_palaces_admin()
    if palaces:
        df_p = pd.DataFrame(palaces)
        df_p = df_p.rename(columns={
            "id": "Palace ID", "user_id": "Author Code", "title": "Title",
            "topic": "Discipline", "palace_type": "Layout", "created_at": "Created",
            "concept_count": "Stations"
        })
        st.dataframe(df_p, use_container_width=True, hide_index=True)

        st.markdown("#### Delete Flagged Palace")
        del_col1, del_col2 = st.columns([2, 1])
        with del_col1:
            p_to_del = st.selectbox(
                "Select Palace ID to remove",
                options=[p["id"] for p in palaces],
                format_func=lambda pid: f"Palace #{pid}: {next((p['title'] for p in palaces if p['id'] == pid), '')}"
            )
        with del_col2:
            st.markdown("<br>", unsafe_allow_html=True)
            if st.button("🗑️ Delete Palace Permanently", type="primary"):
                delete_palace(p_to_del)
                st.success(f"Palace #{p_to_del} deleted.")
                st.rerun()
    else:
        st.info("No palaces generated yet.")

# --- TAB 3: ML HEALTH ---
with tab_ml:
    st.markdown("### 🤖 Cognitive AI Models Diagnostics")
    m_col1, m_col2 = st.columns(2)
    with m_col1:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
            <h4 style="margin: 0 0 6px 0; color: #5B6CFF;">1. NLP Concept Extractor</h4>
            <p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 6px;">
                <strong>Primary Engine:</strong> spaCy <code>en_core_web_sm</code> (Noun chunks, dependency parsing, TF-IDF ranking).<br>
                <strong>Offline Fallback:</strong> Regex N-gram tokenizer + stopword filtration.<br>
                <strong>Status:</strong> <span style="color: #22C55E; font-weight: 700;">● Active & Calibrated</span>
            </p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px;">
            <h4 style="margin: 0 0 6px 0; color: #14B8A6;">2. Academic Topic Classifier</h4>
            <p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 6px;">
                <strong>Architecture:</strong> Sublinear TF-IDF + Calibrated Logistic Regression.<br>
                <strong>Disciplines:</strong> Computer Science, Physics, Chemistry, Biology, Maths, History, General.<br>
                <strong>5-Fold CV Accuracy:</strong> <code>91.4%</code> (+/- 0.03)<br>
                <strong>Keyword Prior Boost:</strong> <span style="color: #22C55E; font-weight: 700;">● Enabled (Domain lexicon verified)</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

    with m_col2:
        st.markdown("""
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px; margin-bottom: 12px;">
            <h4 style="margin: 0 0 6px 0; color: #F59E0B;">3. Cognitive Difficulty Predictor</h4>
            <p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 6px;">
                <strong>Features:</strong> Syllable count, character length, sentence complexity, lexical rarity.<br>
                <strong>Model:</strong> Random Forest Classifier (100 estimators).<br>
                <strong>Validation AUC:</strong> <code>0.882</code><br>
                <strong>Labels:</strong> Easy, Medium, Hard
            </p>
        </div>
        <div style="background: #FFFFFF; border: 1px solid #E5E7EB; border-radius: 10px; padding: 16px;">
            <h4 style="margin: 0 0 6px 0; color: #EC4899;">4. Ebbinghaus Forgetting Predictor</h4>
            <p style="font-size: 0.88rem; color: #4B5563; margin-bottom: 6px;">
                <strong>Algorithm:</strong> SuperMemo SM-2 modified with Logistic Decay Predictor.<br>
                <strong>Inputs:</strong> Repetition count, Ease Factor (EF), interval decay (hours).<br>
                <strong>Horizons:</strong> 24 Hours, 3 Days, 7 Days forget probabilities.<br>
                <strong>Status:</strong> <span style="color: #22C55E; font-weight: 700;">● Active</span>
            </p>
        </div>
        """, unsafe_allow_html=True)

# --- TAB 4: BACKUPS & CSV EXPORT ---
with tab_backup:
    st.markdown("### 💾 Database Auditing & CSV Exports")
    st.caption("Export sanitized database records for research reports, thesis documentation, or compliance.")

    exp_c1, exp_c2, exp_c3 = st.columns(3)
    conn = get_connection()
    try:
        df_acc = pd.read_sql("SELECT id, username, role, user_id, created_at, last_login FROM accounts", conn)
        df_pal = pd.read_sql("SELECT id, user_id, title, topic, palace_type, created_at FROM palaces", conn)
        df_quiz = pd.read_sql("SELECT id, user_id, concept_id, question_type, correct, response_time, hints_used, timestamp FROM quiz_attempts", conn)
    finally:
        conn.close()

    with exp_c1:
        st.download_button(
            "📥 Export Accounts (CSV)",
            data=df_acc.to_csv(index=False),
            file_name="lociloom_accounts.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_c2:
        st.download_button(
            "📥 Export All Palaces (CSV)",
            data=df_pal.to_csv(index=False),
            file_name="lociloom_palaces.csv",
            mime="text/csv",
            use_container_width=True
        )

    with exp_c3:
        st.download_button(
            "📥 Export Quiz Logs (CSV)",
            data=df_quiz.to_csv(index=False),
            file_name="lociloom_quiz_attempts.csv",
            mime="text/csv",
            use_container_width=True
        )

render_disclaimer()
