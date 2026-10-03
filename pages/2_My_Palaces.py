"""
LociLoom Page 2: My Palaces Library
Manages saved memory palaces:
- View saved palaces with creation date, subject, concept count, last practice, and next revision due
- Open full palace view with 2D map & story
- Rename, duplicate, and delete palaces
"""
import streamlit as st
from core.ui_helper import setup_page, render_disclaimer
from core.db import get_palaces, get_palace_by_id, update_palace_title, duplicate_palace, delete_palace
from core.palace_builder import (
    create_2d_route_figure, get_text_route_summary,
    render_infographic_storyboard_html, generate_infographic_image_bytes,
    format_palace_summary_text, create_palace_mindmap_figure
)
from core.visual_mapper import generate_mnemonic_photo_card, generate_ai_photo_prompt
from core.tts import generate_speech_audio, get_browser_speech_html

setup_page(title="My Palaces", icon="📚")
anon_id = st.session_state.get("anon_id", "LL-GUEST")
lang = st.session_state.get("language", "en")

st.markdown("## 📚 My Memory Palaces")
st.caption("Review, inspect, duplicate, and organize all your synthesized spatial memory palaces.")

palaces = get_palaces(anon_id)

if not palaces:
    st.info("You haven't saved any memory palaces yet! Visit **Create Palace** to build your first one.")
    if st.button("✨ Create Your First Palace", type="primary"):
        st.switch_page("pages/1_Create_Palace.py")
