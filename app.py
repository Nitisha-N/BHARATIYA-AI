"""
BharatiyaAI × LearnOS
═══════════════════════════════════════════════════════
Personalized AI Learning Assistant for Indian Students
AI for Bharat Hackathon — Student Track
Team: BharatiyaAI | Lead: Nitisha Mandar Naigaonkar
═══════════════════════════════════════════════════════
"""

import streamlit as st
from streamlit_extras.colored_header import colored_header
import sys, os

sys.path.append(os.path.dirname(__file__))

from utils.session import init_session
from utils.styles import inject_css
from utils.sidebar import render_sidebar

# Page config — MUST be first Streamlit call
st.set_page_config(
    page_title="BharatiyaAI × LearnOS",
    page_icon="🔵",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Boot session state
init_session()

# Inject custom CSS (full design system)
inject_css()

# ── ONBOARDING GATE ──
if not st.session_state.get("onboarded"):
    from modules.onboarding import render_onboarding
    render_onboarding()
    st.stop()

# ── MAIN APP ──
render_sidebar()

tab = st.session_state.get("active_tab", "dashboard")

if tab == "dashboard":
    from modules.dashboard import render_dashboard
    render_dashboard()

elif tab == "learn":
    from modules.learn import render_learn
    render_learn()

elif tab == "curriculum":
    from modules.curriculum import render_curriculum
    render_curriculum()

elif tab == "flashcards":
    from modules.flashcards import render_flashcards
    render_flashcards()

elif tab == "mindmap":
    from modules.mindmap import render_mindmap
    render_mindmap()

elif tab == "practice":
    from modules.practice import render_practice
    render_practice()

elif tab == "insights":
    from modules.insights import render_insights
    render_insights()
