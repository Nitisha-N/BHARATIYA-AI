"""BharatiyaAI × LearnOS — Insights & Analytics Page"""

import streamlit as st
from utils.ai import call_claude_json, INSIGHTS_SYSTEM


def render_insights():
    st.markdown("""
<div style="margin-bottom:1.5rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.8rem;font-weight:600;">◈ Insights</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">Personalized analysis of your learning session</div>
</div>
""", unsafe_allow_html=True)

    # ── SESSION STATS ──
    name = st.session_state.get("student_name", "Student")
    topics = st.session_state.get("topics_studied", [])
    q_attempted = st.session_state.get("questions_attempted", 0)
    correct = st.session_state.get("correct_count", 0)
    weak = st.session_state.get("weak_concepts", [])
    strong = st.session_state.get("strong_concepts", [])
    score = st.session_state.get("session_score")
    fc_known = len(st.session_state.get("fc_known", []))
    fc_total = len(st.session_state.get("fc_cards", []))

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        st.metric("Topics Studied", len(topics))
    with c2:
        st.metric("Flashcards Known", f"{fc_known}/{fc_total}" if fc_total else "—")
    with c3:
        st.metric("Questions Done", q_attempted)
    with c4:
        st.metric("Session Score", f"{score}%" if score is not None else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # ── AI INSIGHTS ──
    insights = st.session_state.get("insights_data")

    if not insights:
        needs_data = len(topics) == 0 and q_attempted == 0 and fc_total == 0

        if needs_data:
            st.markdown("""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:2rem;text-align:center;">
  <div style="font-size:1.5rem;margin-bottom:0.5rem;">📊</div>
  <div style="font-weight:600;margin-bottom:0.5rem;">No session data yet</div>
  <div style="color:#6B7A99;font-size:0.875rem;">
    Study some topics, do flashcards, or take a practice test first.
  </div>
</div>
""", unsafe_allow_html=True)
            return

        if st.button("◈ Generate My Insights", key="gen_insights", use_container_width=True):
            wrong_count = q_attempted - correct
            user_msg = (
                f"Student: {name}\n"
                f"Subject: {st.session_state.get('subject','')}\n"
                f"Week: {st.session_state.get('active_week', 0) + 1}\n"
                f"Learning style: {st.session_state.get('learning_style','')}\n"
                f"Topics studied: {', '.join(topics)}\n"
                f"Weak concepts: {', '.join(weak)}\n"
                f"Strong concepts: {', '.join(strong)}\n"
                f"Questions attempted: {q_attempted}, Correct: {correct}, Wrong: {wrong_count}\n"
                f"Flashcards known: {fc_known} / {fc_total}"
            )
            with st.spinner("BharatiyaAI is analysing your session…"):
                data = call_claude_json(INSIGHTS_SYSTEM, user_msg, max_tokens=900)
            if data:
                st.session_state.insights_data = data
                st.rerun()
            else:
                st.error("Could not generate insights. Check your API key.")
        return

    # ── DISPLAY INSIGHTS ──

    # Headline
    headline = insights.get("headline", "")
    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(255,107,43,0.08),rgba(10,22,48,0));
border:1px solid rgba(255,107,43,0.15);border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.1rem;line-height:1.5;">{headline}</div>
</div>
""", unsafe_allow_html=True)

    # Recommendation
    rec = insights.get("recommendation", "")
    st.markdown(f"""
<div style="background:rgba(255,107,43,0.05);border:1px solid rgba(255,107,43,0.12);
border-left:3px solid #FF6B2B;border-radius:14px;padding:1.25rem;margin-bottom:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#FF6B2B;margin-bottom:0.5rem;">
    ✦ Personalized Recommendation
  </div>
  <div style="font-size:0.875rem;line-height:1.7;">{rec}</div>
</div>
""", unsafe_allow_html=True)

    # Next Action
    next_action = insights.get("next_action", "")
    if next_action:
        st.markdown(f"""
<div style="background:rgba(245,200,66,0.06);border:1px solid rgba(245,200,66,0.15);
border-radius:10px;padding:0.875rem 1rem;margin-bottom:1.25rem;">
  <span style="color:#F5C842;font-weight:600;">▶ Next Action: </span>
  <span style="font-size:0.875rem;">{next_action}</span>
</div>
""", unsafe_allow_html=True)

    # Strengths + Improvements
    col1, col2 = st.columns(2)
    with col1:
        strengths = insights.get("strengths", [])
        st.markdown("""
<div style="background:rgba(19,136,8,0.05);border:1px solid rgba(19,136,8,0.15);
border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#1FAD0F;margin-bottom:0.75rem;">✓ Strengths</div>
""", unsafe_allow_html=True)
        for s in strengths:
            st.markdown(
                f'<div style="display:flex;gap:6px;align-items:flex-start;font-size:0.82rem;'
                f'color:#E8EDF8;margin-bottom:0.375rem;line-height:1.5;">'
                f'<div style="width:5px;height:5px;background:#1FAD0F;border-radius:50%;flex-shrink:0;margin-top:6px;"></div>'
                f'{s}</div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    with col2:
        improvements = insights.get("improvements", [])
        st.markdown("""
