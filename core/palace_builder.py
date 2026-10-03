"""
LociLoom Palace Builder and 2D Route Visualizer
Allocates concepts to virtual or personalized physical loci.
Generates:
1. Ordered locus route assignment (House, Classroom, Garden, Campus, or Custom)
2. Interactive 2D architectural map using Plotly with light theme and animated walk
3. Accessible text-only route alternative for screen readers and non-visual learners
"""
import os
import re
import json
import math
from typing import List, Dict, Any, Optional, Tuple
import plotly.graph_objects as go

TEMPLATES_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "palace_templates.json")

def load_palace_templates() -> Dict[str, Any]:
    """Loads default palace templates from JSON."""
    if os.path.exists(TEMPLATES_PATH):
        with open(TEMPLATES_PATH, "r", encoding="utf-8-sig") as f:
            return json.load(f)
    return {}

def parse_custom_locations(raw_input: str) -> List[Dict[str, Any]]:
    """
    Parses comma- or newline-separated custom locations provided by the student.
    Assigns sequential coordinate positions in a neat winding serpentine path.
    """
    lines = [loc.strip() for loc in re.split(r'[,;\n]+', raw_input) if loc.strip()]
    locations = []
    # Build a serpentine 2D grid path (e.g. 3 columns wide)
    cols = 3
    for idx, name in enumerate(lines):
        row = idx // cols
        col = (idx % cols) if (row % 2 == 0) else (cols - 1 - (idx % cols))
        locations.append({
            "name": name.title(),
            "x": col * 2 + 1,
            "y": row * 2 + 1,
            "zone": "Custom Locus"
        })
    return locations

import re

