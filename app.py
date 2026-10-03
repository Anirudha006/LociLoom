"""
LociLoom: An AI-Based Personalized Memory Palace Generator for Adaptive Learning
Main Entry Point & Home Hub
Matches the design from assets/website_home.html for the authenticated home experience
and assets/login_reference.html for the authentication portal.
"""
import uuid
import streamlit as st
import streamlit.components.v1 as components
from core.ui import (
    setup_page,
    load_css,
    format_loci_id,
    get_animated_sample_map_html,
    get_animated_login_map_html,
    render_disclaimer,
    t
)
from core.db import authenticate_user, register_account, get_palaces

auth_user = st.session_state.get("auth_user")
is_logged_in = auth_user is not None

# When not logged in, hide sidebar and show clean login screen
setup_page(title="Login" if not is_logged_in else "Home", icon="🏛️", hide_sidebar=(not is_logged_in))

lang = st.session_state.get("language", "en")

# ==============================================================================
# 1. LOGIN & ONBOARDING VIEW (When User is Not Logged In)
# ==============================================================================
if not is_logged_in:
    login_cover_css = (
        "<style>"
        "[data-testid='stSidebar'], [data-testid='stSidebarNav'], [data-testid='collapsedControl'], "
        "[data-testid='stSidebarCollapsedControl'], [data-testid='stSidebarCollapseButton'], "
        "section[data-testid='stSidebar'], button[data-testid='stSidebarCollapseButton'] { "
        "display: none !important; width: 0 !important; visibility: hidden !important; pointer-events: none !important; } "
        "header[data-testid='stHeader'], footer { display: none !important; } "
        "html, body, [data-testid='stAppViewContainer'], .main, [data-testid='stMain'] { "
        "background-color: #F7F8FC !important; min-height: 100vh !important; width: 100% !important; margin: 0 !important; padding: 0 !important; } "
        ".main, [data-testid='stAppViewContainer'] > .main, [data-testid='stMain'] { margin-left: 0 !important; padding-left: 0 !important; width: 100% !important; } "
        ".main .block-container, [data-testid='stMainBlockContainer'] { max-width: 1060px !important; width: 95% !important; "
        "padding-top: 12px !important; padding-bottom: 16px !important; padding-left: 14px !important; padding-right: 14px !important; margin: 0 auto !important; } "
        "[data-testid='stColumn']:first-child [data-testid='stVerticalBlockBorderWrapper'] { "
        "background: #FFFFFF !important; border: 1px solid #E8EBF4 !important; border-radius: 18px !important; "
        "padding: 22px 24px !important; box-shadow: 0 1px 2px rgba(31, 41, 55, 0.04), 0 12px 32px rgba(69, 83, 232, 0.07) !important; } "
        "[data-testid='stColumn'] [data-testid='stVerticalBlock'] { gap: 0.6rem !important; } "
        "</style>"
    )
    st.markdown(login_cover_css, unsafe_allow_html=True)

    # Top Header Bar for Login Screen
    hdr_col1, hdr_col2 = st.columns([1, 1])
    with hdr_col1:
        st.markdown("""
        <div style="display: flex; align-items: center; gap: 10px; padding: 0 0 10px 0;">
            <svg width="34" height="34" viewBox="0 0 40 40" role="img" aria-label="LociLoom logo">
                <rect width="40" height="40" rx="10" fill="#4553E8"/>
                <path d="M11 28 C11 20 18 22 20 17 C22 12 29 14 29 12" fill="none" stroke="#FFFFFF" stroke-width="2.5" stroke-linecap="round" stroke-dasharray="1 5"/>
                <circle cx="11" cy="28" r="3.5" fill="#FFFFFF"/>
                <circle cx="29" cy="12" r="3.5" fill="#FBBF24"/>
            </svg>
            <span style="font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 22px; letter-spacing: -0.02em; color: #1F2937;">
                LociLoom
            </span>
        </div>
        """, unsafe_allow_html=True)

    with hdr_col2:
        c_sub, c_lang = st.columns([1.6, 1.2])
        with c_sub:
            st.markdown("""
            <div style="display: flex; justify-content: flex-end; align-items: center; height: 100%; padding-top: 2px;">
                <span style="font-size: 12.5px; color: #6B7280; font-weight: 600;">Method of Loci · Adaptive Retrieval</span>
            </div>
            """, unsafe_allow_html=True)
        with c_lang:
            lang_options = {"en": "English", "hi": "Hindi (हिंदी)", "kn": "Kannada (ಕನ್ನಡ)"}
            curr_l = st.session_state.get("language", "en")
            new_l = st.selectbox(
                "UI Language",
                options=list(lang_options.keys()),
                format_func=lambda x: lang_options[x],
                index=list(lang_options.keys()).index(curr_l) if curr_l in lang_options else 0,
                key="login_lang_select",
                label_visibility="collapsed"
            )
            if new_l != curr_l:
                st.session_state["language"] = new_l
                st.rerun()

    col_card, col_aside = st.columns([1.0, 1.15], gap="large")

    # Left Column: Login Card
    with col_card:
        with st.container(border=True):
            st.markdown("""
            <div>
                <h1 class="login-title">Walk back into your palace.</h1>
                <p class="login-subtitle">
                    Sign in with your anonymous Loci ID. No name, no email, just your notes turned into places you can remember.
                </p>
            </div>
            """, unsafe_allow_html=True)

            tab_return, tab_new = st.tabs(["I have a Loci ID", "I'm new here"])

            with tab_return:
                st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
                loci_id_input = st.text_input(
                    "Loci ID or Username",
                    placeholder="LOCI-7K2Q-M9 or student",
                    key="ret_loci_id",
                    help="Enter your anonymous Loci ID or custom username."
                )
                passcode_input = st.text_input(
                    "Password (7 to 15 digits)",
                    type="password",
                    placeholder="••••••••",
                    key="ret_passcode",
                    help="Your private access password (7 to 15 digits/characters)."
                )
                remember_me = st.checkbox("Remember me on this device", value=True, key="ret_remember")

                enter_btn = st.button("🚪 Enter my palace ➔", type="primary", use_container_width=True, key="ret_submit_btn")
                if enter_btn:
                    if not loci_id_input or not passcode_input:
                        st.warning("Please enter your Loci ID and password.")
                    else:
                        account = authenticate_user(loci_id_input, passcode_input)
                        if account:
                            st.session_state["auth_user"] = account
                            st.session_state["anon_id"] = account["user_id"]
                            st.success(f"Welcome back, {account['username']}!")
                            st.rerun()
                        else:
                            st.error("Invalid Loci ID or password. If you are new, select 'I'm new here'.")

            with tab_new:
                st.markdown("<div style='margin-top: 6px;'></div>", unsafe_allow_html=True)
                if "temp_new_loci_id" not in st.session_state:
                    raw_token = uuid.uuid4().hex[:6].upper()
                    st.session_state["temp_new_loci_id"] = f"LOCI-{raw_token[:4]}-{raw_token[4:6]}"

                new_id = st.session_state["temp_new_loci_id"]

                st.markdown(f"""
                <div style="font-size: 13px; font-weight: 600; color: #1F2937; margin-bottom: 4px;">Your new Loci ID</div>
                <div class="loci-idbox">
                    <div><b>{new_id}</b></div>
                </div>
                """, unsafe_allow_html=True)

                if st.button("🔄 Generate Another ID", key="gen_id_btn"):
                    raw_token = uuid.uuid4().hex[:6].upper()
                    st.session_state["temp_new_loci_id"] = f"LOCI-{raw_token[:4]}-{raw_token[4:6]}"
                    st.rerun()

                st.markdown("""
                <p style="font-size: 12px; line-height: 1.45; color: #4B5563; margin-top: 6px;">
                    Save this ID somewhere safe. We don't collect an email, so we can't recover it for you.
                </p>
                """, unsafe_allow_html=True)

                new_passcode = st.text_input(
                    "Choose a Password (7 to 15 digits)",
                    type="password",
                    placeholder="••••••••",
                    key="new_passcode_input",
                    help="Password must be between 7 and 15 digits or characters."
                )
                agree_storage = st.checkbox(
                    "I agree to my study activity being stored on this device to personalise my revision plan.",
                    value=True,
                    key="new_agree_checkbox"
                )

                create_key_btn = st.button("✨ Create my palace key", type="primary", use_container_width=True, key="new_submit_btn")
                if create_key_btn:
                    if not new_passcode or len(new_passcode) < 7 or len(new_passcode) > 15:
                        st.warning("Please choose a password with 7 to 15 digits or characters.")
                    elif not agree_storage:
                        st.warning("Please accept local storage agreement to enable adaptive spaced repetition.")
                    else:
                        ok, msg, acc = register_account(new_id, new_passcode, role="student")
                        if ok and acc:
                            st.session_state["auth_user"] = acc
                            st.session_state["anon_id"] = acc["user_id"]
                            st.success("Palace key created successfully! Entering LociLoom...")
                            st.rerun()
                        else:
                            st.error(msg)

            st.markdown('<div class="or-divider">or</div>', unsafe_allow_html=True)
            if st.button("Try a sample palace as guest", use_container_width=True, key="guest_btn"):
                st.session_state["anon_id"] = f"LL-GUEST-{uuid.uuid4().hex[:4].upper()}"
                st.switch_page("pages/1_Create_Palace.py")

            st.markdown("""
            <p class="privacy-note">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#0B8F84" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true" style="flex: none; margin-top: 1px;">
                    <path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6l8-3z"/>
                    <path d="M9 12l2 2 4-4"/>
                </svg>
                <span>
                    <strong>Private by design.</strong> Only an anonymous ID is used, and your data stays in a local database on your device.
                </span>
            </p>
            """, unsafe_allow_html=True)

    with col_aside:
        components.html(get_animated_login_map_html(), height=480)

    st.markdown("""
    <div style="margin-top: 16px; text-align: center; color: #6B7280; font-size: 11.5px; line-height: 1.5; border-top: 1px solid #E5E7EB; padding-top: 10px;">
        <p style="margin: 0;">LociLoom Memory Palace Generator · An experimental spatial mnemonic learning system. Cognitive research study edition.</p>
    </div>
    """, unsafe_allow_html=True)