<div style="background:rgba(245,200,66,0.05);border:1px solid rgba(245,200,66,0.15);
border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#F5C842;margin-bottom:0.75rem;">⚑ Areas to Improve</div>
""", unsafe_allow_html=True)
        for imp in improvements:
            st.markdown(
                f'<div style="display:flex;gap:6px;align-items:flex-start;font-size:0.82rem;'
                f'color:#E8EDF8;margin-bottom:0.375rem;line-height:1.5;">'
                f'<div style="width:5px;height:5px;background:#F5C842;border-radius:50%;flex-shrink:0;margin-top:6px;"></div>'
                f'{imp}</div>',
                unsafe_allow_html=True
            )
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Topic Mastery Progress Bars
    topic_mastery = insights.get("topic_mastery", [])
    if topic_mastery:
        st.markdown('<span class="sec-label">Topic Mastery</span>', unsafe_allow_html=True)
        for tm in topic_mastery:
            topic_name = tm.get("name", "")
            topic_score = tm.get("score", 0)
            status = tm.get("status", "learning")
            color = {"strong": "#1FAD0F", "weak": "#F5C842", "learning": "#FF6B2B"}.get(status, "#FF6B2B")
            label_color = color
            st.markdown(f"""
<div style="margin-bottom:0.875rem;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:0.375rem;">
    <span style="font-size:0.85rem;">{topic_name}</span>
    <div style="display:flex;align-items:center;gap:8px;">
      <span style="font-size:0.68rem;padding:1px 7px;border-radius:10px;
      background:{color}22;color:{label_color};border:1px solid {color}44;">{status}</span>
      <span style="font-family:'JetBrains Mono',monospace;font-size:0.8rem;color:#6B7A99;">{topic_score}%</span>
    </div>
  </div>
  <div style="height:6px;background:rgba(255,255,255,0.07);border-radius:3px;">
    <div style="width:{topic_score}%;height:100%;
    background:linear-gradient(90deg,{color},{color}88);border-radius:3px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # ── ADAPTIVE LOOP SUMMARY ──
    interaction_log = st.session_state.get("interaction_log", [])
    topic_confidence = st.session_state.get("topic_confidence", {})

    if interaction_log or topic_confidence:
        st.markdown('<span class="sec-label">🔄 Adaptive Learning Loop</span>',
                    unsafe_allow_html=True)
        loop_cols = st.columns([2, 3])

        with loop_cols[0]:
            st.markdown("""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#6B7A99;margin-bottom:0.875rem;">Recent Interactions</div>
""", unsafe_allow_html=True)
            if interaction_log:
                type_icons = {"practice": "✏️", "flashcard": "🃏",
                              "doubt": "💬", "explain": "⚡"}
                for entry in interaction_log[-6:]:
                    icon = type_icons.get(entry.get("type", ""), "·")
                    correct = entry.get("correct")
                    result = ""
                    if correct is True:
                        result = '<span style="color:#1FAD0F;">✓</span>'
                    elif correct is False:
                        result = '<span style="color:#F5C842;">✗</span>'
                    st.markdown(
                        f'<div style="display:flex;align-items:center;gap:6px;padding:4px 0;'
                        f'border-bottom:1px solid rgba(255,255,255,0.04);font-size:0.78rem;">'
                        f'<span>{icon}</span>'
                        f'<span style="color:#8892BB;flex:1;">{entry.get("topic","")[:22]}</span>'
                        f'<span style="color:#6B7A99;font-size:0.68rem;">{entry.get("timestamp","")}</span>'
                        f'{result}</div>',
                        unsafe_allow_html=True
                    )
            else:
                st.markdown('<span style="font-size:0.78rem;color:#6B7A99;">No interactions yet</span>',
                            unsafe_allow_html=True)
            st.markdown("</div>", unsafe_allow_html=True)

        with loop_cols[1]:
            if topic_confidence:
                st.markdown("""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#6B7A99;margin-bottom:0.875rem;">Topic Confidence Map</div>
""", unsafe_allow_html=True)
                sorted_tc = sorted(
                    topic_confidence.items(),
                    key=lambda x: x[1].get("score", 50)
                )
                for topic_name, tc_data in sorted_tc[:6]:
                    score = tc_data.get("score", 50)
                    status = tc_data.get("status", "learning")
                    attempts = tc_data.get("attempts", 0)
                    color = {"strong": "#1FAD0F", "weak": "#F5C842", "learning": "#FF6B2B"}.get(status, "#FF6B2B")
                    st.markdown(
                        f'<div style="margin-bottom:0.625rem;">'
                        f'<div style="display:flex;justify-content:space-between;'
                        f'font-size:0.78rem;margin-bottom:3px;">'
                        f'<span style="color:#E8EDF8;">{topic_name[:26]}</span>'
                        f'<div style="display:flex;gap:8px;align-items:center;">'
                        f'<span style="font-size:0.65rem;color:#6B7A99;">{attempts} attempts</span>'
                        f'<span style="font-family:JetBrains Mono,monospace;color:{color};">{score}%</span>'
                        f'</div></div>'
                        f'<div style="height:5px;background:rgba(255,255,255,0.07);border-radius:3px;">'
                        f'<div style="width:{score}%;height:100%;background:linear-gradient(90deg,{color},{color}88);'
                        f'border-radius:3px;"></div></div></div>',
                        unsafe_allow_html=True
                    )
                st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Action buttons
    col_ref, col_new = st.columns(2)
    with col_ref:
        if st.button("🔄 Refresh Insights", key="insights_refresh"):
            st.session_state.insights_data = None
            st.rerun()
    with col_new:
        if st.button("✏️ Take Another Test", key="insights_to_practice"):
            from utils.session import set_tab
            st.session_state.practice_questions = []
            st.session_state.practice_generated = False
            set_tab("practice")
            st.rerun()
