"""BharatiyaAI Mentor — Sidebar Navigation + GTA HUD"""

import math
import streamlit as st
from utils.session import set_tab, get_session_time, get_viva_readiness


def _chakra_svg(size=36):
    spokes = ""
    for i in range(24):
        angle = (i * 360 / 24) * math.pi / 180
        x1 = 50 + 14 * math.cos(angle)
        y1 = 50 + 14 * math.sin(angle)
        x2 = 50 + 43 * math.cos(angle)
        y2 = 50 + 43 * math.sin(angle)
        spokes += (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#4AB7E0" stroke-width="2" opacity="0.8"/>'
        )
    arrow = '<polygon points="50,8 54,20 50,16 46,20" fill="#4AB7E0"/>'
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100">'
        f'<circle cx="50" cy="50" r="44" fill="none" stroke="#4AB7E0" stroke-width="2.5"/>'
        f'<circle cx="50" cy="50" r="10" fill="none" stroke="#4AB7E0" stroke-width="2"/>'
        f'{spokes}{arrow}</svg>'
    )


NAV = [
    ("home",    "🏠", "Home"),
    ("level1",  "📚", "Level 1 — Learn"),
    ("level2",  "✏️",  "Level 2 — Practice"),
    ("level3",  "🎯", "Level 3 — Exam Prep"),
    ("viva",    "🧠", "Viva Examiner"),
    ("profile", "👤", "My Profile"),
]

BADGE_INFO = {
    "Concept Master": "🏆",
    "Practice Streak": "🔥",
    "Viva Ready": "🎯",
    "PYQ Analyst": "📊",
    "Top Performer": "⭐",
}


