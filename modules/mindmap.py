"""BharatiyaAI × LearnOS — Mind Map Page"""

import streamlit as st
import math
from utils.ai import call_claude_json, MINDMAP_SYSTEM
from utils.pdf_reader import build_context_block


def _get_week_info():
    curriculum = st.session_state.get("curriculum", {})
    weeks = curriculum.get("weeks", [])
    idx = st.session_state.get("active_week", 0)
    if idx < len(weeks):
        w = weeks[idx]
        return w.get("name", ""), ", ".join(w.get("topics", []))
    return "", ""


def build_mindmap_svg(data: dict, width=820, height=520) -> str:
    """Build a full SVG mind map from Claude's JSON data."""
    if not data:
        return ""

    branches = data.get("branches", [])
    center = data.get("center", "Topic")
    cx, cy = width // 2, height // 2
    r = 175  # radius to branch nodes

    branch_colors = [
        b.get("color", "#FF6B2B") for b in branches
    ]

    svg_parts = [
        f'<svg width="{width}" height="{height}" viewBox="0 0 {width} {height}" '
        f'xmlns="http://www.w3.org/2000/svg" style="font-family:Sora,sans-serif;">',
        # Background
        f'<rect width="{width}" height="{height}" fill="#111C38" rx="16"/>',
        # Subtle grid
        '<pattern id="grid" width="40" height="40" patternUnits="userSpaceOnUse">',
        '<path d="M 40 0 L 0 0 0 40" fill="none" stroke="rgba(255,255,255,0.03)" stroke-width="1"/>',
        '</pattern>',
        f'<rect width="{width}" height="{height}" fill="url(#grid)" rx="16"/>',
    ]

    # Center glow
    svg_parts.append(
        f'<radialGradient id="cg" cx="50%" cy="50%" r="50%">'
        f'<stop offset="0%" stop-color="#FF6B2B" stop-opacity="0.2"/>'
        f'<stop offset="100%" stop-color="#FF6B2B" stop-opacity="0"/>'
        f'</radialGradient>'
        f'<circle cx="{cx}" cy="{cy}" r="90" fill="url(#cg)"/>'
    )

    # Branch lines (draw first, behind nodes)
    for i, branch in enumerate(branches):
        angle = (2 * math.pi * i / len(branches)) - math.pi / 2
        bx = cx + r * math.cos(angle)
        by = cy + r * math.sin(angle)
        color = branch_colors[i]

        # Curved path to branch
        ctrl_x = cx + (r / 2) * math.cos(angle)
        ctrl_y = cy + (r / 2) * math.sin(angle)
        svg_parts.append(
            f'<path d="M {cx} {cy} Q {ctrl_x:.0f} {ctrl_y:.0f} {bx:.0f} {by:.0f}" '
            f'fill="none" stroke="{color}" stroke-width="2" stroke-opacity="0.5"/>'
        )

        # Child lines
        children = branch.get("children", [])
        child_r = r + 100
        for j, child in enumerate(children[:3]):
            ca = angle + (j - 1) * 0.55
            child_x = cx + child_r * math.cos(ca)
            child_y = cy + child_r * math.sin(ca)
            # Clamp to SVG bounds
            child_x = max(80, min(width - 80, child_x))
            child_y = max(30, min(height - 30, child_y))
            svg_parts.append(
                f'<line x1="{bx:.0f}" y1="{by:.0f}" '
                f'x2="{child_x:.0f}" y2="{child_y:.0f}" '
                f'stroke="{color}" stroke-width="1.2" stroke-opacity="0.3" '
                f'stroke-dasharray="4,3"/>'
            )

    # Branch nodes + children labels
    for i, branch in enumerate(branches):
        angle = (2 * math.pi * i / len(branches)) - math.pi / 2
        bx = cx + r * math.cos(angle)
        by = cy + r * math.sin(angle)
        color = branch_colors[i]
        name = branch.get("name", "")[:18]

        # Branch ellipse
        svg_parts.append(
            f'<ellipse cx="{bx:.0f}" cy="{by:.0f}" rx="62" ry="26" '
            f'fill="{color}" fill-opacity="0.15" stroke="{color}" stroke-width="1.5"/>'
        )
        svg_parts.append(
            f'<text x="{bx:.0f}" y="{by + 5:.0f}" text-anchor="middle" '
            f'fill="{color}" font-size="11.5" font-weight="600">{name}</text>'
        )

        # Children
        children = branch.get("children", [])
        child_r = r + 100
        for j, child in enumerate(children[:3]):
            ca = angle + (j - 1) * 0.55
            child_x = cx + child_r * math.cos(ca)
            child_y = cy + child_r * math.sin(ca)
            child_x = max(80, min(width - 80, child_x))
            child_y = max(30, min(height - 30, child_y))
            child_text = str(child)[:20]

            svg_parts.append(
                f'<rect x="{child_x - 55:.0f}" y="{child_y - 13:.0f}" '
                f'width="110" height="26" rx="6" '
                f'fill="rgba(10,22,48,0.92)" stroke="{color}" stroke-width="0.8" stroke-opacity="0.4"/>'
            )
            svg_parts.append(
                f'<text x="{child_x:.0f}" y="{child_y + 5:.0f}" text-anchor="middle" '
                f'fill="#8892BB" font-size="9.5">{child_text}</text>'
            )

    # Center node (on top)
    center_short = center[:22]
    svg_parts.extend([
        f'<ellipse cx="{cx}" cy="{cy}" rx="80" ry="36" '
        f'fill="#0A1630" stroke="#FF6B2B" stroke-width="2.5"/>',
        f'<text x="{cx}" y="{cy + 5}" text-anchor="middle" '
        f'fill="#E8EDF8" font-size="13" font-weight="600">{center_short}</text>',
    ])

    svg_parts.append("</svg>")
    return "\n".join(svg_parts)


