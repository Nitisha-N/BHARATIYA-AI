"""BharatiyaAI × LearnOS — Full CSS Design System"""

import streamlit as st


def inject_css():
    st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700&family=Noto+Serif:ital,wght@0,400;0,600;1,400&family=JetBrains+Mono:wght@400;500&display=swap');

/* ── ROOT VARS ── */
:root {
  --saffron: #FF6B2B;
  --saffron-light: #FF8F5A;
  --saffron-dim: rgba(255,107,43,0.10);
  --saffron-glow: rgba(255,107,43,0.25);
  --green: #138808;
  --green-light: #1FAD0F;
  --green-dim: rgba(19,136,8,0.10);
  --navy: #060D1F;
  --navy2: #0A1630;
  --navy3: #0F1E3D;
  --card: #111C38;
  --card2: #162244;
  --border: rgba(255,255,255,0.07);
  --border2: rgba(255,255,255,0.13);
  --text: #E8EDF8;
  --muted: #6B7A99;
  --muted2: #8892BB;
  --gold: #F5C842;
  --gold-dim: rgba(245,200,66,0.10);
}

/* ── GLOBAL RESET ── */
html, body, [class*="css"] {
  font-family: 'Sora', sans-serif !important;
  background-color: var(--navy) !important;
  color: var(--text) !important;
}

/* ── HIDE STREAMLIT CHROME ── */
#MainMenu, header, footer { visibility: hidden; }
.block-container { padding: 1.5rem 2rem 2rem !important; max-width: 960px; }

/* ── HIDE AUTO-GENERATED PAGE NAV IN SIDEBAR ── */
[data-testid="stSidebarNav"],
[data-testid="stSidebarNavItems"],
section[data-testid="stSidebar"] ul,
section[data-testid="stSidebar"] nav {
  display: none !important;
}

/* ── BACKGROUND MESH ── */
.stApp {
  background:
    radial-gradient(ellipse 90% 50% at 80% -5%, rgba(255,107,43,0.06) 0%, transparent 55%),
    radial-gradient(ellipse 60% 50% at -5% 85%, rgba(19,136,8,0.04) 0%, transparent 55%),
    #060D1F !important;
}

/* ── SIDEBAR ── */
[data-testid="stSidebar"] {
  background: var(--navy2) !important;
  border-right: 1px solid var(--border) !important;
}
[data-testid="stSidebar"] > div:first-child { padding: 0 !important; }

/* ── SIDEBAR BUTTONS — override to look like nav items ── */
[data-testid="stSidebar"] .stButton > button {
  background: transparent !important;
  color: var(--muted2) !important;
  border: 1px solid transparent !important;
  border-radius: 8px !important;
  font-weight: 500 !important;
  font-size: 0.85rem !important;
  text-align: left !important;
  padding: 0.5rem 0.875rem !important;
  box-shadow: none !important;
  justify-content: flex-start !important;
  transition: all 0.15s !important;
}
[data-testid="stSidebar"] .stButton > button:hover {
  background: rgba(255,107,43,0.08) !important;
  border-color: rgba(255,107,43,0.15) !important;
  color: var(--saffron-light) !important;
  transform: none !important;
  box-shadow: none !important;
}

/* ── CARDS ── */
.bai-card {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1.5rem;
  margin-bottom: 1.25rem;
  transition: border-color 0.2s;
}
.bai-card:hover { border-color: var(--border2); }
.bai-card-saffron { border-left: 3px solid var(--saffron) !important; }
.bai-card-green { border-left: 3px solid var(--green-light) !important; }
.bai-card-gold { border-left: 3px solid var(--gold) !important; }

/* ── MAIN BUTTONS (non-sidebar) ── */
.block-container .stButton > button {
  background: var(--saffron) !important;
  color: white !important;
  border: none !important;
  border-radius: 10px !important;
  font-family: 'Sora', sans-serif !important;
  font-weight: 600 !important;
  transition: all 0.18s !important;
  box-shadow: 0 0 20px rgba(255,107,43,0.2) !important;
}
.block-container .stButton > button:hover {
  background: var(--saffron-light) !important;
  transform: translateY(-1px) !important;
  box-shadow: 0 4px 25px rgba(255,107,43,0.35) !important;
}
.block-container .stButton > button:disabled {
  opacity: 0.4 !important;
  transform: none !important;
}

/* ── INPUTS ── */
.stTextInput > div > div > input,
.stTextArea > div > div > textarea,
.stSelectbox > div > div > div {
  background: var(--card2) !important;
  border: 1px solid var(--border2) !important;
  border-radius: 10px !important;
  color: var(--text) !important;
  font-family: 'Sora', sans-serif !important;
}
.stTextInput > div > div > input:focus,
.stTextArea > div > div > textarea:focus {
  border-color: var(--saffron) !important;
  box-shadow: 0 0 0 2px var(--saffron-dim) !important;
}

/* ── FILE UPLOADER ── */
[data-testid="stFileUploader"] {
  background: var(--card) !important;
  border: 1.5px dashed var(--border2) !important;
  border-radius: 14px !important;
  transition: all 0.2s;
}
[data-testid="stFileUploader"]:hover {
  border-color: var(--saffron) !important;
  background: var(--saffron-dim) !important;
}

