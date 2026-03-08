"""
BharatiyaAI Mentor — Viva Examiner Mode
The WOW feature: AI plays strict external examiner
85% threshold, counter-questioning, full scorecard
"""

import streamlit as st
from utils.ai import (
    call_bedrock, call_bedrock_json,
    VIVA_EXAMINER_SYSTEM, VIVA_SCORECARD_SYSTEM
)
from utils.session import log_interaction, get_weak_context
from utils.auth import add_xp, save_user_progress


FIRST_QUESTION_SYSTEM = """You are a strict external examiner starting a viva voce examination.
Ask the first question to begin the viva on the given topic.
Start with a fundamental concept question to assess baseline understanding.
Ask ONE clear, specific question. No preamble. Just the question."""

EVALUATE_ANSWER_SYSTEM = """You are evaluating a student's viva answer.
Check for: correct terminology, conceptual depth, answer completeness.
Return JSON:
{
  "score_pct": 75,
  "terminology_correct": true,
  "depth_adequate": false,
  "missing_points": ["what was missing"],
  "wrong_terms": ["incorrect term → correct term"],
  "pass": false,
  "feedback": "one line examiner-style feedback",
  "counter_question": "follow-up question if score < 85%"
}
pass = true if score_pct >= 85."""


def _build_viva_system() -> str:
    subject  = st.session_state.get("subject", "")
    uni      = st.session_state.get("university", "")
    weak_ctx = get_weak_context()
    curriculum = st.session_state.get("curriculum", {})
    active_week = st.session_state.get("active_week", 0)
    weeks = curriculum.get("weeks", []) if curriculum else []
    week_topics = []
    if weeks and active_week < len(weeks):
        week_topics = weeks[active_week].get("topics", [])

    return f"""{VIVA_EXAMINER_SYSTEM}

Subject: {subject}
University: {uni}
Topics to examine: {', '.join(week_topics) if week_topics else subject}
{weak_ctx}

Remember: you are not a friendly tutor. You are an examiner.
Be formal. Be demanding. Reward precision."""


def render_viva():
    st.markdown("""
<div class="page-title">🧠 Viva Examiner Mode</div>
<div class="page-subtitle">Practice with a strict AI examiner before your real viva</div>
""", unsafe_allow_html=True)

    active = st.session_state.get("viva_active", False)
    scorecard = st.session_state.get("viva_scorecard", None)

    if scorecard:
        _render_scorecard(scorecard)
        return

    if not active:
        _render_start_screen()
    else:
        _render_viva_session()


def _render_start_screen():
    subject  = st.session_state.get("subject", "")
    uni      = st.session_state.get("university", "")
    curriculum = st.session_state.get("curriculum", {})
    active_week = st.session_state.get("active_week", 0)
    weeks = curriculum.get("weeks", []) if curriculum else []
    week_topics = []
    if weeks and active_week < len(weeks):
        week_topics = weeks[active_week].get("topics", [])

    st.markdown(f"""
<div class="viva-examiner-card animate-fade">
  <div style="font-size:2.5rem;margin-bottom:0.75rem;">👨‍💼</div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.3rem;font-weight:700;
  margin-bottom:4px;">External Examiner</div>
  <div style="font-size:0.82rem;color:#5A7FA8;margin-bottom:0.5rem;">
    {subject} · {uni}
  </div>
  <div style="font-size:0.75rem;color:#2A3A50;">Strict · Fair · University Standard</div>
</div>

<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.09);
border-radius:16px;padding:1.5rem;margin-bottom:1.5rem;">
  <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#4AB7E0;margin-bottom:1rem;">How Viva Works</div>
  <div style="font-size:0.85rem;color:#5A7FA8;line-height:1.9;">
    ① The examiner asks you a question<br>
    ② You type your answer using proper technical terminology<br>
    ③ If ≥85% correct → examiner moves to next concept<br>
    ④ If &lt;85% → examiner counter-questions what you missed<br>
    ⑤ After 2 failed attempts → examiner reveals the correct answer<br>
    ⑥ Final scorecard with predicted viva score out of 25
  </div>
</div>
""", unsafe_allow_html=True)

    # Topic selection
    st.markdown('<span class="sec-label">Choose Topic to be Examined On</span>',
                unsafe_allow_html=True)

    col_topic, col_start = st.columns([3, 1])
    with col_topic:
        default_topic = week_topics[0] if week_topics else subject
        viva_topic = st.text_input(
            "Topic",
            value=st.session_state.get("viva_topic", default_topic),
            key="viva_topic_input",
            label_visibility="collapsed",
        )
    with col_start:
        if st.button("Begin Viva →", key="viva_start",
                     use_container_width=True):
            if viva_topic.strip():
                st.session_state.viva_topic = viva_topic.strip()
                _start_viva(viva_topic.strip())
            else:
                st.warning("Enter a topic to be examined on.")

    # Suggested topics
    if week_topics:
        st.markdown("""
<div style="font-size:0.72rem;color:#2A3A50;margin-top:0.5rem;margin-bottom:6px;">
  Suggested topics from your current week:
</div>
""", unsafe_allow_html=True)
        cols = st.columns(min(len(week_topics), 4))
        for col, t in zip(cols, week_topics[:4]):
            with col:
                if st.button(t[:18], key=f"viva_suggest_{t}",
                             use_container_width=True):
                    st.session_state.viva_topic = t
                    _start_viva(t)


