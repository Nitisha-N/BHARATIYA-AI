"""BharatiyaAI Mentor — Account & Settings"""
import streamlit as st
from utils.session import set_tab, flag_weak

BADGE_INFO = {
    "Daily Smasher":        "🔥",
    "Concept Master":       "🏆",
    "Viva Ready":           "🎯",
    "Practice Streak":      "⚡",
    "Top Performer":        "⭐",
    "PYQ Analyst":          "📋",
    "Semester Champion":    "🎓",
}

def render_account():
    name       = st.session_state.get("user_name", "Student")
    username   = st.session_state.get("username", "")
    xp         = st.session_state.get("xp", 0)
    streak     = st.session_state.get("streak", 0)
    badges     = st.session_state.get("badges", [])
    subject    = st.session_state.get("subject", "")
    university = st.session_state.get("university", "")
    topics_studied = st.session_state.get("topics_studied", [])
    q_attempted = st.session_state.get("questions_attempted", 0)
    correct     = st.session_state.get("correct_count", 0)
    viva_sess   = st.session_state.get("viva_sessions", 0)
    accuracy    = int(correct / q_attempted * 100) if q_attempted else 0
    has_daily   = "Daily Smasher" in badges
    trophy      = "🏆" if has_daily else "👤"

    st.markdown(f"""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.20);
  border-radius:20px;padding:1.5rem 2rem;margin-bottom:1.25rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;flex-wrap:wrap;gap:1rem;">
    <div style="display:flex;align-items:center;gap:16px;">
      <div style="width:68px;height:68px;border-radius:50%;
        background:linear-gradient(135deg,#4AB7E0,#FFD166);
        display:flex;align-items:center;justify-content:center;
        font-size:1.8rem;box-shadow:0 0 20px rgba(74,183,224,0.3);">{trophy}</div>
      <div>
        <div style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;
          font-weight:700;color:#6ECAEC;">{name}</div>
        <div style="font-size:0.80rem;color:#7A9CC0;">@{username}</div>
        <div style="font-size:0.75rem;color:#3A5A80;margin-top:2px;">{university[:40] if university else 'No university set'}</div>
      </div>
    </div>
    <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;text-align:center;">
      <div style="background:#0D173B;border:1px solid rgba(74,183,224,0.15);border-radius:12px;padding:0.75rem 1rem;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#FFD166;">{xp:,}</div>
        <div style="font-size:0.62rem;text-transform:uppercase;color:#3A5A80;">Total XP</div>
      </div>
      <div style="background:#0D173B;border:1px solid rgba(74,183,224,0.15);border-radius:12px;padding:0.75rem 1rem;">
        <div style="font-family:'JetBrains Mono',monospace;font-size:1.4rem;font-weight:700;color:#FF6768;">{streak}</div>
        <div style="font-size:0.62rem;text-transform:uppercase;color:#3A5A80;">Day Streak</div>
      </div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

    col1, col2 = st.columns([1.3, 1])

    with col1:
        # SUBJECTS
        st.markdown('<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;color:#3A5A80;font-weight:700;margin-bottom:0.5rem;">📚 My Subjects</div>', unsafe_allow_html=True)
        all_subjects = st.session_state.get("all_subjects", [subject] if subject else [])
        for s in all_subjects:
            is_cur = (s == subject)
            st.markdown(f"""
<div style="background:#0D173B;border:1px solid {'rgba(74,183,224,0.25)' if is_cur else 'rgba(74,183,224,0.10)'};
  border-radius:12px;padding:0.75rem 1rem;margin-bottom:6px;
  display:flex;align-items:center;justify-content:space-between;">
  <div style="font-size:0.9rem;font-weight:600;color:{'#6ECAEC' if is_cur else '#7A9CC0'};">{s}</div>
  {'<span style="font-size:0.65rem;background:rgba(74,183,224,0.12);border:1px solid rgba(74,183,224,0.25);border-radius:20px;padding:1px 8px;color:#4AB7E0;">Active</span>' if is_cur else ''}
</div>
""", unsafe_allow_html=True)

        if st.button("➕ Add New Subject", key="acc_add", use_container_width=True):
            st.session_state.adding_subject = True
            set_tab("onboard_new")
            st.rerun()

        # ACHIEVEMENTS
        st.markdown('<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;color:#3A5A80;font-weight:700;margin:1rem 0 0.5rem;">🏆 Achievements</div>', unsafe_allow_html=True)
        all_badges = list(BADGE_INFO.keys())
        rows = [all_badges[i:i+3] for i in range(0, len(all_badges), 3)]
        for row in rows:
            cols = st.columns(len(row))
            for ci, badge in enumerate(row):
                earned = badge in badges
                icon = BADGE_INFO[badge]
                with cols[ci]:
                    st.markdown(f"""
<div style="background:{'rgba(74,183,224,0.10)' if earned else 'rgba(13,23,59,0.60)'};
  border:1px solid {'rgba(74,183,224,0.25)' if earned else 'rgba(74,183,224,0.06)'};
  border-radius:12px;padding:0.75rem 0.5rem;text-align:center;margin-bottom:6px;
  {'box-shadow:0 0 14px rgba(74,183,224,0.12);' if earned else 'opacity:0.45;'}">
  <div style="font-size:1.4rem;">{icon if earned else '🔒'}</div>
  <div style="font-size:0.62rem;font-weight:600;color:{'#6ECAEC' if earned else '#3A5A80'};margin-top:4px;line-height:1.3;">{badge}</div>
</div>
""", unsafe_allow_html=True)

        # DAYS STUDIED
        st.markdown('<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;color:#3A5A80;font-weight:700;margin:1rem 0 0.5rem;">📅 Study Intensity</div>', unsafe_allow_html=True)
        log = st.session_state.get("interaction_log", [])
        day_counts = {}
        for e in log:
            ts = e.get("timestamp", "")
            if ts:
                day_counts[ts[:5]] = day_counts.get(ts[:5], 0) + 1
        if day_counts:
            for day, count in list(day_counts.items())[-7:]:
                pct = min(100, count * 10)
                st.markdown(f"""
<div style="display:flex;align-items:center;gap:8px;margin-bottom:5px;">
  <span style="font-size:0.72rem;color:#6A90B8;width:40px;">{day}</span>
  <div style="flex:1;height:8px;background:rgba(255,255,255,0.04);border-radius:4px;">
    <div style="width:{pct}%;height:8px;border-radius:4px;
      background:linear-gradient(90deg,#4AB7E0,#FFD166);"></div>
  </div>
  <span style="font-family:'JetBrains Mono',monospace;font-size:0.68rem;color:#4AB7E0;width:20px;">{count}</span>
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown('<div style="font-size:0.78rem;color:#3A5A80;font-style:italic;">No sessions yet.</div>', unsafe_allow_html=True)

    with col2:
        # SPIDER CHART
        st.markdown('<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;color:#3A5A80;font-weight:700;margin-bottom:0.5rem;">🕸 Overall Progress</div>', unsafe_allow_html=True)
        try:
            import plotly.graph_objects as go
            tc = st.session_state.get("topic_confidence", {})
            if tc:
                items = list(tc.items())[:6]
                cats = [k[:14] for k, _ in items]
                vals = [float(v.get("score", 50)) for _, v in items]
            else:
                cats = ["Learn","Practice","Recall","Application","Exam","Viva"]
                vals = [0,0,0,0,0,0]
            cats_c = cats + [cats[0]]
            vals_c = vals + [vals[0]]
            fig = go.Figure()
            fig.add_trace(go.Scatterpolar(
                r=vals_c, theta=cats_c, fill="toself",
                fillcolor="rgba(74,183,224,0.10)",
                line=dict(color="#4AB7E0", width=2),
                marker=dict(color="#6ECAEC", size=6),
            ))
            fig.update_layout(
                polar=dict(
                    bgcolor="rgba(0,0,0,0)",
                    radialaxis=dict(visible=True,range=[0,100],
                        gridcolor="rgba(74,183,224,0.08)",
                        tickfont=dict(color="#3A5A80",size=9)),
                    angularaxis=dict(gridcolor="rgba(74,183,224,0.08)",
                        tickfont=dict(color="#6ECAEC",size=10)),
                ),
                paper_bgcolor="rgba(0,0,0,0)",
                plot_bgcolor="rgba(0,0,0,0)",
                showlegend=False,
                margin=dict(l=40,r=40,t=20,b=20),
                height=260,
            )
            st.plotly_chart(fig, use_container_width=True)
        except Exception:
            st.info("Study more to see your spider chart!")

        # STATS
        st.markdown(f"""
<div style="background:#0D173B;border:1px solid rgba(74,183,224,0.12);
  border-radius:14px;padding:1rem;margin-top:0.5rem;">
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;text-align:center;">
    <div style="padding:0.5rem;background:#1E293B;border-radius:10px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:#FFD166;">{q_attempted}</div>
      <div style="font-size:0.62rem;color:#3A5A80;">Questions</div>
    </div>
    <div style="padding:0.5rem;background:#1E293B;border-radius:10px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:#4AB7E0;">{accuracy}%</div>
      <div style="font-size:0.62rem;color:#3A5A80;">Accuracy</div>
    </div>
    <div style="padding:0.5rem;background:#1E293B;border-radius:10px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:#6ECAEC;">{viva_sess}</div>
      <div style="font-size:0.62rem;color:#3A5A80;">Viva Sessions</div>
    </div>
    <div style="padding:0.5rem;background:#1E293B;border-radius:10px;">
      <div style="font-family:'JetBrains Mono',monospace;font-size:1.2rem;font-weight:700;color:#00E676;">{len(topics_studied)}</div>
      <div style="font-size:0.62rem;color:#3A5A80;">Topics Done</div>
    </div>
  </div>
</div>
""", unsafe_allow_html=True)

        # POST EXAM SURVEY
        st.markdown('<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;color:#3A5A80;font-weight:700;margin:1rem 0 0.5rem;">📝 Post-Exam Survey</div>', unsafe_allow_html=True)
        with st.expander("How was your last exam?"):
            went_well = st.text_area("What went well?", key="survey_well", height=70)
            was_hard  = st.text_area("What was hard?", key="survey_hard", height=70)
            rating    = st.slider("Difficulty (1=Easy, 10=Hard)", 1, 10, 5, key="survey_diff")
            if st.button("Submit Survey", key="submit_survey", use_container_width=True):
                if was_hard:
                    for word in was_hard.split(","):
                        w = word.strip()
                        if w: flag_weak(w)
                st.success("✅ Submitted! We'll adjust your plan.")

        # NEW SEMESTER
        st.markdown('<div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.12em;color:#3A5A80;font-weight:700;margin:1rem 0 0.5rem;">🔄 New Semester?</div>', unsafe_allow_html=True)
        if st.button("Start New Semester Plan", key="new_sem", use_container_width=True):
            st.session_state.adding_subject = True
            set_tab("onboard_new")
            st.rerun()

        if st.button("🏠 Back to Dashboard", key="acc_home", use_container_width=True):
            set_tab("home")
            st.rerun()