# ==============================================================================
# 2. AUTHENTICATED HOME VIEW (Matching assets/website_home.html)
# ==============================================================================
else:
    user_id = auth_user.get("user_id", "")
    username = auth_user.get("username", "Student")
    clean_id = format_loci_id(user_id)
    role = auth_user.get("role", "student")
    is_admin = (role == "admin")
    role_subtitle = "Administrator Portal" if is_admin else "Student Learning Portal"

    # --- 1. WELCOME CARD ---
    st.markdown(f"""
    <section style="background: #FFFFFF; border: 1px solid #E8EBF4; border-radius: 28px; padding: 30px 32px; box-shadow: 0 1px 2px rgba(31,41,55,.04), 0 12px 32px rgba(69,83,232,.07); display: flex; flex-wrap: wrap; gap: 20px; align-items: center; justify-content: space-between; margin-bottom: 26px;">
        <div style="display: flex; flex-direction: column; gap: 10px; flex: 1 1 380px; min-width: 0;">
            <span style="align-self: flex-start; padding: 5px 12px; border-radius: 999px; background: #EEF0FF; color: #3441CF; font-size: 13px; font-weight: 700;">
                ● Active session · {role_subtitle}
            </span>
            <h1 class="hm-h1" style="margin: 0; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 38px; line-height: 1.1; letter-spacing: -0.025em; color: #1F2937;">
                Welcome back into your palace, {username}!
            </h1>
            <p style="margin: 0; font-size: 15px; line-height: 1.55; color: #4B5563;">
                Your notes are waiting along the route. Pick a room below to step inside.
            </p>
        </div>
        <div style="display: flex; align-items: center; gap: 10px; padding: 12px 18px; background: #ECFDF9; border: 1.5px solid #99E6D8; border-radius: 16px; font-size: 14px; color: #0B5F57; font-weight: 600;">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="#0B8F84" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                <path d="M12 3l8 3v6c0 4.5-3.4 8-8 9-4.6-1-8-4.5-8-9V6l8-3z"/>
                <path d="M9 12l2 2 4-4"/>
            </svg>
            Private local storage active
        </div>
    </section>
    """, unsafe_allow_html=True)

    # --- 2. PALACE MAP NAVIGATION (12-Column Grid) ---
    st.markdown("""
    <div style="margin-bottom: 16px;">
        <h2 style="margin: 0; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 28px; letter-spacing: -0.02em; color: #1F2937;">
            Where shall we walk today?
        </h2>
        <p style="margin: 4px 0 0 0; font-size: 15px; color: #4B5563;">
            Every part of LociLoom is a room on your study route.
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Row 1: Large Tile 1 on the left (6 cols) + 2x2 grid on the right (6 cols)
    r1_col1, r1_col2 = st.columns([1.0, 1.0], gap="medium")

    with r1_col1:
        # Tile 1: Weave a new palace (STOP 1 · THE WORKSHOP)
        with st.container(key="tile_workshop"):
            st.markdown("""
            <div class="hm-tile" style="min-height: 340px; background: #4553E8; color: #FFFFFF; border-radius: 28px; padding: 26px; box-shadow: 0 10px 28px rgba(69,83,232,.28);">
                <div class="hm-top">
                    <span class="hm-ic" style="width: 48px; height: 48px; border-radius: 16px; background: rgba(255,255,255,.18);">
                        <svg width="26" height="26" viewBox="0 0 24 24" fill="none" stroke="#FFFFFF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M12 3v3M12 18v3M3 12h3M18 12h3"/>
                            <path d="M12 8l1.5 3.5L17 13l-3.5 1.5L12 18l-1.5-3.5L7 13l3.5-1.5L12 8z"/>
                        </svg>
                    </span>
                    <span style="padding: 6px 12px; border-radius: 999px; background: #FBBF24; color: #3B2A00; font-size: 13px; font-weight: 700;">
                        Start here
                    </span>
                </div>
                <svg viewBox="0 0 360 100" width="100%" role="img" aria-label="A route of four stops being walked" style="display: block; max-width: 100%; height: auto; margin: 6px 0;">
                    <path class="hm-march" d="M24 78 C84 78 84 24 160 24 C236 24 236 78 296 78 C320 78 330 56 338 36" fill="none" stroke="rgba(255,255,255,.9)" stroke-width="3" stroke-linecap="round"/>
                    <g font-family="Bricolage Grotesque, sans-serif" font-size="13" font-weight="700" fill="#4553E8" text-anchor="middle">
                        <circle class="hm-stop" cx="24" cy="78" r="14" fill="#FFFFFF"/><text x="24" y="83">1</text>
                        <circle class="hm-stop" cx="160" cy="24" r="14" fill="#FFFFFF" style="animation-delay: .7s;"/><text x="160" y="29">2</text>
                        <circle class="hm-stop" cx="296" cy="78" r="14" fill="#FFFFFF" style="animation-delay: 1.4s;"/><text x="296" y="83">3</text>
                        <circle class="hm-stop" cx="338" cy="36" r="14" fill="#FBBF24" style="animation-delay: 2.1s;"/><text x="338" y="41" fill="#3B2A00">4</text>
                    </g>
                    <g class="hm-walker">
                        <circle r="7" fill="#FBBF24" stroke="#FFFFFF" stroke-width="2.5"/>
                        <animateMotion dur="7s" repeatCount="indefinite" path="M24 78 C84 78 84 24 160 24 C236 24 236 78 296 78 C320 78 330 56 338 36"/>
                    </g>
                </svg>
                <div class="hm-txt">
                    <span class="hm-lab" style="opacity: .9;">STOP 1 · THE WORKSHOP</span>
                    <span style="font-family: 'Bricolage Grotesque', sans-serif; font-weight: 700; font-size: 30px; line-height: 1.05; letter-spacing: -0.02em;">Weave a new palace</span>
                    <span style="font-size: 14.5px; line-height: 1.45; max-width: 400px; opacity: .95;">Paste your notes, choose a place, and watch them turn into a route with a story.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/1_Create_Palace.py", label="Begin ➔", use_container_width=True)

    with r1_col2:
        # Sub-row 1: Tiles 2 & 3
        sub_c1, sub_c2 = st.columns(2, gap="medium")
        with sub_c1:
            with st.container(key="tile_library"):
                st.markdown("""
                <div class="hm-tile" style="min-height: 154px; background: #FEF3C7;">
                    <div class="hm-top">
                        <span class="hm-ic">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#B45309" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M3 9l9-5 9 5"/><path d="M5 10v8M9 10v8M15 10v8M19 10v8"/><path d="M3 20h18"/>
                            </svg>
                        </span>
                        <span class="hm-no" style="color: #92400E;">2</span>
                    </div>
                    <div class="hm-txt">
                        <span class="hm-lab" style="color: #92400E;">THE LIBRARY</span>
                        <span class="hm-ti">My Palaces</span>
                        <span class="hm-de">Reopen, rename and duplicate your palaces.</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.page_link("pages/2_My_Palaces.py", label="Open library ➔", use_container_width=True)

        with sub_c2:
            with st.container(key="tile_training"):
                st.markdown("""
                <div class="hm-tile" style="min-height: 154px; background: #CCFBEF;">
                    <div class="hm-top">
                        <span class="hm-ic">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#0B5F57" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="5"/><circle cx="12" cy="12" r="1.5"/>
                            </svg>
                        </span>
                        <span class="hm-no" style="color: #0B5F57;">3</span>
                    </div>
                    <div class="hm-txt">
                        <span class="hm-lab" style="color: #0B5F57;">THE TRAINING ROOM</span>
                        <span class="hm-ti">Practice Quiz</span>
                        <span class="hm-de">Walk the route and answer by location.</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.page_link("pages/3_Practice_Quiz.py", label="Start quiz ➔", use_container_width=True)

        # Sub-row 2: Tiles 4 & 5
        sub_c3, sub_c4 = st.columns(2, gap="medium")
        with sub_c3:
            with st.container(key="tile_calendar"):
                st.markdown("""
                <div class="hm-tile" style="min-height: 154px; background: #E0E7FF;">
                    <div class="hm-top">
                        <span class="hm-ic">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#3441CF" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <rect x="3.5" y="5" width="17" height="15" rx="3"/><path d="M3.5 10h17M8 3v4M16 3v4"/>
                            </svg>
                        </span>
                        <span class="hm-no" style="color: #3441CF;">4</span>
                    </div>
                    <div class="hm-txt">
                        <span class="hm-lab" style="color: #3441CF;">THE CALENDAR TOWER</span>
                        <span class="hm-ti">Revision Planner</span>
                        <span class="hm-de">See what to revise today.</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.page_link("pages/4_Revision_Planner.py", label="View schedule ➔", use_container_width=True)

        with sub_c4:
            with st.container(key="tile_observatory"):
                st.markdown("""
                <div class="hm-tile" style="min-height: 154px; background: #DBEAFE;">
                    <div class="hm-top">
                        <span class="hm-ic">
                            <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#1D4ED8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                                <path d="M5 20V11M12 20V5M19 20v-7"/>
                            </svg>
                        </span>
                        <span class="hm-no" style="color: #1D4ED8;">5</span>
                    </div>
                    <div class="hm-txt">
                        <span class="hm-lab" style="color: #1D4ED8;">THE OBSERVATORY</span>
                        <span class="hm-ti">Dashboard</span>
                        <span class="hm-de">Scores, streaks and missed concepts.</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                st.page_link("pages/5_Dashboard.py", label="View dashboard ➔", use_container_width=True)

    # Row 2: Tiles 6, 7, 8 (4 cols each in 12-col grid)
    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    r2_c1, r2_c2, r2_c3 = st.columns(3, gap="medium")

    with r2_c1:
        with st.container(key="tile_lab"):
            st.markdown("""
            <div class="hm-tile" style="min-height: 140px; background: #FFEFD9;">
                <div class="hm-top">
                    <span class="hm-ic">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#B45309" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M9 3h6M10 3v6l-5.5 9.5A1.5 1.5 0 0 0 5.8 21h12.4a1.5 1.5 0 0 0 1.3-2.5L14 9V3"/>
                        </svg>
                    </span>
                    <span class="hm-no" style="color: #92400E;">6</span>
                </div>
                <div class="hm-txt">
                    <span class="hm-lab" style="color: #92400E;">THE LAB</span>
                    <span class="hm-ti">Experiment Mode</span>
                    <span class="hm-de">Compare notes with a palace.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/6_Experiment_Mode.py", label="Enter lab ➔", use_container_width=True)

    with r2_c2:
        with st.container(key="tile_control"):
            st.markdown("""
            <div class="hm-tile" style="min-height: 140px; background: #FFFFFF; border: 1px solid #E3E6F0;">
                <div class="hm-top">
                    <span class="hm-ic" style="background: #F1F3FA;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <path d="M4 7h10M18 7h2M4 17h2M10 17h10"/><circle cx="16" cy="7" r="2"/><circle cx="8" cy="17" r="2"/>
                        </svg>
                    </span>
                    <span class="hm-no" style="color: #4B5563;">7</span>
                </div>
                <div class="hm-txt">
                    <span class="hm-lab" style="color: #4B5563;">THE CONTROL ROOM</span>
                    <span class="hm-ti">Settings &amp; Accessibility</span>
                    <span class="hm-de">Font, contrast, text-only mode, audio.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/7_Settings_Accessibility.py", label="Open settings ➔", use_container_width=True)

    with r2_c3:
        with st.container(key="tile_info"):
            st.markdown("""
            <div class="hm-tile" style="min-height: 140px; background: #FFFFFF; border: 1px solid #E3E6F0;">
                <div class="hm-top">
                    <span class="hm-ic" style="background: #F1F3FA;">
                        <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="#374151" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                            <circle cx="12" cy="12" r="9"/><path d="M9.5 9.5a2.5 2.5 0 1 1 3.5 2.3c-.7.4-1 1-1 1.7M12 17h.01"/>
                        </svg>
                    </span>
                    <span class="hm-no" style="color: #4B5563;">8</span>
                </div>
                <div class="hm-txt">
                    <span class="hm-lab" style="color: #4B5563;">THE INFO DESK</span>
                    <span class="hm-ti">About &amp; Help</span>
                    <span class="hm-de">How the method and the ML parts work.</span>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/8_About_and_Help.py", label="Learn more ➔", use_container_width=True)

    # --- 3. LOWER SPLIT: STUDY PALACES & PRINCIPLE (Left) + SAMPLE PALACE MAP (Right) ---
    st.markdown("<div style='margin-top: 32px;'></div>", unsafe_allow_html=True)
    sec_left, sec_right = st.columns([1.1, 1.0], gap="large")

    with sec_left:
        # A. Your Study Palaces
        st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="margin: 0; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 26px; letter-spacing: -0.02em; color: #1F2937;">
                Your study palaces
            </h2>
        </div>
        """, unsafe_allow_html=True)

        user_palaces = get_palaces(user_id)
        if user_palaces:
            for p in user_palaces[:3]:
                last_dt = p.get("last_practised") or "Not yet practiced"
                next_rev = p.get("next_revision_due") or "Pending scheduled review"
                if len(str(last_dt)) > 16:
                    last_dt = str(last_dt)[:16].replace("T", " ")
                if len(str(next_rev)) > 16:
                    next_rev = str(next_rev)[:16].replace("T", " ")

                st.markdown(f"""
                <div style="background: #FFFFFF; border: 1px solid #E8EBF4; border-radius: 18px; padding: 18px 20px; margin-bottom: 12px; box-shadow: 0 1px 2px rgba(31,41,55,.04); display: flex; flex-direction: column; gap: 8px;">
                    <div style="display: flex; justify-content: space-between; align-items: flex-start; gap: 8px;">
                        <div>
                            <span style="font-family: 'Bricolage Grotesque', sans-serif; font-size: 18px; font-weight: 700; color: #1F2937;">{p['title']}</span>
                            <div style="font-size: 13px; color: #6B7280; margin-top: 2px;">
                                Topic: <strong style="color: #4553E8;">{p['topic']}</strong> · {p.get('concept_count', 0)} Loci
                            </div>
                        </div>
                        <span style="padding: 4px 10px; border-radius: 999px; background: #EEF0FF; color: #3441CF; font-size: 11.5px; font-weight: 700;">
                            {p['palace_type']}
                        </span>
                    </div>
                    <div style="display: flex; gap: 16px; font-size: 12px; color: #4B5563; border-top: 1px solid #F1F3FA; padding-top: 8px;">
                        <span>Last tested: <strong>{last_dt}</strong></span>
                        <span>Next revision: <strong>{next_rev}</strong></span>
                    </div>
                </div>
                """, unsafe_allow_html=True)

            if len(user_palaces) > 3:
                st.caption(f"Showing 3 of {len(user_palaces)} saved palaces.")
            st.page_link("pages/2_My_Palaces.py", label="View all in My Palaces ➔")
        else:
            st.markdown("""
            <div style="background: #FFFFFF; border: 1.5px dashed #C7CDF5; border-radius: 22px; padding: 22px 24px; display: flex; flex-direction: column; gap: 14px; align-items: flex-start; margin-bottom: 12px;">
                <div style="display: flex; align-items: center; gap: 14px;">
                    <span style="flex: none; display: flex; align-items: center; justify-content: center; width: 44px; height: 44px; border-radius: 14px; background: #EEF0FF;">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#4553E8" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">
                            <path d="M3 9l9-5 9 5"/><path d="M5 10v8M9 10v8M15 10v8M19 10v8"/><path d="M3 20h18"/>
                        </svg>
                    </span>
                    <p style="margin: 0; font-size: 14.5px; line-height: 1.5; color: #374151;">
                        You haven't woven a memory palace yet. Your first one takes only a minute.
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            st.page_link("pages/1_Create_Palace.py", label="✨ Weave your first palace ➔")

        # B. The Method of Loci Principles
        st.markdown("<div style='margin-top: 24px;'></div>", unsafe_allow_html=True)
        st.markdown("""
        <div style="margin-bottom: 12px;">
            <h2 style="margin: 0; font-family: 'Bricolage Grotesque', system-ui, sans-serif; font-weight: 700; font-size: 26px; letter-spacing: -0.02em; color: #1F2937;">
                The Method of Loci
            </h2>
        </div>
        <ol style="list-style: none; margin: 0; padding: 0; display: flex; flex-direction: column; gap: 12px;">
            <li style="display: flex; gap: 14px; align-items: flex-start; background: #FFFFFF; border: 1px solid #E8EBF4; border-radius: 18px; padding: 15px 18px;">
                <span style="flex: none; display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: #4553E8; color: #FFFFFF; font: 700 15px 'Bricolage Grotesque', sans-serif;">1</span>
                <span style="font-size: 14.5px; line-height: 1.55; color: #374151;">
                    <strong style="color: #1F2937;">Abstract notes become concrete objects.</strong> Hard concepts turn into things you can picture.
                </span>
            </li>
            <li style="display: flex; gap: 14px; align-items: flex-start; background: #FFFFFF; border: 1px solid #E8EBF4; border-radius: 18px; padding: 15px 18px;">
                <span style="flex: none; display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: #4553E8; color: #FFFFFF; font: 700 15px 'Bricolage Grotesque', sans-serif;">2</span>
                <span style="font-size: 14.5px; line-height: 1.55; color: #374151;">
                    <strong style="color: #1F2937;">Objects are anchored in space.</strong> Each one sits at a stop along an ordered journey through a familiar place.
                </span>
            </li>
            <li style="display: flex; gap: 14px; align-items: flex-start; background: #FFFFFF; border: 1px solid #E8EBF4; border-radius: 18px; padding: 15px 18px;">
                <span style="flex: none; display: flex; align-items: center; justify-content: center; width: 30px; height: 30px; border-radius: 50%; background: #D97706; color: #FFFFFF; font: 700 15px 'Bricolage Grotesque', sans-serif;">3</span>
                <span style="font-size: 14.5px; line-height: 1.55; color: #374151;">
                    <strong style="color: #1F2937;">Recall and spaced repetition.</strong> Test the route with quizzes and SM-2 scheduling to slow forgetting.
                </span>
            </li>
        </ol>
        """, unsafe_allow_html=True)

    with sec_right:
        # Animated Sample Palace Floor-Plan Route Map (Matching assets/website_home.html)
        is_reduced = st.session_state.get("reduced_motion", False)
        components.html(get_animated_sample_map_html(reduced_motion=is_reduced), height=530)

    # --- 4. FOOTER ---
    st.markdown("""
    <div style="margin-top: 36px; text-align: center; color: #4B5563; font-size: 13px; line-height: 1.6; border-top: 1px solid #E5E7EB; padding-top: 20px;">
        <p style="margin: 0;">LociLoom is a study aid, not a guaranteed memory treatment. It works best alongside retrieval practice and spaced repetition.</p>
    </div>
    """, unsafe_allow_html=True)