def assign_concepts_to_palace(concepts: List[Dict[str, Any]],
                              palace_type: str = "house",
                              custom_places: str = "") -> List[Dict[str, Any]]:
    """
    Allocates ordered concepts into palace stations.
    Returns enriched concept list with location_name, x, y, and order_index.
    """
    templates = load_palace_templates()
    key = palace_type.lower()

    if key == "custom" and custom_places.strip():
        stations = parse_custom_locations(custom_places)
    elif key in templates:
        stations = templates[key]["locations"]
    else:
        # Fallback to house template
        stations = templates.get("house", {}).get("locations", [])

    if not stations:
        stations = [
            {"name": f"Station {i+1}", "x": (i % 3) * 2 + 1, "y": (i // 3) * 2 + 1, "zone": "Default"}
            for i in range(len(concepts))
        ]

    assigned = []
    for idx, c in enumerate(concepts):
        if idx < len(stations):
            st = stations[idx]
            loc_name = st["name"]
            x = st["x"]
            y = st["y"]
        else:
            # Overhang: extend route dynamically along upper zone
            ext_num = idx - len(stations) + 1
            loc_name = f"Upper Gallery Section {ext_num}"
            x = (idx % 4) * 2 + 1
            y = (len(stations) // 3 + ext_num) * 2 + 1

        entry = dict(c)
        entry["order_index"] = idx
        entry["location_name"] = loc_name
        entry["x"] = x
        entry["y"] = y
        assigned.append(entry)

    return assigned

def create_2d_route_figure(assigned_concepts: List[Dict[str, Any]],
                           title: str = "Palace Route Map",
                           active_step: Optional[int] = None,
                           reduced_motion: bool = False) -> go.Figure:
    """
    Builds a crisp, accessible 2D floorplan route visualization using Plotly.
    Adheres strictly to the LIGHT THEME:
    - Pure white background (#FFFFFF)
    - Soft grey gridlines
    - Primary indigo line (#5B6CFF) connecting stations with arrow direction
    - Numbered markers with emojis and location labels
    - Highlights active_step marker if provided
    """
    if not assigned_concepts:
        fig = go.Figure()
        fig.update_layout(
            paper_bgcolor="#FFFFFF",
            plot_bgcolor="#FFFFFF",
            annotations=[dict(text="No route concepts available", showarrow=False, font=dict(color="#6B7280", size=14))]
        )
        return fig

    xs = [c.get("x", idx + 1) for idx, c in enumerate(assigned_concepts)]
    ys = [c.get("y", idx + 1) for idx, c in enumerate(assigned_concepts)]
    labels = [f"<b>{idx+1}. {c.get('location_name', 'Station')}</b><br>{c.get('emoji', '📍')} {c.get('concept', '')}"
              for idx, c in enumerate(assigned_concepts)]
    hover_texts = [
        f"<b>Stop {idx+1}: {c.get('location_name')}</b><br>"
        f"<b>Concept:</b> {c.get('concept')}<br>"
        f"<b>Visual Mnemonic:</b> {c.get('visual_object')}<br>"
        f"<b>Difficulty:</b> {c.get('difficulty', 'Medium')}"
        for idx, c in enumerate(assigned_concepts)
    ]

    fig = go.Figure()

    # 1. Connecting path line (Primary Indigo #5B6CFF)
    fig.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="lines+markers",
        line=dict(color="#5B6CFF", width=3, dash="solid"),
        marker=dict(size=10, color="#C7D2FE", symbol="circle"),
        hoverinfo="skip",
        name="Route Path",
        showlegend=False
    ))

    # 2. Station Nodes (Teal Accent & White Badges)
    marker_colors = []
    marker_sizes = []
    for idx in range(len(assigned_concepts)):
        if active_step is not None and idx == active_step:
            marker_colors.append("#F59E0B") # Warm Amber highlight for active walker
            marker_sizes.append(28)
        else:
            marker_colors.append("#14B8A6") # Crisp Teal accent
            marker_sizes.append(22)

    fig.add_trace(go.Scatter(
        x=xs,
        y=ys,
        mode="markers+text",
        marker=dict(
            size=marker_sizes,
            color=marker_colors,
            line=dict(width=2, color="#FFFFFF"),
            symbol="circle"
        ),
        text=[f"{idx+1}" for idx in range(len(assigned_concepts))],
        textposition="middle center",
        textfont=dict(color="#FFFFFF", size=11, family="Inter, Arial, sans-serif"),
        hovertext=hover_texts,
        hoverinfo="text",
        name="Loci Stations",
        showlegend=False
    ))

    # 3. Location labels placed just above each station
    fig.add_trace(go.Scatter(
        x=xs,
        y=[y + 0.4 for y in ys],
        mode="text",
        text=[f"{c.get('emoji', '📍')} {c.get('location_name')}" for c in assigned_concepts],
        textposition="top center",
        textfont=dict(color="#1F2937", size=10, family="Inter, Arial, sans-serif"),
        hoverinfo="skip",
        showlegend=False
    ))

    # Layout styling forced to pure light mode
    min_x, max_x = min(xs) - 1, max(xs) + 1
    min_y, max_y = min(ys) - 1, max(ys) + 1.2

    fig.update_layout(
        title=dict(
            text=f"<b>{title}</b>",
            font=dict(color="#1F2937", size=15, family="Inter, sans-serif"),
            x=0.03
        ),
        paper_bgcolor="#FFFFFF",
        plot_bgcolor="#F8FAFC",
        xaxis=dict(
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            showticklabels=False,
            range=[min_x, max_x]
        ),
        yaxis=dict(
            showgrid=True,
            gridcolor="#E2E8F0",
            zeroline=False,
            showticklabels=False,
            range=[min_y, max_y]
        ),
        margin=dict(l=20, r=20, t=50, b=20),
        height=380,
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=12,
            font_color="#1F2937",
            bordercolor="#E5E7EB"
        )
    )

    return fig


