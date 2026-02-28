"""BharatiyaAI × LearnOS — Dashboard"""

import streamlit as st
from utils.session import set_tab
import math


def make_chakra(size=24):
    spokes = ""
    for i in range(24):
        angle = (i * 360 / 24) * math.pi / 180
        x1 = 50 + 14 * math.cos(angle)
        y1 = 50 + 14 * math.sin(angle)
        x2 = 50 + 43 * math.cos(angle)
        y2 = 50 + 43 * math.sin(angle)
        spokes += f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" stroke="#FF6B2B" stroke-width="1.8" opacity="0.6"/>'
    return f'<svg width="{size}" height="{size}" viewBox="0 0 100 100"><circle cx="50" cy="50" r="44" fill="none" stroke="#FF6B2B" stroke-width="3"/><circle cx="50" cy="50" r="12" fill="none" stroke="#FF6B2B" stroke-width="2"/>{spokes}</svg>'


def render_dashboard():
    curriculum = st.session_state.get("curriculum", {})
    name = st.session_state.get("student_name", "Student")
    subject = st.session_state.get("subject", "")
    weeks_data = curriculum.get("weeks", [])
    total_weeks = curriculum.get("total_weeks", len(weeks_data))
    overall_goal = curriculum.get("overall_goal", "")
    style_note = curriculum.get("style_note", "")

    # ── HERO ──
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(255,107,43,0.08),rgba(10,22,48,0));
border:1px solid rgba(255,107,43,0.15);border-radius:20px;padding:2rem;margin-bottom:1.5rem;">
  <div style="display:flex;align-items:center;gap:12px;margin-bottom:1rem;">
    {make_chakra(36)}
    <div>
      <div style="font-family:'Noto Serif',serif;font-size:1.85rem;font-weight:600;
      background:linear-gradient(135deg,#FF8F5A,#F5C842);-webkit-background-clip:text;-webkit-text-fill-color:transparent;">
      Namaste, {name} ✦</div>
      <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">{subject} · {total_weeks}-week personalized plan</div>
    </div>
  </div>
  <div style="background:rgba(255,107,43,0.06);border-left:3px solid #FF6B2B;
  border-radius:0 10px 10px 0;padding:0.875rem 1rem;font-size:0.875rem;line-height:1.6;">
    <span style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;color:#FF6B2B;display:block;margin-bottom:4px;">Your Goal</span>
    {overall_goal}
  </div>
  <div style="margin-top:0.75rem;font-size:0.8rem;color:#8892BB;">
    <span style="color:#FF6B2B;">✦</span> {style_note}
  </div>
</div>
""", unsafe_allow_html=True)

    # ── QUICK STATS ──
    topics_done = len(st.session_state.get("topics_studied", []))
    q_attempted = st.session_state.get("questions_attempted", 0)
    score = st.session_state.get("session_score")
    weak_count = len(st.session_state.get("weak_concepts", []))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Topics Studied", topics_done)
    with c2:
        st.metric("Questions Done", q_attempted)
    with c3:
        st.metric("Session Score", f"{score}%" if score is not None else "—")
    with c4:
        st.metric("Weak Concepts", weak_count)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── WEEKLY ROADMAP ──
    st.markdown(
        f'<div class="sec-label">📅 Your {total_weeks}-Week Roadmap</div>',
        unsafe_allow_html=True
    )

    if not weeks_data:
        st.info("Curriculum not loaded. Please restart onboarding.")
        return

    active_week = st.session_state.get("active_week", 0)

    # Display weeks in rows of 3
    for row_start in range(0, len(weeks_data), 3):
        row_weeks = weeks_data[row_start:row_start+3]
        cols = st.columns(len(row_weeks))
        for col, (wk_offset, week) in zip(cols, enumerate(row_weeks)):
            wk_idx = row_start + wk_offset
            with col:
                is_active = wk_idx == active_week
                border = "2px solid #FF6B2B" if is_active else "1px solid rgba(255,255,255,0.07)"
                bg = "rgba(255,107,43,0.08)" if is_active else "rgba(17,28,56,0.95)"
                badge_bg = "#FF6B2B" if is_active else "rgba(107,122,153,0.3)"
                badge_col = "white" if is_active else "#8892BB"
                topics_preview = ", ".join(week.get("topics", [])[:2])
                if len(week.get("topics", [])) > 2:
                    topics_preview += "…"
                prog = week.get("progress", 0)

                st.markdown(f"""
<div style="background:{bg};border:{border};border-radius:14px;padding:1.125rem;
cursor:pointer;transition:all 0.2s;height:100%;">
  <div style="display:inline-flex;font-size:0.6rem;font-weight:700;letter-spacing:0.08em;
  text-transform:uppercase;padding:2px 8px;border-radius:10px;
  background:{badge_bg};color:{badge_col};margin-bottom:0.5rem;">
    {"▶ Current" if is_active else f"Week {wk_idx+1}"}
  </div>
  <div style="font-weight:600;font-size:0.9rem;margin-bottom:0.25rem;">{week.get('name','')}</div>
  <div style="font-size:0.72rem;color:#6B7A99;margin-bottom:0.625rem;">{topics_preview}</div>
  <div style="height:4px;background:rgba(255,255,255,0.07);border-radius:2px;">
    <div style="width:{prog}%;height:100%;background:linear-gradient(90deg,#FF6B2B,#F5C842);border-radius:2px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)
                if st.button(f"Study Week {wk_idx+1}", key=f"dash_wk_{wk_idx}", use_container_width=True):
                    st.session_state.active_week = wk_idx
                    # Reset week content
                    st.session_state.last_explanation = None
                    st.session_state.last_flashcards = []
                    st.session_state.fc_cards = []
                    st.session_state.mindmap_data = None
                    st.session_state.practice_questions = []
                    st.session_state.practice_generated = False
                    st.session_state.insights_data = None
                    set_tab("learn")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ADAPTIVE INTELLIGENCE PANEL ──
    priority = st.session_state.get("curriculum_priority", [])
    adaptation_triggered = st.session_state.get("adaptation_triggered", False)
    revision_queue = st.session_state.get("revision_queue", [])
    topic_confidence = st.session_state.get("topic_confidence", {})

    if adaptation_triggered or revision_queue or topic_confidence:
        st.markdown('<div class="sec-label">🔄 Adaptive Intelligence</div>', unsafe_allow_html=True)
        adapt_cols = st.columns([3, 2])

        with adapt_cols[0]:
            if adaptation_triggered and priority and weeks_data:
                st.markdown("""
<div style="background:rgba(74,144,217,0.06);border:1px solid rgba(74,144,217,0.18);
border-left:3px solid #4A90D9;border-radius:14px;padding:1.25rem;margin-bottom:1rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#4A90D9;margin-bottom:0.75rem;">🔄 Curriculum Reordered</div>
  <div style="font-size:0.8rem;color:#8892BB;margin-bottom:0.75rem;">
    Based on your performance, these weeks need attention first:
  </div>
""", unsafe_allow_html=True)
                for rank, wk_idx in enumerate(priority[:3]):
                    if wk_idx < len(weeks_data):
                        w = weeks_data[wk_idx]
                        weak_topics = st.session_state.get("weak_concepts", [])
                        overlaps = [t for t in w.get("topics", []) if t in weak_topics]
                        flag = "🔴" if overlaps else "🟡"
                        weak_badge = (
                            '<span style="font-size:0.68rem;color:#F5C842;margin-left:auto;">⚑ '
                            + str(len(overlaps)) + ' weak</span>'
                        ) if overlaps else ""
                        st.markdown(
                            f'<div style="display:flex;align-items:center;gap:8px;'
                            f'padding:6px 0;border-bottom:1px solid rgba(255,255,255,0.05);">'
                            f'<span style="font-size:0.75rem;color:#6B7A99;width:16px;">#{rank+1}</span>'
                            f'<span style="font-size:0.75rem;">{flag}</span>'
                            f'<span style="font-size:0.82rem;">{w.get("name","")}</span>'
                            f'{weak_badge}'
                            f'</div>',
                            unsafe_allow_html=True
                        )
                st.markdown("</div>", unsafe_allow_html=True)
            elif topic_confidence:
                # Show confidence scores even without full reorder
                st.markdown("""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:1.25rem;margin-bottom:1rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#6B7A99;margin-bottom:0.75rem;">Topic Confidence</div>
""", unsafe_allow_html=True)
                for topic_name, data in list(topic_confidence.items())[:4]:
                    score = data.get("score", 50)
                    status = data.get("status", "learning")
                    color = {"strong": "#1FAD0F", "weak": "#F5C842", "learning": "#FF6B2B"}.get(status, "#FF6B2B")
                    st.markdown(
                        f'<div style="margin-bottom:0.5rem;">'
                        f'<div style="display:flex;justify-content:space-between;font-size:0.78rem;margin-bottom:2px;">'
                        f'<span>{topic_name[:28]}</span>'
                        f'<span style="color:{color};font-family:JetBrains Mono,monospace;">{score}%</span></div>'
                        f'<div style="height:4px;background:rgba(255,255,255,0.07);border-radius:2px;">'
                        f'<div style="width:{score}%;height:100%;background:{color};border-radius:2px;"></div>'
                        f'</div></div>',
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

        with adapt_cols[1]:
            if revision_queue:
                st.markdown("""
<div style="background:rgba(245,200,66,0.05);border:1px solid rgba(245,200,66,0.15);
border-left:3px solid #F5C842;border-radius:14px;padding:1.25rem;margin-bottom:1rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#F5C842;margin-bottom:0.75rem;">⚑ Revision Queue</div>
""", unsafe_allow_html=True)
                for rev_t in revision_queue[:4]:
                    st.markdown(
                        f'<div style="font-size:0.8rem;padding:4px 0;'
                        f'border-bottom:1px solid rgba(255,255,255,0.05);">⚑ {rev_t}</div>',
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)
                if st.button("⚡ Start Revision Session", key="dash_revision",
                             use_container_width=True):
                    set_tab("learn")
                    st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    # ── QUICK ACCESS TILES ──
    st.markdown('<div class="sec-label">⚡ Quick Access</div>', unsafe_allow_html=True)
    qa_cols = st.columns(4)
    tiles = [
        ("⚡", "Learn", "learn", "Ask BharatiyaAI anything"),
        ("🃏", "Flashcards", "flashcards", "Active recall session"),
        ("✏️", "Practice Test", "practice", "Weekly assessment"),
        ("◈",  "Insights", "insights", "Your progress analysis"),
    ]
    for col, (icon, label, tab_id, desc) in zip(qa_cols, tiles):
        with col:
            st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:1.125rem;text-align:center;margin-bottom:0.5rem;">
  <div style="font-size:1.75rem;margin-bottom:0.5rem;">{icon}</div>
  <div style="font-weight:600;font-size:0.875rem;margin-bottom:2px;">{label}</div>
  <div style="font-size:0.72rem;color:#6B7A99;">{desc}</div>
</div>
""", unsafe_allow_html=True)
            if st.button(f"Open {label}", key=f"dash_quick_{tab_id}", use_container_width=True):
                set_tab(tab_id)
                st.rerun()