def render_mindmap():
    week_name, week_topics = _get_week_info()

    st.markdown(f"""
<div style="margin-bottom:1.5rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.8rem;font-weight:600;">🗺️ Mind Map</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">{week_name} · Visual Overview</div>
</div>
""", unsafe_allow_html=True)

    mindmap_data = st.session_state.get("mindmap_data")

    if not mindmap_data:
        st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:1.5rem;margin-bottom:1.25rem;">
  <div style="font-size:0.78rem;color:#8892BB;margin-bottom:0.875rem;">
    Generate a visual mind map for your current week's topics.
  </div>
  <div style="margin-bottom:1rem;">
""", unsafe_allow_html=True)

        chips_html = "".join(
            f'<span style="display:inline-flex;font-size:0.75rem;padding:3px 10px;border-radius:20px;margin:2px;'
            f'background:rgba(255,107,43,0.1);border:1px solid rgba(255,107,43,0.2);color:#FF8F5A;">{t}</span>'
            for t in week_topics.split(", ") if t
        )
        st.markdown(chips_html + "</div></div>", unsafe_allow_html=True)

        if st.button("🗺️ Generate Mind Map", key="mm_generate", use_container_width=True):
            context = build_context_block(
                st.session_state.get("uploaded_text", ""),
                week_topics or st.session_state.get("subject", "")
            )
            with st.spinner("Generating mind map…"):
                data = call_claude_json(MINDMAP_SYSTEM, context, max_tokens=800)
            if data:
                st.session_state.mindmap_data = data
                st.rerun()
            else:
                st.error("Could not generate mind map. Check your API key.")
        return

    # Render SVG
    svg = build_mindmap_svg(mindmap_data)
    st.markdown(
        f'<div class="mindmap-svg-container">{svg}</div>',
        unsafe_allow_html=True
    )

    # Branch legend
    st.markdown("<br>", unsafe_allow_html=True)
    branches = mindmap_data.get("branches", [])
    if branches:
        st.markdown('<span class="sec-label">Branches</span>', unsafe_allow_html=True)
        cols = st.columns(min(len(branches), 5))
        for col, branch in zip(cols, branches):
            with col:
                color = branch.get("color", "#FF6B2B")
                name = branch.get("name", "")
                children = branch.get("children", [])
                st.markdown(
                    f'<div style="background:rgba(17,28,56,0.9);border:1px solid rgba(255,255,255,0.07);'
                    f'border-top:3px solid {color};border-radius:10px;padding:0.875rem;">'
                    f'<div style="font-weight:600;font-size:0.85rem;color:{color};margin-bottom:0.375rem;">{name}</div>'
                    + "".join(
                        f'<div style="font-size:0.72rem;color:#6B7A99;margin-top:2px;">· {c}</div>'
                        for c in children[:3]
                    ) + "</div>",
                    unsafe_allow_html=True
                )

    c1, c2 = st.columns([1, 4])
    with c1:
        if st.button("🔄 Regenerate", key="mm_regen"):
            st.session_state.mindmap_data = None
            st.rerun()