else:
    # Filter / Search bar
    f_col1, f_col2 = st.columns([2, 1])
    with f_col1:
        search_query = st.text_input("🔍 Search palaces by title or topic", "")
    with f_col2:
        sort_by = st.selectbox("Sort by", ["Newest First", "Oldest First", "Most Concepts", "Next Due Soonest"])

    filtered = [p for p in palaces if search_query.lower() in p["title"].lower() or search_query.lower() in p["topic"].lower()]

    if sort_by == "Newest First":
        filtered.sort(key=lambda x: x["id"], reverse=True)
    elif sort_by == "Oldest First":
        filtered.sort(key=lambda x: x["id"])
    elif sort_by == "Most Concepts":
        filtered.sort(key=lambda x: x["concept_count"], reverse=True)
    elif sort_by == "Next Due Soonest":
        filtered.sort(key=lambda x: x["next_revision_due"] or "9999-99-99")

    st.markdown(f"Showing **{len(filtered)}** memory palace(s):")

    for p in filtered:
        p_id = p["id"]
        created_date = p["created_at"][:10] if p["created_at"] else "Unknown"
        last_prac = p["last_practised"][:10] if p["last_practised"] else "Never"
        next_due = p["next_revision_due"] or "Today"

        with st.container():
            st.markdown(f"""
            <div class="lociloom-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span class="badge badge-primary">{p['topic']}</span>
                        <span style="margin-left: 8px; font-size: 0.8rem; color: #6B7280;">Architecture: <strong>{p['palace_type']}</strong></span>
                        <h3 style="margin: 6px 0 4px 0; color: #1F2937;">{p['title']}</h3>
                    </div>
                    <div style="text-align: right; font-size: 0.82rem; color: #6B7280;">
                        <div>Created: <strong>{created_date}</strong></div>
                        <div>Concepts: <strong>{p['concept_count']}</strong></div>
                    </div>
                </div>
                <div style="display: flex; gap: 20px; font-size: 0.85rem; color: #4B5563; margin-top: 10px; padding-top: 10px; border-top: 1px solid #F3F4F6;">
                    <div>🕒 Last Practised: <strong>{last_prac}</strong></div>
                    <div>📅 Next Revision Due: <strong>{next_due}</strong></div>
                </div>
            </div>
            """, unsafe_allow_html=True)

            b_col1, b_col2, b_col3, b_col4, b_col5 = st.columns([1.2, 1.2, 1.2, 1.2, 1.0])

            with b_col1:
                if st.button("📖 Open / Walk", key=f"open_{p_id}", use_container_width=True):
                    st.session_state["view_palace_id"] = p_id

            with b_col2:
                if st.button("🎯 Quiz Me", key=f"quiz_{p_id}", use_container_width=True, type="primary"):
                    full_p = get_palace_by_id(p_id)
                    st.session_state["quiz_palace"] = full_p
                    if "quiz_deck" in st.session_state:
                        del st.session_state["quiz_deck"]
                    st.switch_page("pages/3_Practice_Quiz.py")

            with b_col3:
                # Rename popover/expander
                with st.popover("✏️ Rename"):
                    new_title = st.text_input("New Title", value=p["title"], key=f"rename_input_{p_id}")
                    if st.button("Confirm", key=f"conf_ren_{p_id}"):
                        update_palace_title(p_id, new_title)
                        st.success("Renamed!")
                        st.rerun()

            with b_col4:
                if st.button("📋 Duplicate", key=f"dup_{p_id}", use_container_width=True):
                    new_id = duplicate_palace(p_id)
                    st.success(f"Duplicated palace as #{new_id}!")
                    st.rerun()

            with b_col5:
                with st.popover("🗑️ Delete"):
                    st.write(f"Delete '{p['title']}' permanently?")
                    if st.button("Yes, Delete", key=f"del_conf_{p_id}", type="primary"):
                        delete_palace(p_id)
                        st.success("Deleted palace.")
                        st.rerun()

    # --- EXPANDED PALACE INSPECTION MODAL / SECTION ---
    if "view_palace_id" in st.session_state and st.session_state["view_palace_id"]:
        v_id = st.session_state["view_palace_id"]
        v_palace = get_palace_by_id(v_id)
        if v_palace:
            st.markdown("---")
            st.markdown(f"### 🏰 Inspecting: {v_palace['title']}")
            
            close_col1, close_col2 = st.columns([4, 1])
            with close_col2:
                if st.button("✖️ Close Inspection"):
                    del st.session_state["view_palace_id"]
                    st.rerun()

            v_concepts = v_palace.get("concepts", [])

            # Narrative Walk
            st.markdown("#### 📖 The Associative Walk Story")
            st.markdown(f"""
            <div class="lociloom-card-highlight">
                <p style="margin: 0; font-size: 1.05rem; line-height: 1.7; color: #1F2937;">
                    {v_palace['story_text']}
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown(get_browser_speech_html(v_palace["story_text"], lang=lang), unsafe_allow_html=True)

            # 2D Route & Storyboard Presentation
            st.markdown("#### 🗺️ Palace Route & Visual Storyboard")
            reduced_motion = st.session_state.get("reduced_motion", False)
            text_only = st.session_state.get("text_only_mode", False)

            if text_only:
                st.markdown(get_text_route_summary(v_concepts))
            else:
                insp_tab_storyboard, insp_tab_mindmap, insp_tab_photos, insp_tab_map, insp_tab_text = st.tabs([
                    "🎨 Visual Storyboard Picture (Comic)",
                    "🧠 Interactive Mind Map",
                    "📸 AI Photo Cards (LLM Mode)",
                    "📐 2D Floorplan Map",
                    "📄 Accessible Text Table"
                ])

                with insp_tab_storyboard:
                    st.html(render_infographic_storyboard_html(v_concepts, title=v_palace["title"]))
                    dl_col1, dl_col2 = st.columns(2)
                    with dl_col1:
                        try:
                            img_bytes = generate_infographic_image_bytes(v_concepts, title=v_palace["title"])
                            st.download_button(
                                label="📥 Download 2D Storyboard Picture (PNG)",
                                data=img_bytes,
                                file_name=f"{v_palace['title'].lower().replace(' ', '_')}_storyboard.png",
                                mime="image/png",
                                key=f"dl_story_{v_id}",
                                use_container_width=True
                            )
                        except Exception:
                            pass
                    with dl_col2:
                        summary_txt = format_palace_summary_text(v_palace, v_concepts)
                        st.download_button(
                            label="📥 Download Summary Sheet (.txt)",
                            data=summary_txt,
                            file_name=f"{v_palace['topic'].lower()}_study_summary.txt",
                            mime="text/plain",
                            key=f"dl_txt_{v_id}",
                            use_container_width=True
                        )

                with insp_tab_mindmap:
                    st.markdown("##### 🧠 Interactive Radial Mind Map")
                    st.caption("Visual knowledge network connecting your palace hub, loci stations, and mnemonic anchors.")
                    v_mindmap = create_palace_mindmap_figure(v_palace["title"], v_palace["topic"], v_concepts)
                    st.plotly_chart(v_mindmap, use_container_width=True)

                with insp_tab_photos:
                    st.markdown("##### 📸 AI Mnemonic Photo Cards & Prompts")
                    st.caption("High-contrast illustrated photo cards and generative image prompts.")
                    vp_cols = st.columns(min(3, max(1, len(v_concepts))))
                    for idx, c in enumerate(v_concepts):
                        col = vp_cols[idx % len(vp_cols)]
                        with col:
                            st.markdown(f"**Stop #{idx+1}: {c['location_name']}**")
                            c_text = c.get("concept_text") or c.get("concept", "")
                            st.caption(f"Anchor: *{c_text}*")
                            card_png = generate_mnemonic_photo_card(
                                concept=c_text,
                                visual_object=c['visual_object'],
                                emoji=c.get('emoji', '📍'),
                                location=c['location_name'],
                                topic=v_palace['topic'],
                                difficulty=c.get('difficulty', 'Medium')
                            )
                            st.image(card_png, use_column_width=True)
                            st.download_button(
                                label=f"📥 Download Station #{idx+1} Photo Card",
                                data=card_png,
                                file_name=f"station_{idx+1}_{c_text[:10].lower().replace(' ', '_')}.png",
                                mime="image/png",
                                key=f"dl_card_my_{v_id}_{idx}",
                                use_container_width=True
                            )
                            with st.expander("🤖 View AI Image Prompt"):
                                ai_prompt = generate_ai_photo_prompt(c_text, c['visual_object'], c['location_name'])
                                st.code(ai_prompt, language="text")

                with insp_tab_map:
                    fig = create_2d_route_figure(v_concepts, title=v_palace["title"], reduced_motion=reduced_motion)
                    st.plotly_chart(fig, use_container_width=True)

                with insp_tab_text:
                    st.markdown(get_text_route_summary(v_concepts))

            # Stations list
            st.markdown("#### 📍 Loci Stations Breakdown")
            c_cols = st.columns(min(3, max(1, len(v_concepts))))
            for idx, c in enumerate(v_concepts):
                col = c_cols[idx % len(c_cols)]
                with col:
                    st.markdown(f"""
                    <div class="location-card">
                        <strong>Stop #{idx+1}: {c['location_name']}</strong>
                        <h4 style="margin: 4px 0;">{c['concept_text']}</h4>
                        <div style="color: #14B8A6; font-size: 0.9rem; font-weight: 600;">{c['visual_object']}</div>
                        <p style="color: #6B7280; font-size: 0.8rem; margin: 4px 0 0 0;">{c['visual_reason']}</p>
                    </div>
                    """, unsafe_allow_html=True)

render_disclaimer()
