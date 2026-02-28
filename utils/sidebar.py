"""BharatiyaAI × LearnOS — Sidebar Navigation"""

import streamlit as st
from utils.session import set_tab
import math

def make_chakra(size=32, color="#FF6B2B"):
    spokes = ""
    for i in range(24):
        angle = (i * 360 / 24) * math.pi / 180
        x1 = 50 + 14 * math.cos(angle)
        y1 = 50 + 14 * math.sin(angle)
        x2 = 50 + 43 * math.cos(angle)
        y2 = 50 + 43 * math.sin(angle)
        spokes += (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="{color}" stroke-width="1.8" opacity="0.7"/>'
        )
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">'
        f'<circle cx="50" cy="50" r="44" fill="none" stroke="{color}" stroke-width="3"/>'
        f'<circle cx="50" cy="50" r="12" fill="none" stroke="{color}" stroke-width="2"/>'
        f'{spokes}</svg>'
    )


NAV = [
    ("dashboard", "⬡", "Dashboard"),
    ("learn",     "⚡", "Learn & Doubts"),
    ("curriculum","🗓", "Curriculum"),
    ("flashcards","🃏", "Flashcards"),
    ("mindmap",   "🗺", "Mind Map"),
    ("practice",  "✏", "Practice Test"),
    ("insights",  "◈",  "Insights"),
]

STYLE_LABELS = {
    "stepbystep": "🪜 Step-by-Step",
    "flashcard":  "🃏 Flashcard",
    "summary":    "📋 Summary",
    "visual":     "🎨 Visual",
}