def _start_viva(topic: str):
    """Initialize and get first examiner question."""
    with st.spinner("Examiner is preparing your viva…"):
        subj = st.session_state.get("subject", "")
        uni  = st.session_state.get("university", "")
        first_q = call_bedrock(
            FIRST_QUESTION_SYSTEM,
            f"Begin viva on: {topic}\nSubject: {subj}\nUniversity: {uni}",
            use_sonnet=False,
            max_tokens=200,
        )
        if first_q.startswith("ERROR"):
            st.error(f"Could not start viva: {first_q}")
            return

        st.session_state.viva_active = True
        st.session_state.viva_history = [{
            "role": "examiner",
            "content": first_q,
            "question_no": 1,
        }]
        st.session_state.viva_question_count = 1
        st.session_state.viva_failed_attempts = 0
        st.session_state.viva_scores = []
        st.session_state.viva_scorecard = None
        st.rerun()


def _render_viva_session():
    topic    = st.session_state.get("viva_topic", "")
    history  = st.session_state.get("viva_history", [])
    q_count  = st.session_state.get("viva_question_count", 1)
    failed   = st.session_state.get("viva_failed_attempts", 0)
    scores   = st.session_state.get("viva_scores", [])

    # ── EXAMINER HEADER ──
    st.markdown(f"""
<div class="viva-examiner-card">
  <div style="display:flex;align-items:center;justify-content:space-between;">
    <div style="display:flex;align-items:center;gap:12px;">
      <div style="font-size:1.8rem;">👨‍💼</div>
      <div style="text-align:left;">
        <div style="font-weight:700;font-size:0.9rem;">External Examiner</div>
        <div style="font-size:0.72rem;color:#5A7FA8;">{topic} · {st.session_state.get('university','')}</div>
      </div>
    </div>
    <div style="text-align:right;">
      <div style="font-size:0.62rem;color:#2A3A50;text-transform:uppercase;letter-spacing:0.08em;">
        Question
      </div>
      <div style="font-family:JetBrains Mono,monospace;font-size:1.1rem;color:#6ECAEC;">
        {q_count}
      </div>
    </div>
  </div>
  <div style="display:flex;align-items:center;gap:6px;margin-top:0.75rem;">
    <div style="width:8px;height:8px;background:#FF4757;border-radius:50%;
    animation:pulse 1s infinite;"></div>
    <div style="font-size:0.68rem;color:#FF4757;">Viva in Progress</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # ── CHAT HISTORY ──
    for msg in history:
        role = msg.get("role")
        content = msg.get("content", "")
        if role == "examiner":
            st.markdown(f"""
<div class="viva-question animate-fade">
  <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#4AB7E0;margin-bottom:0.5rem;">Examiner asks:</div>
  {content}
</div>
""", unsafe_allow_html=True)
        elif role == "student":
            st.markdown(f"""
<div class="chat-user" style="font-size:0.875rem;">
  <div style="font-size:0.6rem;color:#3A5A7A;margin-bottom:4px;">Your answer:</div>
  {content}
</div>
""", unsafe_allow_html=True)
        elif role == "feedback":
            passed = msg.get("passed", False)
            color = "#00E676" if passed else "#FFD166"
            icon = "✓" if passed else "↺"
            st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.09);
border-left:3px solid {color};border-radius:12px;padding:0.875rem 1rem;
margin-bottom:0.75rem;font-size:0.82rem;color:#5A7FA8;">
  <span style="color:{color};font-weight:600;">{icon} </span>{content}
</div>
""", unsafe_allow_html=True)
        elif role == "correction":
            st.markdown(f"""
<div style="background:rgba(255,71,87,0.06);border:1px solid rgba(255,71,87,0.2);
border-radius:12px;padding:0.875rem 1rem;margin-bottom:0.75rem;
font-size:0.82rem;color:#5A7FA8;">
  <div style="font-size:0.6rem;text-transform:uppercase;letter-spacing:0.08em;
  color:#FF4757;margin-bottom:4px;">Correct Answer</div>
  {content}
</div>
""", unsafe_allow_html=True)

    # ── ANSWER INPUT ──
    # Check if last message is from examiner (waiting for student)
    if history and history[-1].get("role") == "examiner":
        st.markdown("<div style='height:0.5rem'></div>", unsafe_allow_html=True)

        col_ans, col_btns = st.columns([4, 1])
        with col_ans:
            student_answer = st.text_area(
                "Your answer",
                placeholder="Type your answer using correct technical terminology...",
                key=f"viva_ans_{q_count}_{failed}",
                height=120,
                label_visibility="collapsed",
            )
        with col_btns:
            st.markdown("<br>", unsafe_allow_html=True)
            submit = st.button("Submit →", key=f"viva_submit_{q_count}_{failed}",
                               use_container_width=True)
            end = st.button("End Viva", key="viva_end",
                            use_container_width=True)

        if end:
            _end_viva()
            return

        if submit and student_answer.strip():
            _process_viva_answer(student_answer.strip(), history, q_count, failed, scores, topic)


