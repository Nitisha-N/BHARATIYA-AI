"""BharatiyaAI Mentor — Onboarding Wizard (Cyber theme, fixed HTML rendering)"""

import streamlit as st
from utils.ai import call_bedrock_json, CURRICULUM_SYSTEM
from utils.auth import save_onboarding_data
from utils.session import set_tab
from utils.pdf_reader import extract_text, upload_to_s3

UNIVERSITIES = [
    "Mumbai University",
    "Savitribai Phule Pune University (SPPU)",
    "Dr. Babasaheb Ambedkar Technological University (DBATU)",
    "Visvesvaraya Technological University (VTU)",
    "Gujarat Technological University (GTU)",
]

STYLES = {
    "guided":    ("🧭", "Guided Discovery",  "AI questions YOU. Socratic method. Cross-questioning. Best for deep understanding."),
    "visual":    ("🎨", "Visual & Analogy",   "Flowcharts, diagrams, mental models. Best for visual thinkers."),
    "summary":   ("📋", "Quick Summary",      "TL;DR + bullet points. Best for revision and time-pressed studying."),
    "flashcard": ("🃏", "Flashcard",          "7 Q&A cards per topic. Active recall. Spaced repetition built in."),
}

STEPS      = ["Learning Profile", "What to Learn", "Learning Style", "Exam Reality", "Your Plan"]
STEP_ICONS = ["🎓", "📚", "🧠", "📅", "✦"]


