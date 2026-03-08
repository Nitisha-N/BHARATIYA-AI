"""BharatiyaAI Mentor — My Profile"""

import streamlit as st
from utils.session import get_viva_readiness
from utils.auth import save_user_progress

BADGES = [
    ("Concept Master",  "🏆", "Master 10+ topics",       "mastered 10+ topics"),
    ("Practice Streak", "🔥", "5-day study streak",       "5 consecutive days of studying"),
    ("Viva Ready",      "🎯", "Score 20+/25 in viva",     "aced the Viva Examiner"),
    ("PYQ Analyst",     "📊", "Attempt 20+ PYQ questions","analyzed 20+ past year questions"),
    ("Top Performer",   "⭐", "85%+ overall accuracy",    "achieved 85%+ accuracy"),
]

XP_LEVELS = [
    (0,    "Beginner",    "#3A5A7A"),
    (100,  "Student",     "#5A7FA8"),
    (300,  "Learner",     "#FFD166"),
    (600,  "Practitioner","#6ECAEC"),
    (1000, "Scholar",     "#4AB7E0"),
    (2000, "Expert",      "#00E676"),
]


def _get_level(xp: int):
    level_name, level_color = "Beginner", "#3A5A7A"
    for threshold, name, color in XP_LEVELS:
        if xp >= threshold:
            level_name, level_color = name, color
    return level_name, level_color


def render_profile():
    name       = st.session_state.get("user_name", "Student")
    username   = st.session_state.get("username", "")
    uni        = st.session_state.get("university", "")
    subject    = st.session_state.get("subject", "")
    style_id   = st.session_state.get("learning_style", "guided")
    xp         = st.session_state.get("xp", 0)
    streak     = st.session_state.get("streak", 0)
    badges     = st.session_state.get("badges", [])
    tc         = st.session_state.get("topic_confidence", {})
    attempted  = st.session_state.get("questions_attempted", 0)
    correct    = st.session_state.get("correct_count", 0)
    viva_sess  = st.session_state.get("viva_sessions", 0)
    pyq_att    = st.session_state.get("pyq_attempted", 0)
    viva_ready = get_viva_readiness()

    accuracy = round(correct / attempted * 100) if attempted else 0
    level_name, level_color = _get_level(xp)

    # XP to next level
    next_xp = next((t for t, _, _ in XP_LEVELS if t > xp), None)
    xp_progress = 0
    prev_xp = 0
    for t, _, _ in XP_LEVELS:
        if xp >= t:
            prev_xp = t
    if next_xp:
        xp_progress = int((xp - prev_xp) / (next_xp - prev_xp) * 100)

    style_labels = {
        "guided": "🧭 Guided Discovery",
        "visual": "🎨 Visual & Analogy",
        "summary": "📋 Quick Summary",
        "flashcard": "🃏 Flashcard",
    }

    # ── PROFILE HERO ──
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(255,107,26,0.07),rgba(10,46,26,0));
border:1px solid rgba(255,107,26,0.15);border-radius:20px;padding:2rem;
margin-bottom:1.5rem;" class="animate-fade">
  <div style="display:flex;align-items:flex-start;gap:1.5rem;flex-wrap:wrap;">
    <div style="width:72px;height:72px;background:rgba(74,183,224,0.10);
    border:2px solid rgba(74,183,224,0.28);border-radius:50%;
    display:flex;align-items:center;justify-content:center;
    font-size:1.75rem;flex-shrink:0;">👤</div>
    <div style="flex:1;">
      <div style="font-family:'Space Grotesk',sans-serif;font-size:1.6rem;
      font-weight:700;margin-bottom:2px;">{name}</div>
      <div style="font-size:0.78rem;color:#3A5A7A;margin-bottom:6px;">
        @{username} · {uni}
      </div>
      <div style="font-size:0.8rem;color:#5A7FA8;">
        {subject} · {style_labels.get(style_id, style_id)}
      </div>
    </div>
    <div style="text-align:center;">
      <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
      color:#3A5A7A;margin-bottom:2px;">Level</div>
      <div style="font-size:1.25rem;font-weight:700;color:{level_color};">
        {level_name}</div>
      <div style="font-size:0.72rem;color:#3A5A7A;">{xp:,} XP</div>
    </div>
  </div>

  <div style="margin-top:1.25rem;">
    <div style="display:flex;justify-content:space-between;
    font-size:0.7rem;color:#3A5A7A;margin-bottom:4px;">
      <span>XP Progress</span>
      <span>{xp:,} / {next_xp:,} XP{' to next level' if next_xp else ''}</span>
    </div>
    <div style="height:6px;background:rgba(74,183,224,0.08);border-radius:3px;">
      <div style="width:{xp_progress}%;height:100%;
      background:linear-gradient(90deg,#4AB7E0,#FFD166);border-radius:3px;
      transition:width 0.5s;"></div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── STATS ──
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1:
        st.metric("🔥 Streak", f"{streak}d")
    with c2:
        st.metric("⚡ Total XP", f"{xp:,}")
    with c3:
        st.metric("🧠 Viva Ready", f"{viva_ready}%")
    with c4:
        st.metric("✏️ Accuracy", f"{accuracy}%" if attempted else "—")
    with c5:
        st.metric("📊 PYQ Done", pyq_att)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── BADGES ──
    st.markdown('<span class="sec-label">Achievement Badges</span>',
                unsafe_allow_html=True)

    badge_cols = st.columns(5)
    for col, (bname, icon, desc, how) in zip(badge_cols, BADGES):
        unlocked = bname in badges
        with col:
            opacity = "1" if unlocked else "0.3"
            glow = "filter:drop-shadow(0 0 10px rgba(255,107,26,0.5));" if unlocked else ""
            border = "1px solid rgba(74,183,224,0.28)" if unlocked else "1px solid rgba(74,183,224,0.08)"
            st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);{border};border-radius:16px;