def create_palace_mindmap_figure(palace_title: str, topic: str, concepts: List[Dict[str, Any]]) -> go.Figure:
    """
    Renders an interactive radial 2D Mind Map visualization of the memory palace.
    - Central Hub: Palace Topic & Name
    - Tier 1: Sequential Loci Stations
    - Tier 2: Visual Mnemonic Tokens
    - Tier 3: Anchored Academic Concepts
    Built on Plotly with pure light theme, clean hover metadata, and rounded branch curves.
    """
    fig = go.Figure()
    if not concepts:
        return fig

    N = len(concepts)
    hub_x, hub_y = 0.0, 0.0

    # Coordinate lists for scatter traces
    edge_x = []
    edge_y = []

    stn_x, stn_y, stn_text, stn_hover = [], [], [], []
    vis_x, vis_y, vis_text, vis_hover = [], [], [], []
    con_x, con_y, con_text, con_hover = [], [], [], []

    r_stn = 3.2
    r_vis = 5.2
    r_con = 7.2

    for idx, c in enumerate(concepts):
        theta = (2.0 * math.pi * idx / N) - (math.pi / 2.0)
        loc = c.get("location_name", f"Station {idx+1}")
        concept_name = c.get("concept") or c.get("concept_text", f"Concept {idx+1}")
        vis_obj = c.get("visual_object", "Token")
        emoji = c.get("emoji", "📍")
        reason = c.get("visual_reason", "")
        diff = c.get("difficulty", "Medium")

        # Station coordinates
        xs = r_stn * math.cos(theta)
        ys = r_stn * math.sin(theta)
        stn_x.append(xs)
        stn_y.append(ys)
        stn_text.append(f"#{idx+1} {loc}")
        stn_hover.append(f"<b>Stop #{idx+1}: {loc}</b><br>Station in memory route")

        # Edge: Hub -> Station
        edge_x.extend([hub_x, xs, None])
        edge_y.extend([hub_y, ys, None])

        # Visual Mnemonic coordinates (slightly offset angle for radial branching)
        theta_v = theta - (0.28 / (1 + idx % 2))
        xv = r_vis * math.cos(theta_v)
        yv = r_vis * math.sin(theta_v)
        vis_x.append(xv)
        vis_y.append(yv)
        vis_text.append(f"{emoji} {vis_obj}")
        vis_hover.append(f"<b>Mnemonic:</b> {emoji} {vis_obj}<br><b>Meaning:</b> {reason}")

        # Edge: Station -> Visual Mnemonic
        edge_x.extend([xs, xv, None])
        edge_y.extend([ys, yv, None])

        # Concept Anchor coordinates
        theta_c = theta + (0.28 / (1 + idx % 2))
        xc = r_con * math.cos(theta_c)
        yc = r_con * math.sin(theta_c)
        con_x.append(xc)
        con_y.append(yc)
        con_text.append(f"💡 {concept_name}")
        con_hover.append(f"<b>Target Concept:</b> {concept_name}<br><b>Difficulty:</b> {diff}<br><b>Anchor Locus:</b> {loc}")

        # Edge: Station -> Concept
        edge_x.extend([xs, xc, None])
        edge_y.extend([ys, yc, None])

    # 1. Connecting Branch Lines
    fig.add_trace(go.Scatter(
        x=edge_x, y=edge_y,
        mode="lines",
        line=dict(color="#CBD5E1", width=2),
        hoverinfo="none",
        showlegend=False
    ))

    # 2. Central Palace Hub
    clean_title = re.sub(r'(\s+Palace)+\s*$', '', palace_title, flags=re.IGNORECASE)
    fig.add_trace(go.Scatter(
        x=[hub_x], y=[hub_y],
        mode="markers+text",
        marker=dict(size=44, color="#5B6CFF", line=dict(color="#4856E0", width=3)),
        text=["🏰 Central Hub"],
        textposition="top center",
        textfont=dict(color="#1E1B4B", size=13, family="sans-serif"),
        hoverinfo="text",
        hovertext=[f"<b>{clean_title} Palace</b><br>Academic Discipline: {topic}<br>Total Loci: {N}"],
        name="Palace Core"
    ))

    # 3. Loci Stations (Tier 1)
    fig.add_trace(go.Scatter(
        x=stn_x, y=stn_y,
        mode="markers+text",
        marker=dict(size=24, color="#14B8A6", line=dict(color="#0D9488", width=2)),
        text=stn_text,
        textposition="middle right",
        textfont=dict(color="#0F766E", size=11, family="sans-serif"),
        hoverinfo="text",
        hovertext=stn_hover,
        name="Loci Stations"
    ))

    # 4. Visual Mnemonics (Tier 2)
    fig.add_trace(go.Scatter(
        x=vis_x, y=vis_y,
        mode="markers+text",
        marker=dict(size=20, color="#F59E0B", line=dict(color="#D97706", width=2)),
        text=vis_text,
        textposition="bottom center",
        textfont=dict(color="#B45309", size=10, family="sans-serif"),
        hoverinfo="text",
        hovertext=vis_hover,
        name="Visual Mnemonics"
    ))

    # 5. Academic Concepts (Tier 3)
    fig.add_trace(go.Scatter(
        x=con_x, y=con_y,
        mode="markers+text",
        marker=dict(size=20, color="#22C55E", line=dict(color="#16A34A", width=2)),
        text=con_text,
        textposition="top center",
        textfont=dict(color="#15803D", size=10, family="sans-serif"),
        hoverinfo="text",
        hovertext=con_hover,
        name="Academic Concepts"
    ))

    fig.update_layout(
        title=dict(
            text=f"🧠 <b>Cognitive Mind Map:</b> {clean_title} ({topic})",
            font=dict(family="sans-serif", size=16, color="#1F2937")
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-8.5, 8.5]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-8.5, 8.5]),
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        height=580,
        margin=dict(l=20, r=20, t=50, b=20),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=-0.08,
            xanchor="center",
            x=0.5,
            font=dict(size=11, color="#374151")
        ),
        hoverlabel=dict(
            bgcolor="#FFFFFF",
            font_size=12,
            font_family="sans-serif",
            font_color="#1F2937",
            bordercolor="#CBD5E1"
        )
    )

    return fig
    """
    Returns an accessible markdown text alternative describing each locus station in order.
    Ideal for screen readers and learners who prefer descriptive text over graphics.
    """
    lines = [
        "### 🏛️ Accessible Ordered Route Guide",
        "Walk through these locations sequentially from start to finish:\n"
    ]
    for idx, c in enumerate(assigned_concepts):
        loc = c.get("location_name", f"Station {idx+1}")
        concept = c.get("concept", "")
        obj = c.get("visual_object", "")
        reason = c.get("visual_reason", "")
        diff = c.get("difficulty", "Medium")
        emoji = c.get("emoji", "📍")

        lines.append(
            f"**Stop {idx+1}: {loc}**\n"
            f"- **Concept Anchor:** {concept} *(Difficulty: {diff})*\n"
            f"- **Visual Mnemonic ({emoji}):** {obj}\n"
            f"- **Associative Meaning:** {reason}\n"
        )

    return "\n".join(lines)