# ─────────────────────────────────────────────────────────────────────────────
#  STEP RAIL  — built as ONE string, rendered in ONE st.markdown call
# ─────────────────────────────────────────────────────────────────────────────
def _render_header(step: int):
    name = st.session_state.get("user_name", "Student")
    pct  = int(step / len(STEPS) * 100)

    # Build pill HTML for each step
    pills_html = ""
    for i, (s, icon) in enumerate(zip(STEPS, STEP_ICONS)):
        done   = i < step
        active = i == step

        if done:
            bg      = "rgba(0,230,118,0.10)"
            border  = "1px solid rgba(0,230,118,0.35)"
            dot_bg  = "#00E676"
            lbl_col = "#00E676"
            dot_icon = "✓"
        elif active:
            bg      = "rgba(74,183,224,0.12)"
            border  = "1.5px solid #4AB7E0"
            dot_bg  = "#4AB7E0"
            lbl_col = "#6ECAEC"
            dot_icon = icon
            # wrap in glow span
        else:
            bg      = "rgba(255,255,255,0.02)"
            border  = "1px solid rgba(74,183,224,0.10)"
            dot_bg  = "#243044"
            lbl_col = "#3A5A7A"
            dot_icon = icon

        glow = "box-shadow:0 0 12px rgba(74,183,224,0.4);" if active else ""

        pill = (
            f'<div style="display:inline-flex;align-items:center;gap:8px;'
            f'background:{bg};border:{border};border-radius:10px;'
            f'padding:6px 12px;white-space:nowrap;{glow}">'
            f'  <div style="width:20px;height:20px;border-radius:50%;background:{dot_bg};'
            f'    display:flex;align-items:center;justify-content:center;'
            f'    font-size:0.65rem;font-weight:700;color:white;flex-shrink:0;">'
            f'    {dot_icon}'
            f'  </div>'
            f'  <span style="font-size:0.72rem;font-weight:{"700" if active else "500"};'
            f'    color:{lbl_col};font-family:Inter,sans-serif;">{s}</span>'
            f'</div>'
        )

        # connector line between pills
        if i < len(STEPS) - 1:
            conn = "#00E676" if done else ("rgba(74,183,224,0.25)" if active else "rgba(74,183,224,0.08)")
            connector = (
                f'<div style="flex:1;height:2px;background:{conn};'
                f'min-width:12px;border-radius:1px;align-self:center;margin:0 4px;"></div>'
            )
        else:
            connector = ""

        pills_html += pill + connector

    st.markdown(f"""
<div class="animate-fade" style="margin-bottom:2.5rem;">

  <!-- Title row -->
  <div style="display:flex;align-items:flex-start;justify-content:space-between;
    flex-wrap:wrap;gap:1rem;margin-bottom:1.75rem;">
    <div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:2rem;font-weight:800;
        color:#F0F6FF;line-height:1.2;margin-bottom:4px;">
        Welcome, <span style="color:#4AB7E0;">{name}</span> ✦
      </div>
      <div style="font-size:0.875rem;color:#5A7FA8;">
        Let's build your personalized learning plan — Step {step + 1} of {len(STEPS)}
      </div>
    </div>
    <div style="text-align:right;min-width:120px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;
        color:#3A5A7A;letter-spacing:0.08em;margin-bottom:5px;">
        {step} / {len(STEPS)} COMPLETE
      </div>
      <div style="width:100%;height:4px;background:rgba(74,183,224,0.10);border-radius:4px;">
        <div style="width:{pct}%;height:100%;
          background:linear-gradient(90deg,#4AB7E0,#FF6768);border-radius:4px;
          transition:width 0.4s ease;"></div>
      </div>
    </div>
  </div>

  <!-- Step rail — all in one flex row -->
  <div style="display:flex;align-items:center;gap:0;overflow-x:auto;padding-bottom:4px;">
    {pills_html}
  </div>

</div>
""", unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
#  MAIN RENDER
# ─────────────────────────────────────────────────────────────────────────────
def render_onboarding(new_subject_mode=False):
    step = st.session_state.get("onboard_step", 0)
    _render_header(step)

    if step == 0:
        _step_profile()
    elif step == 1:
        _step_topics()
    elif step == 2:
        _step_style()
    elif step == 3:
        _step_exam()
    elif step == 4:
        _step_generate()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 0 — Learning Profile
# ─────────────────────────────────────────────────────────────────────────────
def _step_profile():
    st.markdown("""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.12);
  border-radius:18px;padding:1.75rem 1.75rem 1.25rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;font-weight:700;
    margin-bottom:4px;">🎓 Tell us about your studies</div>
  <div style="font-size:0.825rem;color:#5A7FA8;margin-bottom:1.25rem;">
    We'll tailor every response to your university's exam pattern.
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns(2)
    with col1:
        university = st.selectbox(
            "Your University",
            ["Select university…"] + UNIVERSITIES,
            key="ob_university",
        )
    with col2:
        subject = st.text_input(
            "Subject / Course",
            placeholder="e.g. Cloud Computing, DBMS, OS",
            key="ob_subject",
        )

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    _, col_btn = st.columns([3, 1])
    with col_btn:
        next_clicked = st.button("Next →", key="ob_next_0", use_container_width=True)

    if next_clicked:
        if university == "Select university…":
            st.error("Please select your university.")
        elif not subject.strip():
            st.error("Please enter your subject.")
        else:
            st.session_state.university = university
            st.session_state.subject    = subject.strip()
            st.session_state.onboard_step = 1
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 1 — What to Learn
# ─────────────────────────────────────────────────────────────────────────────
def _step_topics():
    subject = st.session_state.get("subject", "")
    uni     = st.session_state.get("university", "")

    st.markdown(f"""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.12);
  border-radius:18px;padding:1.75rem 1.75rem 1.25rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;font-weight:700;
    margin-bottom:4px;">📚 What do you want to learn?</div>
  <div style="font-size:0.825rem;color:#5A7FA8;">
    {subject} &nbsp;·&nbsp; {uni}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    topics = st.text_area(
        "Topics or concepts",
        placeholder=(
            "e.g. Virtualization, Cloud Service Models, Docker, Kubernetes…\n\n"
            "Separate by commas or new lines."
        ),
        height=120,
        key="ob_topics",
    )

    st.markdown("""
<div style="font-size:0.78rem;color:#5A7FA8;margin:0.75rem 0 0.5rem;">
  Or upload your syllabus / notes PDF
  <span style="color:#3A5A7A;">(optional)</span>
</div>
""", unsafe_allow_html=True)

    uploaded = st.file_uploader("Upload PDF or TXT", type=["pdf", "txt"], key="ob_upload")
    if uploaded:
        text = extract_text(uploaded)
        st.session_state.uploaded_filename = uploaded.name
        st.session_state.uploaded_text     = text
        st.success(f"✓ Loaded: {uploaded.name}")
        uploaded.seek(0)
        upload_to_s3(uploaded.read(), uploaded.name, folder="uploads")

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 4])
    with col_back:
        back = st.button("← Back", key="ob_back_1")
    with col_next:
        nxt = st.button("Next →", key="ob_next_1", use_container_width=True)

    if back:
        st.session_state.onboard_step = 0
        st.rerun()
    if nxt:
        if not topics.strip() and not st.session_state.get("uploaded_text"):
            st.error("Please enter topics or upload a file.")
        else:
            st.session_state.topics_text  = topics.strip()
            st.session_state.onboard_step = 2
            st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 2 — Learning Style