/* ── METRIC / STAT CARDS ── */
[data-testid="stMetric"] {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 12px !important;
  padding: 1rem !important;
}
[data-testid="stMetricValue"] {
  font-family: 'JetBrains Mono', monospace !important;
  color: var(--saffron) !important;
  font-size: 2rem !important;
}
[data-testid="stMetricLabel"] {
  font-size: 0.7rem !important;
  text-transform: uppercase !important;
  letter-spacing: 0.08em !important;
  color: var(--muted) !important;
}

/* ── PROGRESS BAR ── */
.stProgress > div > div > div {
  background: linear-gradient(90deg, var(--saffron), var(--gold)) !important;
  border-radius: 10px !important;
}
.stProgress > div > div {
  background: var(--card2) !important;
  border-radius: 10px !important;
  height: 6px !important;
}

/* ── TABS ── */
.stTabs [data-baseweb="tab-list"] {
  background: var(--card) !important;
  border-radius: 12px !important;
  padding: 4px !important;
  gap: 2px !important;
  border: 1px solid var(--border) !important;
}
.stTabs [data-baseweb="tab"] {
  background: transparent !important;
  color: var(--muted) !important;
  border-radius: 8px !important;
  font-family: 'Sora', sans-serif !important;
  font-size: 0.85rem !important;
  transition: all 0.18s !important;
}
.stTabs [aria-selected="true"] {
  background: var(--saffron) !important;
  color: white !important;
}

/* ── EXPANDER ── */
.streamlit-expanderHeader {
  background: var(--card) !important;
  border: 1px solid var(--border) !important;
  border-radius: 10px !important;
  font-family: 'Sora', sans-serif !important;
}

/* ── DIVIDER ── */
hr { border-color: var(--border) !important; margin: 1.25rem 0 !important; }

/* ── BADGES ── */
.bai-badge {
  display: inline-flex; align-items: center; gap: 4px;
  font-size: 0.7rem; font-weight: 700; letter-spacing: 0.08em;
  text-transform: uppercase; padding: 3px 10px; border-radius: 20px;
}
.badge-saffron { background: var(--saffron-dim); border: 1px solid var(--saffron-glow); color: var(--saffron-light); }
.badge-green { background: var(--green-dim); border: 1px solid rgba(19,136,8,0.25); color: var(--green-light); }
.badge-gold { background: var(--gold-dim); border: 1px solid rgba(245,200,66,0.25); color: var(--gold); }

/* ── FLASHCARD ── */
.fc-front {
  background: var(--card);
  border: 1.5px solid var(--border2);
  border-radius: 20px;
  padding: 2.5rem;
  text-align: center;
  min-height: 200px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}
.fc-back {
  background: rgba(255,107,43,0.04);
  border: 1.5px solid rgba(255,107,43,0.3);
  border-radius: 20px;
  padding: 2.5rem;
  text-align: center;
  min-height: 200px;
  display: flex; flex-direction: column;
  align-items: center; justify-content: center;
}

/* ── PRACTICE OPTIONS ── */
.opt-correct  { border-color: var(--green-light) !important; background: var(--green-dim) !important; color: var(--green-light) !important; }
.opt-wrong    { border-color: #F76F6F !important; background: rgba(247,111,111,0.08) !important; color: #F76F6F !important; }

/* ── MIND MAP ── */
.mindmap-svg-container {
  background: var(--card);
  border: 1px solid var(--border);
  border-radius: 16px;
  padding: 1rem;
  overflow: auto;
}

/* ── SECTION LABEL ── */
.sec-label {
  font-size: 0.68rem;
  text-transform: uppercase;
  letter-spacing: 0.12em;
  color: var(--muted);
  font-weight: 700;
  margin-bottom: 0.875rem;
  display: block;
}

/* ── GLOW HEADER ── */
.glow-title {
  font-family: 'Noto Serif', serif !important;
  font-size: 2rem !important;
  background: linear-gradient(135deg, #FF8F5A, #F5C842) !important;
  -webkit-background-clip: text !important;
  -webkit-text-fill-color: transparent !important;
  margin-bottom: 0.25rem !important;
}

.brand-name {
  font-family: 'Noto Serif', serif;
  background: linear-gradient(135deg, #FF6B2B, #F5C842);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  font-size: 1.3rem;
  font-weight: 600;
}

/* ── SCORE DISPLAY ── */
.big-score {
  font-family: 'JetBrains Mono', monospace;
  font-size: 4rem;
  color: var(--saffron);
  text-align: center;
  line-height: 1;
}

/* ── SPINNER ── */
.stSpinner > div { border-top-color: var(--saffron) !important; }

/* ── SELECTBOX ── */
.stSelectbox [data-baseweb="select"] > div {
  background: var(--card2) !important;
  border-color: var(--border2) !important;
}

/* ── ALERT ── */
.stAlert { border-radius: 12px !important; }

/* ── PULSE ANIMATION ── */
@keyframes pulse {
  0%, 100% { opacity: 1; }
  50% { opacity: 0.4; }
}
</style>
""", unsafe_allow_html=True)
