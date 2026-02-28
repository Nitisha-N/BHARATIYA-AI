"""BharatiyaAI × LearnOS — Onboarding Wizard (4 steps)"""

import streamlit as st
from utils.session import init_session
from utils.ai import call_claude_json, CURRICULUM_SYSTEM
from utils.pdf_reader import extract_text, build_context_block
import math


def make_chakra_large(size=80):
    spokes = ""
    for i in range(24):
        angle = (i * 360 / 24) * math.pi / 180
        x1 = 50 + 14 * math.cos(angle)
        y1 = 50 + 14 * math.sin(angle)
        x2 = 50 + 43 * math.cos(angle)
        y2 = 50 + 43 * math.sin(angle)
        spokes += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#FF6B2B" stroke-width="1.8" opacity="0.6"/>'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="none" stroke="#FF6B2B" stroke-width="3"/><circle cx="50" cy="50" r="12" fill="none" stroke="#FF6B2B" stroke-width="2"/>{spokes}</svg>'


STYLE_OPTIONS = {
    "stepbystep": ("🪜", "Step-by-Step", "Numbered, structured explanations that build on each other"),
    "flashcard":  ("🃏", "Flashcard Mode", "Active recall cards for memory-based learning"),
    "summary":    ("📋", "Quick Summary", "Concise bullet-rich summaries for fast revision"),
    "visual":     ("🎨", "Visual & Analogy", "Mental images, diagrams and comparisons"),
}

EXAM_OPTIONS = {
    1: "1 Week Sprint",
    2: "2 Weeks",
    4: "4 Weeks",
    8: "8 Weeks",
    12: "12 Weeks (Semester)",
}