# ─────────────────────────────────────────────────────────────────────────────
def _step_style():
    st.markdown("""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.12);
  border-radius:18px;padding:1.75rem 1.75rem 0.5rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;font-weight:700;
    margin-bottom:4px;">🧠 How do you learn best?</div>
  <div style="font-size:0.825rem;color:#5A7FA8;margin-bottom:1.25rem;">
    This shapes every single response BharatiyaAI gives you.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    current = st.session_state.get("learning_style", "guided")

    for sid, (icon, label, desc) in STYLES.items():
        is_sel = current == sid
        border = "1.5px solid #4AB7E0" if is_sel else "1px solid rgba(74,183,224,0.10)"
        bg     = "rgba(74,183,224,0.08)" if is_sel else "rgba(30,41,59,0.6)"
        glow   = "box-shadow:0 0 16px rgba(74,183,224,0.25);" if is_sel else ""
        badge  = (
            '<span style="font-size:0.58rem;background:#4AB7E0;color:#0D173B;'
            'padding:2px 7px;border-radius:5px;margin-left:6px;font-weight:700;">'
            'ACTIVE</span>'
        ) if is_sel else ""

        st.markdown(f"""
<div style="background:{bg};border:{border};border-radius:12px;
  padding:0.875rem 1.125rem;margin-bottom:0.5rem;{glow}">
  <div style="display:flex;align-items:center;gap:8px;margin-bottom:3px;">
    <span style="font-size:1rem;">{icon}</span>
    <strong style="font-size:0.875rem;font-family:'Space Grotesk',sans-serif;">{label}</strong>
    {badge}
  </div>
  <div style="font-size:0.775rem;color:#5A7FA8;padding-left:1.75rem;">{desc}</div>
</div>
""", unsafe_allow_html=True)
        if st.button(f"Choose {label}", key=f"style_{sid}", use_container_width=True):
            st.session_state.learning_style = sid
            st.rerun()

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 4])
    with col_back:
        back = st.button("← Back", key="ob_back_2")
    with col_next:
        nxt = st.button("Next →", key="ob_next_2", use_container_width=True)

    if back:
        st.session_state.onboard_step = 1
        st.rerun()
    if nxt:
        st.session_state.onboard_step = 3
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 3 — Exam Reality
# ─────────────────────────────────────────────────────────────────────────────
def _step_exam():
    st.markdown("""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.12);
  border-radius:18px;padding:1.75rem 1.75rem 0.5rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.2rem;font-weight:700;
    margin-bottom:4px;">📅 Your Exam Reality</div>
  <div style="font-size:0.825rem;color:#5A7FA8;margin-bottom:1.25rem;">
    BharatiyaAI builds a realistic plan based on your actual time and goals.
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)

    has_exam = st.radio(
        "Do you have an upcoming exam?",
        ["Yes, I have an exam", "No, I'm learning for general knowledge"],
        key="ob_has_exam",
        horizontal=True,
    )

    if "Yes" in has_exam:
        col1, col2 = st.columns(2)
        with col1:
            exam_date = st.date_input("When is your exam?", key="ob_exam_date")
        with col2:
            target = st.selectbox(
                "Target score?",
                ["Just pass (40-50%)", "Good (55-65%)", "Distinction (70-80%)", "Full marks (85%+)"],
                key="ob_target",
            )
        hours = st.slider(
            "Hours you can study per day",
            min_value=1, max_value=10, value=3, step=1,
            key="ob_hours",
        )
        st.session_state.exam_date    = str(exam_date)
        st.session_state.target_score = target
        st.session_state.hours_per_day = hours
    else:
        st.session_state.exam_date     = "No exam"
        st.session_state.target_score  = "General learning"
        st.session_state.hours_per_day = 2

    st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)
    col_back, col_next = st.columns([1, 4])
    with col_back:
        back = st.button("← Back", key="ob_back_3")
    with col_next:
        nxt = st.button("Build My Plan →", key="ob_next_3", use_container_width=True)

    if back:
        st.session_state.onboard_step = 2
        st.rerun()
    if nxt:
        st.session_state.onboard_step = 4
        st.rerun()


