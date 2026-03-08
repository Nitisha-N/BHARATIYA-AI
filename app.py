"""
BharatiyaAI Mentor
India's first three-level adaptive AI mentor for Indian university students.
Built by a student, for every student.
Team Lead: Nitisha Mandar Naigaonkar
AI for Bharat Hackathon — Student Track
Powered by Amazon Nova (ap-south-1)
"""

import streamlit as st
import sys
import os

sys.path.append(os.path.dirname(__file__))

st.set_page_config(
    page_title="BharatiyaAI Mentor",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
)

from utils.session import init_session
from utils.styles import inject_css
from utils.auth import is_logged_in

init_session()
inject_css()


# ── AUTH GATE ──
if not is_logged_in():
    from modules.auth import render_auth
    render_auth()
    st.stop()


# ── ONBOARDING GATE ──
if not st.session_state.get("onboarded", False):
    from modules.onboarding import render_onboarding
    render_onboarding()
    st.stop()


# ── ADD SUBJECT FLOW ──
if st.session_state.get("active_tab") == "onboard_new":
    from modules.onboarding import render_onboarding
    render_onboarding(new_subject_mode=True)
    st.stop()


# ── MAIN APP (SIDEBAR ALWAYS HERE) ──
from utils.sidebar import render_sidebar
render_sidebar()


tab = st.session_state.get("active_tab", "home")


# ── ROUTING ──
if tab == "home":
    from modules.dashboard import render_dashboard
    render_dashboard()

elif tab == "level1":
    from modules.level1 import render_level1
    render_level1()

elif tab == "level2":
    from modules.level2 import render_level2
    render_level2()

elif tab == "level3":
    from modules.level3 import render_level3
    render_level3()

elif tab == "viva":
    from modules.viva import render_viva
    render_viva()

elif tab == "profile":
    from modules.account import render_account
    render_account()

elif tab == "account":
    from modules.account import render_account
    render_account()

else:
    from modules.dashboard import render_dashboard
    render_dashboard()