def render_sidebar():
    # ── HIDE STREAMLIT'S DEFAULT PAGE NAV + OTHER CHROME ──
    st.markdown("""
<style>
/* Hide the default Streamlit multipage nav entirely */
[data-testid="stSidebarNav"] { display: none !important; }
[data-testid="stSidebarNavItems"] { display: none !important; }
[data-testid="stSidebarNavSeparator"] { display: none !important; }
/* Hide deploy button */
.stDeployButton { display: none !important; }
/* Tighten sidebar padding */
[data-testid="stSidebar"] > div:first-child {
    padding-top: 0 !important;
    padding-left: 0 !important;
    padding-right: 0 !important;
}
/* Nav button overrides — make them look like menu items not generic buttons */
section[data-testid="stSidebar"] .stButton > button {
    background: transparent !important;
    border: 1px solid transparent !important;
    border-radius: 8px !important;
    color: #8892BB !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.5rem 0.75rem !important;
    box-shadow: none !important;
    transition: all 0.15s !important;
    margin-bottom: 2px !important;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background: rgba(255,107,43,0.08) !important;
    border-color: rgba(255,107,43,0.15) !important;
    color: #E8EDF8 !important;
    transform: none !important;
}
/* Reset button (bottom) */
section[data-testid="stSidebar"] .stButton > button[kind="secondary"] {
    color: #6B7A99 !important;
    font-size: 0.75rem !important;
}
</style>
""", unsafe_allow_html=True)

    with st.sidebar:
        # ── BRAND ──
        st.markdown(
            f'<div style="display:flex;align-items:center;gap:10px;'
            f'padding:1.25rem 1rem 0.75rem;border-bottom:1px solid rgba(255,255,255,0.06);">'
            f'{make_chakra(30)}'
            f'<div>'
            f'<div class="brand-name">BharatiyaAI</div>'
            f'<div style="font-size:0.58rem;color:#6B7A99;letter-spacing:0.12em;'
            f'text-transform:uppercase;margin-top:1px;">× LearnOS</div>'
            f'</div></div>',
            unsafe_allow_html=True
        )

        # ── STUDENT CHIP ──
        name = st.session_state.get("student_name", "Student")
        subj = st.session_state.get("subject", "")
        style = st.session_state.get("learning_style", "stepbystep")
        style_label = STYLE_LABELS.get(style, style)
        file_name = st.session_state.get("uploaded_filename", "")
        score = st.session_state.get("session_score")

        file_row = ""
        if file_name:
            short = file_name[:22] + ("…" if len(file_name) > 22 else "")
            file_row = (
                f'<div style="font-size:0.7rem;color:#6B7A99;margin-top:2px;">📄 {short}</div>'
            )
        score_row = ""
        if score is not None:
            score_row = (
                f'<div style="font-size:0.7rem;color:#FF6B2B;margin-top:2px;">'
                f'Score: {score}%</div>'
            )

        st.markdown(
            f'<div style="padding:0.875rem 1rem;border-bottom:1px solid rgba(255,255,255,0.06);">'
            f'<div style="font-size:0.6rem;color:#6B7A99;text-transform:uppercase;'
            f'letter-spacing:0.08em;margin-bottom:0.375rem;">Active Session</div>'
            f'<div style="display:flex;align-items:center;gap:6px;margin-bottom:3px;">'
            f'<div style="width:7px;height:7px;background:#FF6B2B;border-radius:50%;'
            f'flex-shrink:0;"></div>'
            f'<span style="font-size:0.82rem;font-weight:600;color:#E8EDF8;">{name}</span>'
            f'</div>'
            f'<div style="font-size:0.72rem;color:#8892BB;">📚 {subj}</div>'
            f'<div style="font-size:0.72rem;color:#8892BB;">{style_label}</div>'
            f'{file_row}{score_row}'
            f'</div>',
            unsafe_allow_html=True
        )

        # ── NAVIGATION ──
        st.markdown(
            '<div style="padding:0.625rem 0.75rem 0.25rem;">'
            '<div style="font-size:0.6rem;color:#6B7A99;text-transform:uppercase;'
            'letter-spacing:0.1em;margin-bottom:0.375rem;">Navigation</div>'
            '</div>',
            unsafe_allow_html=True
        )

        current = st.session_state.get("active_tab", "dashboard")
        for tab_id, icon, label in NAV:
            is_active = current == tab_id
            # Inject active styling via a wrapper div trick
            if is_active:
                st.markdown(
                    f'<div style="padding:0 0.5rem;">'
                    f'<div style="background:rgba(255,107,43,0.12);border:1px solid rgba(255,107,43,0.22);'
                    f'border-radius:8px;padding:0.5rem 0.75rem;font-size:0.82rem;font-weight:600;'
                    f'color:#FF8F5A;margin-bottom:2px;cursor:default;">'
                    f'{icon}  {label}</div></div>',
                    unsafe_allow_html=True
                )
                # Still need a hidden button to keep key space consistent — but active rows show as div
                # Add invisible button for click (it won't show due to CSS override but keeps logic)
            else:
                col_wrap = st.container()
                with col_wrap:
                    st.markdown('<div style="padding:0 0.5rem;">', unsafe_allow_html=True)
                    if st.button(f"{icon}  {label}", key=f"nav_{tab_id}",
                                 use_container_width=True):
                        set_tab(tab_id)
                        st.rerun()
                    st.markdown('</div>', unsafe_allow_html=True)

        # ── WEAK CONCEPTS ──
        weak = st.session_state.get("weak_concepts", [])
        st.markdown(
            '<div style="padding:0.875rem 1rem 0.5rem;border-top:1px solid rgba(255,255,255,0.06);'
            'margin-top:0.5rem;">'
            '<div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;'
            'color:#6B7A99;margin-bottom:0.5rem;">⚑ Weak Concepts</div>',
            unsafe_allow_html=True
        )
        if weak:
            chips = "".join(
                f'<span style="display:inline-flex;font-size:0.68rem;padding:2px 7px;'
                f'border-radius:4px;margin:2px;background:rgba(245,200,66,0.08);'
                f'border:1px solid rgba(245,200,66,0.18);color:#F5C842;">⚑ {c}</span>'
                for c in weak[:5]
            )
            st.markdown(chips, unsafe_allow_html=True)
        else:
            st.markdown(
                '<span style="font-size:0.75rem;color:#6B7A99;font-style:italic;">None flagged yet</span>',
                unsafe_allow_html=True
            )
        st.markdown('</div>', unsafe_allow_html=True)

        # ── REVISION QUEUE COUNT ──
        rq = st.session_state.get("revision_queue", [])
        if rq:
            st.markdown(
                f'<div style="padding:0 1rem 0.75rem;">'
                f'<div style="background:rgba(74,144,217,0.08);border:1px solid rgba(74,144,217,0.18);'
                f'border-radius:8px;padding:0.5rem 0.75rem;font-size:0.75rem;color:#4A90D9;">'
                f'🔄 {len(rq)} topic{"s" if len(rq) != 1 else ""} in revision queue'
                f'</div></div>',
                unsafe_allow_html=True
            )

        # ── RESET ──
        st.markdown('<div style="padding:0 0.75rem 1rem;margin-top:0.25rem;">',
                    unsafe_allow_html=True)
        if st.button("↩ New Session", use_container_width=True, key="reset_session"):
            for key in list(st.session_state.keys()):
                del st.session_state[key]
            st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