def render_sidebar():
    st.markdown("""
<style>
[data-testid="stSidebarNav"] { display: none !important; }
</style>
""", unsafe_allow_html=True)

    with st.sidebar:
        # ── LOGO ──
        st.markdown(f"""
<div style="padding:1.25rem 1rem 0.5rem;border-bottom:1px solid rgba(74,183,224,0.08);
margin-bottom:0.5rem;">
  <div style="display:flex;align-items:center;gap:10px;margin-bottom:6px;">
    {_chakra_svg(32)}
    <div>
      <div style="font-family:'Space Grotesk',sans-serif;font-size:0.95rem;font-weight:700;
      background:linear-gradient(135deg,#6ECAEC,#FFD166);
      -webkit-background-clip:text;-webkit-text-fill-color:transparent;line-height:1.2;">
        BharatiyaAI
      </div>
      <div style="font-size:0.65rem;color:#3A5A7A;letter-spacing:0.08em;text-transform:uppercase;">
        Mentor
      </div>
    </div>
  </div>
  <div style="font-size:0.68rem;color:#3A5A7A;font-style:italic;padding-left:2px;">
    Built by a student, for every student
  </div>
</div>
""", unsafe_allow_html=True)

        # ── GTA HUD ──
        xp = st.session_state.get("xp", 0)
        streak = st.session_state.get("streak", 0)
        viva_ready = get_viva_readiness()
        session_time = get_session_time()

        st.markdown(f"""
<div style="margin:0.75rem 0.75rem 0.5rem;background:rgba(9,16,42,0.97);
border:1px solid rgba(74,183,224,0.22);border-radius:12px;padding:0.75rem 0.875rem;">
  <div style="font-size:0.58rem;text-transform:uppercase;letter-spacing:0.12em;
  color:#4AB7E0;margin-bottom:0.5rem;font-weight:700;">⬡ Stats</div>
  <div style="display:grid;grid-template-columns:1fr 1fr;gap:4px;">
    <div style="font-size:0.72rem;color:#5A7FA8;">🔥 Streak</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;
    color:#6ECAEC;text-align:right;">{streak}d</div>
    <div style="font-size:0.72rem;color:#5A7FA8;">⚡ XP</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;
    color:#6ECAEC;text-align:right;">{xp:,}</div>
    <div style="font-size:0.72rem;color:#5A7FA8;">🧠 Viva</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;
    color:#6ECAEC;text-align:right;">{viva_ready}%</div>
    <div style="font-size:0.72rem;color:#5A7FA8;">⏱ Time</div>
    <div style="font-family:'JetBrains Mono',monospace;font-size:0.78rem;
    color:#6ECAEC;text-align:right;">{session_time}</div>
  </div>
</div>
""", unsafe_allow_html=True)

        # ── NAV ──
        st.markdown("""
<div style="padding:0 0.5rem;margin-bottom:0.25rem;">
  <div style="font-size:0.58rem;text-transform:uppercase;letter-spacing:0.12em;
  color:#2A3A50;font-weight:700;padding:0 0.5rem;margin-bottom:4px;">Navigation</div>
</div>
""", unsafe_allow_html=True)

        active = st.session_state.get("active_tab", "home")
        for tab_id, icon, label in NAV:
            is_active = active == tab_id
            if is_active:
                st.markdown(f"""
<div style="margin:2px 0.5rem;background:rgba(74,183,224,0.12);
border:1px solid rgba(74,183,224,0.22);border-radius:10px;
padding:0.5rem 1rem;display:flex;align-items:center;gap:8px;">
  <span style="font-size:0.9rem;">{icon}</span>
  <span style="font-size:0.85rem;font-weight:600;color:#6ECAEC;">{label}</span>
  <span style="margin-left:auto;width:6px;height:6px;background:#4AB7E0;
  border-radius:50%;animation:pulse 2s infinite;"></span>
</div>
""", unsafe_allow_html=True)
            else:
                if st.button(f"{icon}  {label}", key=f"nav_{tab_id}",
                             use_container_width=True):
                    set_tab(tab_id)
                    st.rerun()

        # ── BADGES ──
        badges = st.session_state.get("badges", [])
        if badges:
            st.markdown("""
<div style="padding:0 0.75rem;margin-top:0.75rem;margin-bottom:0.25rem;">
  <div style="font-size:0.58rem;text-transform:uppercase;letter-spacing:0.12em;
  color:#2A3A50;font-weight:700;">Badges</div>
</div>
""", unsafe_allow_html=True)
            badge_html = "".join(
                f'<span title="{b}" style="font-size:1.2rem;cursor:default;">{BADGE_INFO.get(b, "🏅")}</span>'
                for b in badges
            )
            st.markdown(
                f'<div style="padding:0 0.875rem;display:flex;gap:6px;flex-wrap:wrap;">{badge_html}</div>',
                unsafe_allow_html=True
            )

        # ── WEAK CONCEPTS ──
        weak = st.session_state.get("weak_concepts", [])
        if weak:
            st.markdown("""
<div style="padding:0 0.75rem;margin-top:0.875rem;">
  <div style="font-size:0.58rem;text-transform:uppercase;letter-spacing:0.12em;
  color:#2A3A50;font-weight:700;margin-bottom:6px;">⚑ Needs Revision</div>
""", unsafe_allow_html=True)
            chips = "".join(
                f'<div style="font-size:0.7rem;padding:2px 8px;border-radius:6px;margin-bottom:3px;'
                f'background:rgba(255,209,102,0.08);border:1px solid rgba(255,209,102,0.2);'
                f'color:#FFD166;">⚑ {w[:22]}</div>'
                for w in weak[:4]
            )
            st.markdown(f'<div>{chips}</div></div>', unsafe_allow_html=True)

        # ── LOGOUT ──
        st.markdown("<div style='height:1rem'></div>", unsafe_allow_html=True)
        if st.button("↩ Sign Out", key="nav_logout", use_container_width=True):
            from utils.auth import logout
            logout()
            st.rerun()

        # ── FOOTER ──
        st.markdown("""
<div style="padding:0.75rem;margin-top:0.5rem;border-top:1px solid rgba(74,183,224,0.06);">
  <div style="font-size:0.62rem;color:#2A3A50;text-align:center;">
    AI for Bharat Hackathon 2025<br>
    <span style="color:#4AB7E0;">Student Track</span>
  </div>
</div>
""", unsafe_allow_html=True)
