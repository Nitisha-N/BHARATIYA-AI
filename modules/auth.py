"""BharatiyaAI Mentor — Login & Signup (Cyber theme)"""

import streamlit as st
import math
from utils.auth import login, signup


def _chakra(size=56):
    spokes = ""
    for i in range(24):
        angle = (i * 360 / 24) * math.pi / 180
        x1 = 50 + 14 * math.cos(angle)
        y1 = 50 + 14 * math.sin(angle)
        x2 = 50 + 43 * math.cos(angle)
        y2 = 50 + 43 * math.sin(angle)
        spokes += (
            f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
            f'stroke="#4AB7E0" stroke-width="2" opacity="0.7"/>'
        )
    arrow = '<polygon points="50,8 55,22 50,17 45,22" fill="#FF6768"/>'
    return (
        f'<svg width="{size}" height="{size}" viewBox="0 0 100 100">'
        f'<circle cx="50" cy="50" r="44" fill="none" stroke="#4AB7E0" stroke-width="2.5"/>'
        f'<circle cx="50" cy="50" r="10" fill="none" stroke="#4AB7E0" stroke-width="2"/>'
        f'{spokes}{arrow}</svg>'
    )


def render_auth():
    _, col, _ = st.columns([1, 1.8, 1])

    with col:
        # ── HERO ──
        st.markdown(f"""
<div class="animate-fade" style="text-align:center;padding:3rem 0 2rem;">
  <div style="display:flex;justify-content:center;margin-bottom:1.25rem;">
    <div class="animate-float">{_chakra(60)}</div>
  </div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:2.1rem;font-weight:800;
    background:linear-gradient(135deg,#4AB7E0,#6ECAEC);
    -webkit-background-clip:text;-webkit-text-fill-color:transparent;
    margin-bottom:6px;letter-spacing:-0.02em;">
    BharatiyaAI Mentor
  </div>
  <div style="font-size:0.875rem;color:#5A7FA8;margin-bottom:4px;">
    India's Adaptive AI Learning Mentor
  </div>
  <div style="font-size:0.78rem;color:#3A5A7A;font-style:italic;">
    Built by a student, for every student
  </div>
</div>
""", unsafe_allow_html=True)

        # ── AUTH CARD ──
        st.markdown("""
<div style="background:#1E293B;border:1px solid rgba(74,183,224,0.15);
  border-radius:20px;padding:0.25rem;margin-bottom:1rem;">
""", unsafe_allow_html=True)

        login_tab, signup_tab = st.tabs(["  Sign In  ", "  Create Account  "])

        with login_tab:
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            username = st.text_input(
                "Username",
                placeholder="your username",
                key="login_username",
            )
            password = st.text_input(
                "Password",
                type="password",
                placeholder="your password",
                key="login_password",
            )
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            if st.button("Sign In →", key="do_login", use_container_width=True):
                if username and password:
                    with st.spinner("Signing in…"):
                        success, msg = login(username, password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please enter username and password.")

            # ── GUEST MODE ──
            st.markdown("""
<div style="display:flex;align-items:center;gap:12px;margin:1rem 0 0.5rem;">
  <div style="flex:1;height:1px;background:rgba(74,183,224,0.10);"></div>
  <div style="font-size:0.7rem;color:#3A5A7A;white-space:nowrap;">or</div>
  <div style="flex:1;height:1px;background:rgba(74,183,224,0.10);"></div>
</div>
""", unsafe_allow_html=True)
            st.markdown("""
<div style="text-align:center;font-size:0.72rem;color:#3A5A7A;margin-bottom:0.5rem;">
  Hackathon judge? Skip auth ↓
</div>
""", unsafe_allow_html=True)

            if st.button("⚡ Continue as Guest", key="guest_login",
                         use_container_width=True):
                st.session_state.logged_in = True
                st.session_state.username = "guest"
                st.session_state.user_name = "Guest"
                st.session_state.xp = 0
                st.session_state.streak = 0
                st.session_state.badges = []
                st.rerun()

        with signup_tab:
            st.markdown("<div style='height:0.75rem'></div>", unsafe_allow_html=True)
            name = st.text_input(
                "Full Name",
                placeholder="Nitisha Naigaonkar",
                key="signup_name",
            )
            new_username = st.text_input(
                "Username",
                placeholder="choose a username",
                key="signup_username",
            )
            new_password = st.text_input(
                "Password",
                type="password",
                placeholder="min 6 characters",
                key="signup_password",
            )
            st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

            if st.button("Create Account →", key="do_signup",
                         use_container_width=True):
                if name and new_username and new_password:
                    with st.spinner("Creating your account…"):
                        success, msg = signup(name, new_username, new_password)
                    if success:
                        st.success(msg)
                        st.rerun()
                    else:
                        st.error(msg)
                else:
                    st.warning("Please fill all fields.")

        st.markdown("</div>", unsafe_allow_html=True)

        # ── FEATURE PILLS ──
        st.markdown("""
<div style="display:flex;justify-content:center;gap:8px;flex-wrap:wrap;margin-top:1.25rem;">
  <span style="font-size:0.68rem;padding:3px 10px;border-radius:20px;
    background:rgba(74,183,224,0.08);border:1px solid rgba(74,183,224,0.18);
    color:#5A7FA8;">🎓 3-Level Learning</span>
  <span style="font-size:0.68rem;padding:3px 10px;border-radius:20px;
    background:rgba(74,183,224,0.08);border:1px solid rgba(74,183,224,0.18);
    color:#5A7FA8;">🧠 AI Viva Examiner</span>
  <span style="font-size:0.68rem;padding:3px 10px;border-radius:20px;
    background:rgba(74,183,224,0.08);border:1px solid rgba(74,183,224,0.18);
    color:#5A7FA8;">📄 PYQ Bank</span>
  <span style="font-size:0.68rem;padding:3px 10px;border-radius:20px;
    background:rgba(74,183,224,0.08);border:1px solid rgba(74,183,224,0.18);
    color:#5A7FA8;">⚡ AWS Bedrock</span>
</div>
""", unsafe_allow_html=True)

        # ── FOOTER ──
        st.markdown("""
<div style="text-align:center;margin-top:1.75rem;padding-top:1rem;
  border-top:1px solid rgba(74,183,224,0.08);">
  <div style="font-size:0.68rem;color:#3A5A7A;">
    AI for Bharat Hackathon · Student Track · Powered by AWS Bedrock
  </div>
</div>
""", unsafe_allow_html=True)