padding:1.25rem 0.75rem;text-align:center;opacity:{opacity};">
  <div style="font-size:2rem;{glow}margin-bottom:6px;">{icon}</div>
  <div style="font-size:0.75rem;font-weight:600;margin-bottom:4px;">{bname}</div>
  <div style="font-size:0.65rem;color:#3A5A7A;line-height:1.4;">{desc}</div>
  {f'<div style="font-size:0.6rem;color:#4AB7E0;margin-top:6px;">✓ Unlocked</div>' if unlocked else f'<div style="font-size:0.6rem;color:#2A3A50;margin-top:6px;">{how}</div>'}
</div>
""", unsafe_allow_html=True)

    # ── STRENGTH vs WEAKNESS ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec-label">Strength & Weakness Map</span>',
                unsafe_allow_html=True)

    if tc:
        strong = [(t, d) for t, d in tc.items() if d.get("status") == "strong"]
        weak   = [(t, d) for t, d in tc.items() if d.get("status") == "weak"]
        learn  = [(t, d) for t, d in tc.items() if d.get("status") == "learning"]

        sw_cols = st.columns(2)
        with sw_cols[0]:
            st.markdown("""
<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
color:#00E676;margin-bottom:8px;">💪 Strong Topics</div>
""", unsafe_allow_html=True)
            if strong:
                for t, d in sorted(strong, key=lambda x: x[1].get("score", 0), reverse=True):
                    score = d.get("score", 0)
                    attempts = d.get("attempts", 0)
                    st.markdown(f"""
<div style="background:rgba(0,230,118,0.04);border:1px solid rgba(0,230,118,0.12);
border-radius:10px;padding:0.625rem 0.875rem;margin-bottom:6px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-size:0.82rem;">{t}</span>
    <span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;color:#00E676;">
      {int(score)}%</span>
  </div>
  <div style="height:3px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:6px;">
    <div style="width:{int(score)}%;height:100%;background:#00E676;border-radius:2px;"></div>
  </div>
  <div style="font-size:0.65rem;color:#2A3A50;margin-top:3px;">{attempts} attempts</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="font-size:0.8rem;color:#2A3A50;">Keep studying to build strengths!</div>',
                    unsafe_allow_html=True
                )

        with sw_cols[1]:
            st.markdown("""
<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
color:#FFD166;margin-bottom:8px;">⚑ Weak Topics — Needs Revision</div>
""", unsafe_allow_html=True)
            display_weak = weak + learn
            if display_weak:
                for t, d in sorted(display_weak, key=lambda x: x[1].get("score", 50)):
                    score = d.get("score", 50)
                    status = d.get("status", "learning")
                    color = "#FF4757" if status == "weak" else "#FFD166"
                    attempts = d.get("attempts", 0)
                    st.markdown(f"""
<div style="background:rgba(255,209,102,0.03);border:1px solid rgba(255,209,102,0.12);
border-radius:10px;padding:0.625rem 0.875rem;margin-bottom:6px;">
  <div style="display:flex;justify-content:space-between;align-items:center;">
    <span style="font-size:0.82rem;">{t}</span>
    <span style="font-family:JetBrains Mono,monospace;font-size:0.8rem;color:{color};">
      {int(score)}%</span>
  </div>
  <div style="height:3px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:6px;">
    <div style="width:{int(score)}%;height:100%;background:{color};border-radius:2px;"></div>
  </div>
  <div style="font-size:0.65rem;color:#2A3A50;margin-top:3px;">{attempts} attempts</div>
</div>
""", unsafe_allow_html=True)
            else:
                st.markdown(
                    '<div style="font-size:0.8rem;color:#2A3A50;">No weak areas detected yet!</div>',
                    unsafe_allow_html=True
                )
    else:
        st.markdown("""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.08);
border-radius:14px;padding:2rem;text-align:center;color:#2A3A50;font-size:0.875rem;">
  Start studying to see your strength & weakness map
</div>
""", unsafe_allow_html=True)

    # ── ACTIVITY SUMMARY ──
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec-label">Activity Summary</span>',
                unsafe_allow_html=True)

    act_cols = st.columns(4)
    stats = [
        ("📚", "Topics Studied", len(st.session_state.get("topics_studied", []))),
        ("✏️", "Questions Done", attempted),
        ("🧠", "Viva Sessions", viva_sess),
        ("🎯", "PYQ Attempted", pyq_att),
    ]
    for col, (icon, label, val) in zip(act_cols, stats):
        with col:
            st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.08);
border-radius:14px;padding:1.25rem;text-align:center;">
  <div style="font-size:1.5rem;margin-bottom:4px;">{icon}</div>
  <div style="font-family:JetBrains Mono,monospace;font-size:1.4rem;color:#6ECAEC;">
    {val}</div>
  <div style="font-size:0.7rem;color:#3A5A7A;margin-top:2px;">{label}</div>
</div>
""", unsafe_allow_html=True)

    # Save button
    st.markdown("<br>", unsafe_allow_html=True)
    if st.button("💾 Save Progress to Cloud", key="save_progress",
                 use_container_width=False):
        with st.spinner("Saving…"):
            save_user_progress()
        st.success("✓ Progress saved to DynamoDB!")