def _process_viva_answer(answer: str, history: list, q_count: int,
                         failed: int, scores: list, topic: str):
    # Get the current question
    current_q = ""
    for msg in reversed(history):
        if msg.get("role") == "examiner":
            current_q = msg.get("content", "")
            break

    # Add student answer to history
    history.append({"role": "student", "content": answer})

    # Evaluate
    with st.spinner("Examiner is evaluating your answer…"):
        viva_system = _build_viva_system()
        eval_prompt = f"""Question: {current_q}
Student's answer: {answer}
Topic: {topic}
Subject: {st.session_state.get('subject', '')}"""

        result = call_bedrock_json(
            EVALUATE_ANSWER_SYSTEM + f"\n\nContext:\n{viva_system}",
            eval_prompt,
            use_sonnet=False,
            max_tokens=500,
        )

    if not result:
        st.error("Evaluation failed. Try again.")
        return

    score_pct   = result.get("score_pct", 50)
    passed      = result.get("pass", score_pct >= 85)
    feedback    = result.get("feedback", "")
    counter_q   = result.get("counter_question", "")
    wrong_terms = result.get("wrong_terms", [])
    missing     = result.get("missing_points", [])

    scores.append({
        "question": current_q[:60],
        "score_pct": score_pct,
        "passed": passed,
        "wrong_terms": wrong_terms,
    })

    # Add feedback
    feedback_content = feedback
    if wrong_terms:
        feedback_content += f"\n\n⚑ Terminology: {'; '.join(wrong_terms[:2])}"
    history.append({
        "role": "feedback",
        "content": feedback_content,
        "passed": passed,
    })

    if passed:
        # Move to next question
        log_interaction("viva", topic, correct=True)
        add_xp(20, "viva question passed")
        st.session_state.viva_failed_attempts = 0

        # Get next question (after 5 questions, end)
        new_q_count = q_count + 1
        if new_q_count > 5:
            st.session_state.viva_history = history
            st.session_state.viva_scores = scores
            _end_viva()
            return

        next_q = _get_next_question(history, topic, score_pct)
        history.append({
            "role": "examiner",
            "content": next_q,
            "question_no": new_q_count,
        })
        st.session_state.viva_question_count = new_q_count
    else:
        # Counter-question or correction
        new_failed = failed + 1
        log_interaction("viva", topic, correct=False)

        if new_failed >= 2:
            # Show correct answer
            correct_ans = _get_correct_answer(current_q, topic)
            history.append({
                "role": "correction",
                "content": correct_ans,
            })
            st.session_state.viva_failed_attempts = 0
            # Move to next question
            new_q_count = q_count + 1
            if new_q_count > 5:
                st.session_state.viva_history = history
                st.session_state.viva_scores = scores
                _end_viva()
                return
            next_q = _get_next_question(history, topic, score_pct)
            history.append({
                "role": "examiner",
                "content": next_q,
                "question_no": new_q_count,
            })
            st.session_state.viva_question_count = new_q_count
        else:
            # Counter-question
            if counter_q:
                history.append({
                    "role": "examiner",
                    "content": counter_q,
                    "question_no": q_count,
                })
            st.session_state.viva_failed_attempts = new_failed

    st.session_state.viva_history = history
    st.session_state.viva_scores = scores
    st.rerun()


