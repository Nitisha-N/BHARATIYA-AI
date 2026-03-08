"""BharatiyaAI Mentor — Design System v5.2 (Fixed Overlay Bug)"""

import streamlit as st


def inject_css():
    st.markdown("""
<style>

@import url('https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500;600&display=swap');

:root {
  --navy:#0D173B;
  --navy-dark:#09102A;
  --slate:#1E293B;
  --blue:#4AB7E0;
  --blue-light:#6ECAEC;
  --coral:#FF6768;
  --green:#00E676;
  --gold:#FFD166;
  --white:#F0F6FF;
  --muted:#7A9CC0;
  --border:rgba(74,183,224,0.10);
  --border2:rgba(74,183,224,0.20);
}

/* BASE */

html, body, [class*="css"] {
  font-family:'Inter',sans-serif !important;
  background-color:var(--navy) !important;
  color:var(--white) !important;
}

#MainMenu, header, footer { visibility:hidden; }

.block-container {
  padding:1.5rem 2rem 3rem !important;
  max-width:1040px;
  position:relative;
  z-index:1;
}

/* APP BACKGROUND */

.stApp {
  background:
    linear-gradient(180deg, rgba(74,183,224,0.04) 0%, transparent 40%),
    radial-gradient(ellipse 70% 50% at 100% 0%, rgba(74,183,224,0.07) 0%, transparent 60%),
    radial-gradient(ellipse 50% 40% at 0% 100%, rgba(255,103,104,0.05) 0%, transparent 60%),
    #0D173B !important;
}

/* GRID OVERLAY — FIXED */

.stApp::before {
  content:'';
  position:fixed;
  inset:0;
  background-image: radial-gradient(rgba(74,183,224,0.08) 1px, transparent 1px);
  background-size:32px 32px;
  pointer-events:none;
  z-index:-1;
}

/* MAIN CONTENT FIX */

.main .block-container {
  position:relative;
  z-index:1;
}

/* SIDEBAR */

[data-testid="stSidebar"] {
  background:var(--slate) !important;
  border-right:1px solid var(--border) !important;
}

[data-testid="stSidebar"] .stButton > button {
  background:transparent !important;
  color:var(--muted) !important;
  border-radius:10px !important;
  border:1px solid transparent !important;
  padding:0.6rem 1rem !important;
  text-align:left !important;
  width:100% !important;
}

[data-testid="stSidebar"] .stButton > button:hover {
  background:rgba(74,183,224,0.10) !important;
  border-color:var(--border2) !important;
  color:var(--blue-light) !important;
}

/* MAIN BUTTONS */

.block-container .stButton > button {
  background:linear-gradient(135deg,var(--coral),#D94F50) !important;
  color:white !important;
  border:none !important;
  border-radius:10px !important;
  font-weight:600 !important;
  box-shadow:0 0 18px rgba(255,103,104,0.25) !important;
}

.block-container .stButton > button:hover {
  transform:translateY(-1px);
}

/* INPUTS */

.stTextInput input,
.stTextArea textarea {
  background:var(--slate) !important;
  border:1px solid var(--border2) !important;
  border-radius:10px !important;
  color:var(--white) !important;
}

/* METRICS */

[data-testid="stMetric"] {
  background:var(--slate) !important;
  border:1px solid var(--border) !important;
  border-radius:14px !important;
  padding:1rem 1.25rem !important;
}

[data-testid="stMetricValue"] {
  font-family:'JetBrains Mono',monospace !important;
  color:var(--blue-light) !important;
  font-size:1.75rem !important;
}

/* PROGRESS */

.stProgress > div > div > div {
  background:linear-gradient(90deg,var(--blue),var(--coral)) !important;
}

.stProgress > div > div {
  background:var(--slate) !important;
}

/* CARD HELPERS */

.baim-card {
  background:var(--slate);
  border:1px solid var(--border);
  border-radius:16px;
  padding:1.5rem;
  margin-bottom:1rem;
}

/* ANIMATIONS */

@keyframes pulse {
  0%,100% {opacity:1;}
  50% {opacity:0.5;}
}

.animate-pulse {
  animation:pulse 2s infinite;
}

</style>
""", unsafe_allow_html=True)
