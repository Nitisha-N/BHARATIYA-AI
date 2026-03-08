"""BharatiyaAI Mentor — Dashboard (Sidebar-Safe Version)"""
import streamlit as st
from utils.session import set_tab, get_session_time, get_viva_readiness

_LEVELS = [
    (0, "Beginner", "#7AAF94"),
    (200, "Student", "#8AAF94"),
    (500, "Learner", "#FFD166"),
    (1000, "Practitioner", "#6ECAEC"),
    (2000, "Scholar", "#4AB7E0"),
    (4000, "Expert", "#00E676"),
]

def _xp_level(xp):
    for i in range(len(_LEVELS) - 1, -1, -1):
        threshold, name, color = _LEVELS[i]
        if xp >= threshold:
            nxt = _LEVELS[i + 1][0] if i + 1 < len(_LEVELS) else None
            nxt_name = _LEVELS[i + 1][1] if i + 1 < len(_LEVELS) else "Max"
            within = xp - threshold
            span = (nxt - threshold) if nxt else 1
            return name, color, within, span, nxt_name
    return "Beginner", "#7AAF94", xp, 200, "Student"

def render_dashboard():
    name        = st.session_state.get("user_name", "Student")
    subject     = st.session_state.get("subject", "")
    xp          = st.session_state.get("xp", 0)
    streak      = st.session_state.get("streak", 0)
    topics_done = len(st.session_state.get("topics_studied", []))
    q_attempted = st.session_state.get("questions_attempted", 0)
    correct     = st.session_state.get("correct_count", 0)
    accuracy    = int(correct / q_attempted * 100) if q_attempted else 0
    viva        = get_viva_readiness()
    curriculum  = st.session_state.get("curriculum", None)

    level_name, level_color, xp_in, xp_span, next_level = _xp_level(xp)
    xp_pct = min(100, int(xp_in / xp_span * 100)) if xp_span else 100

    st.markdown(f"""
<div style="background:#1E293B;border-radius:20px;padding:1.5rem 2rem;
  border:1px solid rgba(74,183,224,0.2);margin-bottom:1.25rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.8rem;font-weight:700;
    color:#6ECAEC;">Namaste, {name} ✦</div>
  <div style="font-size:0.85rem;color:#7A9CC0;margin-bottom:1rem;">{subject or 'No subject set'}</div>
  <div style="display:grid;grid-template-columns:repeat(5,1fr);gap:8px;text-align:center;margin-bottom:1rem;">
    <div style="background:#0D173B;border-radius:10px;padding:0.75rem;">
      <div style="font-size:1.2rem;">📚</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#6ECAEC;">{topics_done}</div>
      <div style="font-size:0.62rem;color:#7A9CC0;">Topics</div>
    </div>
    <div style="background:#0D173B;border-radius:10px;padding:0.75rem;">
      <div style="font-size:1.2rem;">✏️</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#6ECAEC;">{q_attempted}</div>
      <div style="font-size:0.62rem;color:#7A9CC0;">Questions</div>
    </div>
    <div style="background:#0D173B;border-radius:10px;padding:0.75rem;">
      <div style="font-size:1.2rem;">🎯</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#6ECAEC;">{"—" if not q_attempted else f"{accuracy}%"}</div>
      <div style="font-size:0.62rem;color:#7A9CC0;">Accuracy</div>
    </div>
    <div style="background:#0D173B;border-radius:10px;padding:0.75rem;">
      <div style="font-size:1.2rem;">🧠</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#6ECAEC;">{viva}%</div>
      <div style="font-size:0.62rem;color:#7A9CC0;">Viva Ready</div>
    </div>
    <div style="background:#0D173B;border-radius:10px;padding:0.75rem;">
      <div style="font-size:1.2rem;">🔥</div>
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.1rem;color:#FFD166;">{streak}d</div>
      <div style="font-size:0.62rem;color:#7A9CC0;">Streak</div>
    </div>
  </div>
  <div style="display:flex;justify-content:space-between;font-size:0.7rem;color:#7A9CC0;margin-bottom:4px;">
    <span>Level: {level_name}</span>
    <span>{xp_in:,} / {xp_span:,} XP → {next_level}</span>
  </div>
  <div style="height:6px;background:#0D173B;border-radius:4px;">
    <div style="width:{xp_pct}%;height:6px;background:linear-gradient(90deg,#4AB7E0,#FFD166);border-radius:4px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Today's topic
    if curriculum and curriculum.get("weeks"):
        week = curriculum["weeks"][st.session_state.get("active_week", 0)]
        topics = week.get("topics", [])
        focus  = week.get("focus", "")
        st.markdown(f"""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.15);
  border-radius:16px;padding:1.25rem 1.5rem;margin-bottom:1rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
    color:#4AB7E0;font-weight:700;margin-bottom:0.5rem;">📅 What do you learn today?</div>
  <div style="font-size:1rem;font-weight:600;color:#F0F6FF;margin-bottom:0.5rem;">{focus or 'Continue your curriculum'}</div>
  <div style="display:flex;flex-wrap:wrap;gap:6px;">
    {"".join(f'<span style="background:rgba(74,183,224,0.10);border:1px solid rgba(74,183,224,0.18);border-radius:20px;padding:2px 10px;font-size:0.72rem;color:#6ECAEC;">{t}</span>' for t in topics[:4])}
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("### ⚡ Quick Access")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        if st.button("📖 Level 1 — Learn", use_container_width=True):
            set_tab("level1"); st.rerun()
    with c2:
        if st.button("✏️ Level 2 — Practice", use_container_width=True):
            set_tab("level2"); st.rerun()
    with c3:
        if st.button("🎯 Level 3 — Exam Prep", use_container_width=True):
            set_tab("level3"); st.rerun()
    with c4:
        if st.button("🧠 Viva Examiner", use_container_width=True):
            set_tab("viva"); st.rerun()
