"""BharatiyaAI × LearnOS — Curriculum Page"""

import streamlit as st
from utils.session import set_tab


def render_curriculum():
    curriculum = st.session_state.get("curriculum", {})
    weeks = curriculum.get("weeks", [])
    subject = st.session_state.get("subject", "")
    active_week = st.session_state.get("active_week", 0)

    st.markdown(f"""
<div style="margin-bottom:1.5rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.8rem;font-weight:600;">🗓️ Your Curriculum</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">
    {subject} · {curriculum.get('total_weeks', len(weeks))}-week personalized roadmap
  </div>
</div>
""", unsafe_allow_html=True)

    if not weeks:
        st.info("No curriculum loaded.")
        return

    # Overall goal banner
    st.markdown(f"""
<div style="background:rgba(255,107,43,0.06);border:1px solid rgba(255,107,43,0.15);
border-radius:14px;padding:1.25rem;margin-bottom:1.5rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#FF6B2B;margin-bottom:0.5rem;">End Goal</div>
  <div style="font-size:0.9rem;line-height:1.6;">{curriculum.get('overall_goal','')}</div>
  <div style="font-size:0.78rem;color:#8892BB;margin-top:0.5rem;">✦ {curriculum.get('style_note','')}</div>
</div>
""", unsafe_allow_html=True)

    # Each week
    for idx, week in enumerate(weeks):
        is_active = idx == active_week
        border = "2px solid #FF6B2B" if is_active else "1px solid rgba(255,255,255,0.07)"
        bg = "rgba(255,107,43,0.05)" if is_active else "rgba(17,28,56,0.95)"

        topics_html = "".join(
            f'<span style="display:inline-flex;font-size:0.72rem;padding:2px 9px;border-radius:20px;margin:2px;'
            f'background:rgba(255,107,43,0.1);border:1px solid rgba(255,107,43,0.18);color:#FF8F5A;">{t}</span>'
            for t in week.get("topics", [])
        )

        prog = week.get("progress", 0)

        with st.container():
            st.markdown(f"""
<div style="background:{bg};border:{border};border-radius:16px;padding:1.5rem;margin-bottom:1rem;">
  <div style="display:flex;align-items:flex-start;justify-content:space-between;margin-bottom:0.875rem;">
    <div>
      <div style="display:inline-flex;font-size:0.6rem;font-weight:700;letter-spacing:0.08em;
      text-transform:uppercase;padding:2px 8px;border-radius:10px;margin-bottom:0.5rem;
      background:{"rgba(255,107,43,0.2)" if is_active else "rgba(107,122,153,0.2)"};
      color:{"#FF8F5A" if is_active else "#6B7A99"};">
        {"▶ Current Week" if is_active else f"Week {idx+1}"}
      </div>
      <div style="font-family:'Noto Serif',serif;font-size:1.1rem;font-weight:600;margin-bottom:0.25rem;">
        {week.get('name','')}
      </div>
      <div style="font-size:0.78rem;color:#8892BB;">{week.get('theme','')}</div>
    </div>
    <div style="text-align:right;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#FF6B2B;">{prog}%</div>
      <div style="font-size:0.65rem;color:#6B7A99;text-transform:uppercase;letter-spacing:0.08em;">progress</div>
    </div>
  </div>
  <div style="margin-bottom:0.875rem;">{topics_html}</div>
  <div style="background:rgba(255,107,43,0.06);border-radius:8px;padding:0.625rem 0.875rem;
  font-size:0.78rem;color:#8892BB;margin-bottom:0.875rem;">
    <span style="color:#FF6B2B;">🎯 Focus:</span> {week.get('focus','')}
  </div>
  <div style="background:rgba(245,200,66,0.06);border-radius:8px;padding:0.5rem 0.875rem;
  font-size:0.78rem;color:#8892BB;margin-bottom:1rem;">
    <span style="color:#F5C842;">💡 Tip:</span> {week.get('mode_tip','')}
  </div>
  <div style="height:5px;background:rgba(255,255,255,0.07);border-radius:3px;">
    <div style="width:{prog}%;height:100%;background:linear-gradient(90deg,#FF6B2B,#F5C842);border-radius:3px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

            c1, c2 = st.columns([2, 5])
            with c1:
                if st.button(
                    f"{'▶ Study Now' if is_active else f'Switch to Week {idx+1}'}",
                    key=f"curr_wk_{idx}",
                    use_container_width=True,
                ):
                    st.session_state.active_week = idx
                    st.session_state.last_explanation = None
                    st.session_state.last_flashcards = []
                    st.session_state.fc_cards = []
                    st.session_state.mindmap_data = None
                    st.session_state.practice_questions = []
                    st.session_state.practice_generated = False
                    st.session_state.insights_data = None
                    set_tab("learn")
                    st.rerun()