def _get_next_question(history: list, topic: str, prev_score: int) -> str:
    subj = st.session_state.get("subject", "")
    uni  = st.session_state.get("university", "")
    history_summary = " → ".join(
        msg["content"][:40] for msg in history if msg.get("role") == "examiner"
    )
    next_q = call_bedrock(
        f"""{VIVA_EXAMINER_SYSTEM}
Subject: {subj}. University: {uni}.
Previous questions covered: {history_summary}
Ask the NEXT question on a DIFFERENT aspect of {topic}.
If previous score was low ({prev_score}%), stay on basics.
If score was high (>85%), advance to application/analysis level.
ONE question only. No preamble.""",
        f"Next viva question on {topic}:",
        use_sonnet=False,
        max_tokens=150,
    )
    return next_q


def _get_correct_answer(question: str, topic: str) -> str:
    subj = st.session_state.get("subject", "")
    return call_bedrock(
        f"""You are explaining a viva answer to a student who got it wrong.
Give the correct, complete answer in 3-5 sentences using proper terminology.
Subject: {subj}. Topic: {topic}.""",
        f"Question: {question}\nProvide the correct answer:",
        use_sonnet=False,
        max_tokens=300,
    )


def _end_viva():
    """Generate scorecard and end session."""
    history  = st.session_state.get("viva_history", [])
    scores   = st.session_state.get("viva_scores", [])
    topic    = st.session_state.get("viva_topic", "")
    subject  = st.session_state.get("subject", "")

    with st.spinner("Generating your viva scorecard…"):
        session_summary = "\n".join(
            f"Q: {s['question']} — Score: {s['score_pct']}%"
            + (f" — Wrong terms: {', '.join(s['wrong_terms'])}" if s.get('wrong_terms') else "")
            for s in scores
        )
        scorecard = call_bedrock_json(
            VIVA_SCORECARD_SYSTEM,
            f"Topic: {topic}\nSubject: {subject}\nSession:\n{session_summary}",
            use_sonnet=False,
            max_tokens=600,
        )

    if scorecard:
        st.session_state.viva_scorecard = scorecard
        st.session_state.viva_active = False
        viva_sessions = st.session_state.get("viva_sessions", 0) + 1
        st.session_state.viva_sessions = viva_sessions
        predicted = scorecard.get("predicted_score", 0)
        if predicted >= 20:
            add_xp(50, "excellent viva")
        elif predicted >= 15:
            add_xp(30, "good viva")
        else:
            add_xp(15, "viva completed")
        save_user_progress()
    else:
        st.error("Could not generate scorecard. Check AWS.")
    st.rerun()