def format_palace_summary_text(palace: Dict[str, Any], concepts: List[Dict[str, Any]]) -> str:
    """
    Produces a beautifully structured, clean, non-repetitive plain text study summary sheet.
    No raw Markdown asterisks, cleanly aligned locus stations.
    """
    raw_title = palace.get("title", "Memory Palace")
    clean_title = re.sub(r'(\s+Palace)+\s*$', ' Palace', raw_title, flags=re.IGNORECASE)
    topic = palace.get("topic", "General")
    palace_type = palace.get("palace_type", "House")
    story_style = palace.get("story_style", "Normal")
    story_text = palace.get("story_text", "").strip()

    separator = "=" * 64
    sub_sep = "-" * 64

    lines = [
        separator,
        f"LOCILOOM STUDY SUMMARY SHEET: {clean_title.upper()}",
        f"Discipline: {topic} | Spatial Layout: {palace_type} | Narrative Style: {story_style}",
        separator,
        "",
        "I. VIVID NARRATIVE WALK (METHOD OF LOCI STORY)",
        sub_sep,
        story_text,
        "",
        "II. ORDERED LOCUS STATIONS & MNEMONIC ANCHORS",
        sub_sep,
    ]

    for idx, c in enumerate(concepts):
        loc = c.get("location_name", f"Station {idx+1}")
        concept = c.get("concept") or c.get("concept_text", f"Concept {idx+1}")
        obj = c.get("visual_object", "Token")
        reason = c.get("visual_reason", "")
        diff = c.get("difficulty", "Medium")
        emoji = c.get("emoji", "📍")

        lines.append(f"Station #{idx+1}: {loc}")
        lines.append(f"  * Target Concept : {concept} [Difficulty: {diff}]")
        lines.append(f"  * Visual Mnemonic: {emoji} {obj}")
        if reason:
            lines.append(f"  * Associative Link: {reason}")
        lines.append("")

    lines.extend([
        sub_sep,
        "III. COGNITIVE RETENTION PROTOCOL",
        "  1. Mental Walkthrough: Close your eyes and walk through stations 1 to N.",
        "  2. Active Retrieval  : Practice the LociLoom quiz to reinforce synaptic recall.",
        "  3. Spaced Repetition : Follow your personalized SM-2 Revision Planner schedule.",
        separator,
        "Generated with LociLoom - Adaptive Memory Palace Generator",
        separator
    ])

    return "\n".join(lines)


def get_text_route_summary(concepts: List[Dict[str, Any]]) -> str:
    """
    Returns an accessible, screen-reader friendly markdown table summary of the palace route stops.
    """
    if not concepts:
        return "*No concepts assigned to this route yet.*"
    lines = [
        "| Stop | Room / Location | Target Concept | Tangible Mnemonic Token |",
        "| :---: | :--- | :--- | :--- |"
    ]
    for idx, c in enumerate(concepts):
        loc = c.get("location_name", f"Station {idx+1}")
        c_text = c.get("concept_text", c.get("concept", "Concept"))
        obj = c.get("visual_object", "Mnemonic Object")
        lines.append(f"| **{idx+1}** | {loc} | **{c_text}** | {obj} |")
    return "\n".join(lines)