# ─────────────────────────────────────────────────────────────────────────────
#  STEP 4 — Generate Plan
# ─────────────────────────────────────────────────────────────────────────────
def _step_generate():
    name      = st.session_state.get("user_name", "")
    uni       = st.session_state.get("university", "")
    subject   = st.session_state.get("subject", "")
    topics    = st.session_state.get("topics_text", "")
    style_id  = st.session_state.get("learning_style", "guided")
    style_lbl = STYLES.get(style_id, ("", "Unknown", ""))[1]
    target    = st.session_state.get("target_score", "")
    hours     = st.session_state.get("hours_per_day", 2)
    exam_dt   = st.session_state.get("exam_date", "")

    # Build the entire profile card as one HTML string — no split calls
    def _field(label, value, accent="#4AB7E0"):
        return (
            f'<div style="border-left:2px solid rgba({_hex_to_rgba(accent)},0.3);'
            f'padding-left:0.875rem;">'
            f'  <div style="font-size:0.58rem;color:#3A5A7A;text-transform:uppercase;'
            f'    letter-spacing:0.12em;margin-bottom:3px;">{label}</div>'
            f'  <div style="font-size:0.875rem;font-weight:600;color:{accent};">{value}</div>'
            f'</div>'
        )

    fields_html = (
        _field("Student",        name,       "#F0F6FF") +
        _field("University",     uni,        "#F0F6FF") +
        _field("Subject",        subject,    "#F0F6FF") +
        _field("Learning Style", style_lbl,  "#4AB7E0") +
        _field("Target Score",   target,     "#FF6768") +
        _field("Hours / Day",    f"{hours}h","#FF6768")
    )

    st.markdown(f"""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.15);
  border-radius:18px;padding:1.75rem;margin-bottom:1.5rem;">
  <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.15em;
    color:#4AB7E0;font-weight:700;margin-bottom:1.25rem;">
    ✦ Your Learning Profile
  </div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:1rem 1.5rem;">
    {fields_html}
  </div>
</div>
""", unsafe_allow_html=True)

    if not st.session_state.get("curriculum"):
        if st.button("✦ Generate My Curriculum", key="ob_generate",
                     use_container_width=True):
            with st.spinner("BharatiyaAI is designing your personalized curriculum…"):
                prompt = f"""
Student: {name}
University: {uni}
Subject: {subject}
Topics to cover: {topics}
Learning style: {style_lbl}
Target score: {target}
Hours per day: {hours}
Exam date: {exam_dt}
Uploaded material: {"Yes — " + st.session_state.get("uploaded_filename", "") if st.session_state.get("uploaded_filename") else "No"}

Design a realistic week-by-week curriculum for this student.
"""
                curriculum = call_bedrock_json(
                    CURRICULUM_SYSTEM, prompt,
                    use_sonnet=False, max_tokens=2000
                )
                if curriculum:
                    st.session_state.curriculum = curriculum
                    st.session_state.onboarded  = True
                    save_onboarding_data()
                    st.success("✓ Your personalized curriculum is ready!")
                    st.balloons()
                    import time; time.sleep(1.5)
                    set_tab("home")
                    st.rerun()
                else:
                    st.error("Could not generate curriculum. Check your AWS credentials in secrets.toml")
    else:
        st.success("✓ Curriculum already generated!")
        if st.button("Go to Dashboard →", key="ob_to_dash", use_container_width=True):
            st.session_state.onboarded = True
            set_tab("home")
            st.rerun()

    col_back, _ = st.columns([1, 4])
    with col_back:
        if st.button("← Back", key="ob_back_4"):
            st.session_state.onboard_step = 3
            st.session_state.curriculum   = None
            st.rerun()


def _hex_to_rgba(hex_color: str) -> str:
    """Convert #RRGGBB to 'R,G,B' for use inside rgba()."""
    h = hex_color.lstrip("#")
    if len(h) == 6:
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return f"{r},{g},{b}"
    return "255,255,255"