def render_onboarding():
    step = st.session_state.get("onboard_step", 0)

    # Hero header
    col_logo, col_title = st.columns([1, 5])
    with col_logo:
        st.markdown(make_chakra_large(60), unsafe_allow_html=True)
    with col_title:
        st.markdown(
            '<div style="padding-top:0.5rem;">'
            '<div style="font-family:\'Noto Serif\',serif;font-size:2.2rem;font-weight:600;'
            'background:linear-gradient(135deg,#FF6B2B,#F5C842);'
            '-webkit-background-clip:text;-webkit-text-fill-color:transparent;">BharatiyaAI × LearnOS</div>'
            '<div style="font-size:0.85rem;color:#6B7A99;margin-top:2px;">Personalized AI Learning — Built for Bharat</div>'
            '</div>',
            unsafe_allow_html=True
        )

    st.markdown("<br>", unsafe_allow_html=True)

    # Step indicator
    steps_labels = ["👤 You", "📚 Subject", "🧠 Style", "🗓️ Plan"]
    cols = st.columns(4)
    for i, (col, label) in enumerate(zip(cols, steps_labels)):
        with col:
            if i < step:
                color, bg = "#1FAD0F", "rgba(19,136,8,0.12)"
            elif i == step:
                color, bg = "#FF6B2B", "rgba(255,107,43,0.12)"
            else:
                color, bg = "#6B7A99", "rgba(255,255,255,0.04)"
            st.markdown(
                f'<div style="text-align:center;padding:0.625rem;border-radius:10px;'
                f'background:{bg};border:1.5px solid {color};'
                f'color:{color};font-size:0.8rem;font-weight:600;">'
                f'{"✓" if i < step else label}</div>',
                unsafe_allow_html=True
            )

    st.markdown("<br>", unsafe_allow_html=True)

    # ── STEP 0: Name ──
    if step == 0:
        st.markdown(
            '<div style="font-family:\'Noto Serif\',serif;font-size:1.75rem;">What\'s your name?</div>'
            '<div style="color:#6B7A99;font-size:0.9rem;margin-bottom:1.5rem;">Let\'s make this personal.</div>',
            unsafe_allow_html=True
        )
        name = st.text_input("", placeholder="Enter your first name…", key="input_name",
                             label_visibility="collapsed")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("Continue →", key="ob_step0", disabled=not name.strip()):
            st.session_state.student_name = name.strip()
            st.session_state.onboard_step = 1
            st.rerun()

    # ── STEP 1: Subject + Upload ──
    elif step == 1:
        st.markdown(
            f'<div style="font-family:\'Noto Serif\',serif;font-size:1.75rem;">Hi {st.session_state.student_name}! What are you studying?</div>'
            '<div style="color:#6B7A99;font-size:0.9rem;margin-bottom:1.5rem;">Tell us your subject and upload your study material.</div>',
            unsafe_allow_html=True
        )
        subj = st.text_input("Subject", placeholder="e.g. Biology, Thermodynamics, Indian History, Data Structures…",
                             key="input_subject")
        syllabus = st.text_area("Syllabus / Key Topics",
                                placeholder="Paste your syllabus, chapter list, or key topics here…\ne.g. Chapter 1: Cell Biology, Chapter 2: Mitosis & Meiosis…",
                                height=130, key="input_syllabus")
        uploaded = st.file_uploader("Upload study material (optional)", type=["pdf", "txt"], key="ob_upload")

        st.markdown("<br>", unsafe_allow_html=True)
        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← Back", key="ob_back1"):
                st.session_state.onboard_step = 0
                st.rerun()
        with col_next:
            if st.button("Continue →", key="ob_step1",
                         disabled=not (subj.strip() and syllabus.strip())):
                st.session_state.subject = subj.strip()
                st.session_state.syllabus_text = syllabus.strip()
                if uploaded:
                    st.session_state.uploaded_filename = uploaded.name
                    st.session_state.uploaded_text = extract_text(uploaded)
                st.session_state.onboard_step = 2
                st.rerun()

    # ── STEP 2: Learning Style ──
    elif step == 2:
        st.markdown(
            '<div style="font-family:\'Noto Serif\',serif;font-size:1.75rem;">How do you learn best?</div>'
            '<div style="color:#6B7A99;font-size:0.9rem;margin-bottom:1.5rem;">Your entire curriculum will be designed around this.</div>',
            unsafe_allow_html=True
        )

        selected_style = st.session_state.get("learning_style", "stepbystep")
        cols = st.columns(2)
        style_items = list(STYLE_OPTIONS.items())
        for idx, (style_id, (emoji, name, desc)) in enumerate(style_items):
            with cols[idx % 2]:
                is_sel = selected_style == style_id
                border = "2px solid #FF6B2B" if is_sel else "1.5px solid rgba(255,255,255,0.07)"
                bg = "rgba(255,107,43,0.10)" if is_sel else "rgba(17,28,56,1)"
                if st.button(
                    f"{emoji}  **{name}**\n{desc}",
                    key=f"style_{style_id}",
                    use_container_width=True,
                ):
                    st.session_state.learning_style = style_id
                    st.rerun()
                st.markdown(
                    f'<div style="margin-top:-0.5rem;margin-bottom:0.75rem;padding:0.875rem;'
                    f'border-radius:12px;border:{border};background:{bg};pointer-events:none;">'
                    f'<div style="font-size:1.4rem;margin-bottom:0.375rem;">{emoji}</div>'
                    f'<div style="font-weight:600;font-size:0.9rem;color:{"#FF8F5A" if is_sel else "#E8EDF8"};">{name}</div>'
                    f'<div style="font-size:0.75rem;color:#6B7A99;margin-top:2px;">{desc}</div>'
                    f'</div>',
                    unsafe_allow_html=True
                )

        st.markdown("<br>", unsafe_allow_html=True)
        col_back, col_next = st.columns([1, 3])
        with col_back:
            if st.button("← Back", key="ob_back2"):
                st.session_state.onboard_step = 1
                st.rerun()
        with col_next:
            if st.button("Continue →", key="ob_step2"):
                st.session_state.onboard_step = 3
                st.rerun()

    # ── STEP 3: Exam timeline + Generate ──
    elif step == 3:
        st.markdown(
            '<div style="font-family:\'Noto Serif\',serif;font-size:1.75rem;">When\'s your exam?</div>'
            '<div style="color:#6B7A99;font-size:0.9rem;margin-bottom:1.5rem;">We\'ll build a week-by-week roadmap just for you.</div>',
            unsafe_allow_html=True
        )

        exam_weeks = st.selectbox(
            "Time until exam",
            options=list(EXAM_OPTIONS.keys()),
            format_func=lambda x: EXAM_OPTIONS[x],
            index=2,
            key="input_exam_weeks",
        )

        # Summary card
        st.markdown(f"""
<div style="background:rgba(255,107,43,0.06);border:1px solid rgba(255,107,43,0.2);
border-radius:14px;padding:1.25rem;margin:1.25rem 0;">
  <div style="font-size:0.7rem;text-transform:uppercase;letter-spacing:0.1em;color:#FF6B2B;margin-bottom:0.75rem;">Your Learning Profile</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:0.75rem;font-size:0.875rem;">
    <div><span style="color:#6B7A99;">Student:</span> <strong>{st.session_state.student_name}</strong></div>
    <div><span style="color:#6B7A99;">Subject:</span> <strong>{st.session_state.subject}</strong></div>
    <div><span style="color:#6B7A99;">Style:</span> <strong>{STYLE_OPTIONS[st.session_state.learning_style][1]}</strong></div>
    <div><span style="color:#6B7A99;">Timeline:</span> <strong>{EXAM_OPTIONS[exam_weeks]}</strong></div>
  </div>
</div>
""", unsafe_allow_html=True)

        col_back, col_gen = st.columns([1, 3])
        with col_back:
            if st.button("← Back", key="ob_back3"):
                st.session_state.onboard_step = 2
                st.rerun()
        with col_gen:
            if st.button("✦ Build My Personalized Curriculum", key="ob_generate"):
                st.session_state.exam_weeks = exam_weeks
                _generate_curriculum()

    # Error display
    if st.session_state.get("onboard_error"):
        st.error(st.session_state.onboard_error)
        st.session_state.onboard_error = ""


def _generate_curriculum():
    with st.spinner("✦ BharatiyaAI is designing your personalized curriculum…"):
        weeks = st.session_state.exam_weeks
        style = st.session_state.learning_style
        style_name = STYLE_OPTIONS[style][1]

        user_msg = (
            f"Student: {st.session_state.student_name}\n"
            f"Subject: {st.session_state.subject}\n"
            f"Learning style: {style_name}\n"
            f"Weeks until exam: {weeks}\n"
            f"Syllabus/Topics:\n{st.session_state.syllabus_text}"
        )

        data = call_claude_json(CURRICULUM_SYSTEM, user_msg, max_tokens=1500)

        if data is None:
            st.session_state.onboard_error = (
                "Could not generate curriculum. Please check your API key in secrets.toml."
            )
            st.rerun()
            return

        st.session_state.curriculum = data
        st.session_state.active_week = 0
        st.session_state.onboarded = True
        st.session_state.active_tab = "dashboard"
        st.rerun()