def render_infographic_storyboard_html(assigned_concepts: List[Dict[str, Any]], title: str = "Method of Loci") -> str:
    """
    Renders an illustrated, comic-strip style 2D Infographic Storyboard
    with sequential panels, location banners, scene visuals, connecting arrows,
    and bottom explanation cards (inspired by educational mnemonic infographics).
    """
    palette = [
        ("#EF4444", "#FEE2E2"),  # 1. Coral Red
        ("#3B82F6", "#DBEAFE"),  # 2. Cerulean Blue
        ("#10B981", "#D1FAE5"),  # 3. Emerald Green
        ("#8B5CF6", "#EDE9FE"),  # 4. Violet Purple
        ("#F59E0B", "#FEF3C7"),  # 5. Warm Amber
        ("#EC4899", "#FCE7F3"),  # 6. Deep Pink
        ("#6366F1", "#E0E7FF"),  # 7. Indigo
        ("#14B8A6", "#CCFBF1")   # 8. Crisp Teal
    ]

    panels_html = []
    total = len(assigned_concepts)

    for idx, c in enumerate(assigned_concepts):
        hdr_color, bg_tint = palette[idx % len(palette)]
        step_num = idx + 1
        loc = c.get("location_name", f"Station {step_num}")
        concept = c.get("concept", "")
        obj = c.get("visual_object", "")
        reason = c.get("visual_reason", "")
        emoji = c.get("emoji", "📍")
        sentence = c.get("supporting_sentence", "") or c.get("sentence", "")
        difficulty = c.get("difficulty", "Medium")

        next_arrow = ""
        if step_num < total:
            next_loc = assigned_concepts[idx + 1].get("location_name", f"Station {step_num + 1}")
            next_arrow = f"""
            <div style="margin-top: 10px; padding-top: 8px; border-top: 1px dashed #E2E8F0; text-align: right; font-size: 0.78rem; font-weight: 700; color: {hdr_color};">
                Walking to Stop {step_num + 1}: {next_loc} ➔
            </div>
            """

        panel = f"""
        <div style="background: #FFFFFF; border-radius: 14px; border: 2px solid #E2E8F0; box-shadow: 0 4px 12px rgba(0,0,0,0.05); overflow: hidden; display: flex; flex-direction: column; position: relative;">
            <div style="background: {hdr_color}; color: #FFFFFF; padding: 10px 14px; font-weight: 700; font-size: 0.92rem; display: flex; align-items: center; justify-content: space-between;">
                <span><span style="background: rgba(255,255,255,0.25); border-radius: 50%; width: 22px; height: 22px; display: inline-flex; align-items: center; justify-content: center; font-size: 0.82rem; margin-right: 6px;">{step_num}</span> {loc}</span>
                <span style="font-size: 0.75rem; background: rgba(0,0,0,0.15); padding: 2px 8px; border-radius: 12px;">{difficulty}</span>
            </div>
            
            <div style="background: {bg_tint}; padding: 16px 12px; text-align: center; border-bottom: 1px solid #E2E8F0;">
                <div style="font-size: 2.8rem; margin-bottom: 6px; line-height: 1;">{emoji}</div>
                <div style="font-weight: 800; color: #1E293B; font-size: 0.98rem; margin-bottom: 4px;">{concept}</div>
                <div style="font-size: 0.82rem; font-weight: 600; color: #475569; background: #FFFFFF; border-radius: 6px; padding: 4px 8px; display: inline-block; box-shadow: 0 1px 3px rgba(0,0,0,0.05);">
                    Anchor: <strong>{obj}</strong>
                </div>
                {f'<div style="font-size: 0.76rem; color: #64748B; margin-top: 6px; font-style: italic;">{reason}</div>' if reason else ''}
            </div>
            
            <div style="background: #FFFFFF; padding: 12px 14px; flex-grow: 1; font-size: 0.85rem; color: #334155; line-height: 1.55; display: flex; flex-direction: column; justify-content: space-between;">
                <div>{sentence if sentence else f'Recall <strong>{concept}</strong> placed at the {loc}.'}</div>
                {next_arrow}
            </div>
        </div>
        """
        panels_html.append(panel)

    all_panels = "\n".join(panels_html)

    html = f"""
    <div style="background: #F8FAFC; border: 1px solid #E2E8F0; border-radius: 18px; padding: 20px; margin: 15px 0;">
        <div style="text-align: center; margin-bottom: 20px;">
            <div style="display: inline-block; background: #5B6CFF; color: #FFFFFF; padding: 8px 24px; border-radius: 24px; font-weight: 800; font-size: 1.15rem; box-shadow: 0 4px 10px rgba(91,108,255,0.25);">
                🏛️ {title} — Method of Loci Storyboard
            </div>
            <div style="color: #64748B; font-size: 0.82rem; margin-top: 6px;">
                Walk from Panel 1 to Panel {total} in sequence. Each station anchors a key concept to a physical memory place.
            </div>
        </div>

        <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 18px;">
            {all_panels}
        </div>
    </div>
    """
    clean_lines = [line.strip() for line in html.splitlines() if line.strip()]
    return "\n".join(clean_lines)