def _render_scorecard(scorecard: dict):
    topic = st.session_state.get("viva_topic", "")
    predicted = scorecard.get("predicted_score", 0)
    terminology = scorecard.get("terminology_score", 0)
    depth       = scorecard.get("depth_score", 0)
    structure   = scorecard.get("structure_score", 0)
    grade       = scorecard.get("grade", "")
    strengths   = scorecard.get("strengths", [])
    weak_areas  = scorecard.get("weak_areas", [])
    term_errors = scorecard.get("terminology_errors", [])
    comment     = scorecard.get("examiner_comment", "")
    revision    = scorecard.get("revision_priority", [])

    pct = int(predicted / 25 * 100)
    score_color = "#00E676" if pct >= 70 else ("#FFD166" if pct >= 50 else "#FF4757")

    st.markdown(f"""
<div style="background:linear-gradient(135deg,rgba(74,183,224,0.08),rgba(17,43,26,0));
border:1px solid rgba(74,183,224,0.18);border-radius:20px;padding:2rem;
margin-bottom:1.5rem;text-align:center;" class="animate-fade">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;
  margin-bottom:0.5rem;">Viva Scorecard</div>
  <div style="font-size:0.8rem;color:#3A5A7A;margin-bottom:1.25rem;">{topic}</div>
  <div style="font-size:4rem;font-family:JetBrains Mono,monospace;color:{score_color};
  line-height:1;">{predicted}<span style="font-size:1.5rem;color:#2A3A50;">/25</span></div>
  <div style="font-size:0.9rem;color:{score_color};margin:0.5rem 0 1rem;
  font-weight:600;">{grade}</div>
  <div style="font-size:0.8rem;color:#3A5A7A;font-style:italic;">"{comment}"</div>
</div>
""", unsafe_allow_html=True)

    # Score breakdown
    cols = st.columns(3)
    with cols[0]:
        t_pct = int(terminology / 10 * 100)
        st.markdown(f"""
<div style="text-align:center;background:rgba(30,41,59,0.95);
border:1px solid rgba(74,183,224,0.09);border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#3A5A7A;margin-bottom:0.5rem;">Terminology</div>
  <div style="font-size:2rem;font-family:JetBrains Mono,monospace;color:#6ECAEC;">
    {terminology}/10</div>
  <div style="height:4px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:0.5rem;">
    <div style="width:{t_pct}%;height:100%;background:#4AB7E0;border-radius:2px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)
    with cols[1]:
        d_pct = int(depth / 10 * 100)
        st.markdown(f"""
<div style="text-align:center;background:rgba(30,41,59,0.95);
border:1px solid rgba(74,183,224,0.09);border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#3A5A7A;margin-bottom:0.5rem;">Concept Depth</div>
  <div style="font-size:2rem;font-family:JetBrains Mono,monospace;color:#6ECAEC;">
    {depth}/10</div>
  <div style="height:4px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:0.5rem;">
    <div style="width:{d_pct}%;height:100%;background:#4AB7E0;border-radius:2px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)
    with cols[2]:
        s_pct = int(structure / 5 * 100)
        st.markdown(f"""
<div style="text-align:center;background:rgba(30,41,59,0.95);
border:1px solid rgba(74,183,224,0.09);border-radius:14px;padding:1.25rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#3A5A7A;margin-bottom:0.5rem;">Answer Structure</div>
  <div style="font-size:2rem;font-family:JetBrains Mono,monospace;color:#6ECAEC;">
    {structure}/5</div>
  <div style="height:4px;background:rgba(255,255,255,0.05);border-radius:2px;margin-top:0.5rem;">
    <div style="width:{s_pct}%;height:100%;background:#4AB7E0;border-radius:2px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    detail_cols = st.columns(2)

    with detail_cols[0]:
        if strengths:
            st.markdown('<span class="sec-label">💪 Strengths</span>',
                        unsafe_allow_html=True)
            for s in strengths:
                st.markdown(
                    f'<div style="font-size:0.82rem;padding:4px 0;color:#00E676;">✓ {s}</div>',
                    unsafe_allow_html=True
                )
        if term_errors:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<span class="sec-label">⚑ Terminology Corrections</span>',
                        unsafe_allow_html=True)
            for e in term_errors:
                st.markdown(
                    f'<div style="font-size:0.8rem;padding:4px 0;color:#FFD166;">• {e}</div>',
                    unsafe_allow_html=True
                )

    with detail_cols[1]:
        if weak_areas:
            st.markdown('<span class="sec-label">📚 Areas to Improve</span>',
                        unsafe_allow_html=True)
            for w in weak_areas:
                st.markdown(
                    f'<div style="font-size:0.82rem;padding:4px 0;color:#6ECAEC;">⚑ {w}</div>',
                    unsafe_allow_html=True
                )
        if revision:
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<span class="sec-label">🔄 Revise Before Next Viva</span>',
                        unsafe_allow_html=True)
            for r in revision:
                st.markdown(
                    f'<div style="font-size:0.8rem;padding:4px 0;color:#5A7FA8;">→ {r}</div>',
                    unsafe_allow_html=True
                )

    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    with c1:
        if st.button("🔄 New Viva Session", key="viva_new",
                     use_container_width=True):
            st.session_state.viva_scorecard = None
            st.session_state.viva_active = False
            st.session_state.viva_history = []
            st.session_state.viva_scores = []
            st.session_state.viva_question_count = 1
            st.session_state.viva_failed_attempts = 0
            st.rerun()
    with c2:
        if st.button("🏠 Back to Dashboard", key="viva_dash",
                     use_container_width=True):
            from utils.session import set_tab
            st.session_state.viva_scorecard = None
            set_tab("home")
            st.rerun()