def generate_infographic_image_bytes(assigned_concepts: List[Dict[str, Any]], title: str = "Method of Loci") -> bytes:
    """
    Draws a 2D composite infographic poster image (PNG) using Pillow.
    Creates a multi-panel visual memory palace sheet with title, colored headers,
    concept cards, and walking route arrows.
    """
    from PIL import Image, ImageDraw
    import io

    num_items = max(1, len(assigned_concepts))
    cols = 3 if num_items >= 3 else num_items
    rows = (num_items + cols - 1) // cols

    card_w = 360
    card_h = 240
    gap = 24
    pad_x = 40
    pad_y = 100

    img_w = pad_x * 2 + cols * card_w + (cols - 1) * gap
    img_h = pad_y + rows * card_h + (rows - 1) * gap + 50

    img = Image.new("RGB", (img_w, img_h), color="#F8FAFC")
    draw = ImageDraw.Draw(img)

    # Top Header Pill
    pill_w = min(img_w - 80, 600)
    pill_x0 = (img_w - pill_w) // 2
    draw.rounded_rectangle([pill_x0, 25, pill_x0 + pill_w, 75], radius=25, fill="#5B6CFF")
    header_text = f"{title[:35]} - Method of Loci"
    draw.text((pill_x0 + 30, 42), header_text, fill="#FFFFFF")

    palette = ["#EF4444", "#3B82F6", "#10B981", "#8B5CF6", "#F59E0B", "#EC4899", "#6366F1", "#14B8A6"]

    for idx, c in enumerate(assigned_concepts):
        r = idx // cols
        col = idx % cols
        x0 = pad_x + col * (card_w + gap)
        y0 = pad_y + r * (card_h + gap)
        x1 = x0 + card_w
        y1 = y0 + card_h

        hdr_color = palette[idx % len(palette)]
        loc = c.get("location_name", f"Station {idx+1}")
        concept = c.get("concept", "")
        obj = c.get("visual_object", "")
        sentence = c.get("supporting_sentence", "") or c.get("sentence", "")

        # Card base
        draw.rounded_rectangle([x0, y0, x1, y1], radius=14, fill="#FFFFFF", outline="#CBD5E1", width=2)
        # Header banner
        draw.rounded_rectangle([x0, y0, x1, y0 + 42], radius=14, fill=hdr_color)
        draw.rectangle([x0, y0 + 28, x1, y0 + 42], fill=hdr_color)

        draw.text((x0 + 14, y0 + 12), f"Stop {idx+1}: {loc[:24]}", fill="#FFFFFF")
        
        # Concept & Object text
        draw.text((x0 + 14, y0 + 56), f"Concept: {concept[:30]}", fill="#1E293B")
        draw.text((x0 + 14, y0 + 82), f"Anchor: {obj[:32]}", fill="#475569")
        
        # Note body text
        body = sentence[:120] if sentence else f"Placed at {loc}."
        words = body.split()
        lines = []
        cur_line = []
        for w in words:
            if len(" ".join(cur_line + [w])) <= 42:
                cur_line.append(w)
            else:
                lines.append(" ".join(cur_line))
                cur_line = [w]
        if cur_line:
            lines.append(" ".join(cur_line))

        for l_idx, line in enumerate(lines[:4]):
            draw.text((x0 + 14, y0 + 115 + l_idx * 20), line, fill="#334155")

        # Arrow indicator
        if idx < num_items - 1:
            draw.text((x1 - 100, y1 - 25), "Next Stop ->", fill=hdr_color)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

