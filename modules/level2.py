"""BharatiyaAI Mentor — Level 2: Practice"""

import streamlit as st
from utils.ai import call_bedrock_json, call_bedrock, PRACTICE_SYSTEM, FEEDBACK_SYSTEM
from utils.session import flag_weak, flag_strong, log_interaction, get_weak_context
from utils.auth import add_xp, save_user_progress


def _build_practice_prompt() -> str:
    subject  = st.session_state.get("subject", "")
    uni      = st.session_state.get("university", "")
    topics   = st.session_state.get("topics_studied", [])
    weak     = st.session_state.get("weak_concepts", [])
    curriculum = st.session_state.get("curriculum", {})
    active_week = st.session_state.get("active_week", 0)
    weeks = curriculum.get("weeks", []) if curriculum else []
    week_topics = []
    if weeks and active_week < len(weeks):
        week_topics = weeks[active_week].get("topics", [])

    focus_topics = week_topics or topics[-5:] or [subject]
    return f"""
Subject: {subject}
University: {uni}
Topics to test: {", ".join(focus_topics)}
Weak areas to target: {", ".join(weak[:5]) if weak else "None identified yet"}
Generate adaptive practice questions focusing on weak areas.
"""


def render_level2():
    st.markdown("""
<div class="page-title">✏️ Level 2 — Practice</div>
<div class="page-subtitle">Strengthen articulation and retention through adaptive testing</div>
""", unsafe_allow_html=True)

    tabs = st.tabs(["📝 Adaptive Test", "📊 Performance"])

    with tabs[0]:
        _render_practice()

    with tabs[1]:
        _render_performance()


def _render_practice():
    weak = st.session_state.get("weak_concepts", [])
    questions = st.session_state.get("practice_questions", [])
    generated = st.session_state.get("practice_generated", False)

    # ── WEAK AREA BANNER ──
    if weak:
        chips = "".join(
            f'<span style="display:inline-block;font-size:0.7rem;padding:2px 8px;'
            f'margin:2px;border-radius:6px;background:rgba(255,209,102,0.08);'
            f'border:1px solid rgba(255,209,102,0.2);color:#FFD166;">⚑ {w[:20]}</span>'
            for w in weak[:5]
        )
        st.markdown(f"""
<div style="background:rgba(255,209,102,0.04);border:1px solid rgba(255,209,102,0.15);
border-radius:12px;padding:0.75rem 1rem;margin-bottom:1rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#FFD166;margin-bottom:6px;">⚡ Adaptive — Targeting Your Weak Areas</div>
  <div>{chips}</div>
</div>
""", unsafe_allow_html=True)

    # ── GENERATE ──
    col_gen, col_reset = st.columns([3, 1])
    with col_gen:
        if st.button(
            "🎲 Generate Adaptive Test" if not generated else "🔄 New Test",
            key="l2_generate",
            use_container_width=True,
        ):
            with st.spinner("Generating adaptive questions…"):
                prompt = _build_practice_prompt()
                questions = call_bedrock_json(
                    PRACTICE_SYSTEM, prompt,
                    use_sonnet=False, max_tokens=1500
                )
                if questions and isinstance(questions, list):
                    st.session_state.practice_questions = questions
                    st.session_state.practice_answers = {}
                    st.session_state.practice_feedbacks = {}
                    st.session_state.practice_revealed = {}
                    st.session_state.practice_generated = True
                    st.rerun()
                else:
                    st.error("Could not generate questions. Check AWS credentials.")
    with col_reset:
        if generated and st.button("Reset", key="l2_reset", use_container_width=True):
            st.session_state.practice_questions = []
            st.session_state.practice_answers = {}
            st.session_state.practice_feedbacks = {}
            st.session_state.practice_revealed = {}
            st.session_state.practice_generated = False
            st.rerun()

    if not questions:
        st.markdown("""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.08);
border-radius:16px;padding:3rem;text-align:center;color:#2A3A50;margin-top:1rem;">
  <div style="font-size:2rem;margin-bottom:0.75rem;">✏️</div>
  <div>Generate a test to begin practice.<br>
  <span style="font-size:0.8rem;">Questions adapt to your weak areas automatically.</span></div>
</div>
""", unsafe_allow_html=True)
        return

    # ── QUESTIONS ──
    answers = st.session_state.get("practice_answers", {})
    feedbacks = st.session_state.get("practice_feedbacks", {})
    revealed = st.session_state.get("practice_revealed", {})

    for i, q in enumerate(questions):
        q_text    = q.get("question", "")
        q_type    = q.get("type", "mcq")
        options   = q.get("options", [])
        correct   = q.get("answer", 0)
        marks     = q.get("marks", 2)
        topic_tag = q.get("topic_tag", "")
        difficulty = q.get("difficulty", "medium")
        explanation = q.get("explanation", "")

        diff_color = {"easy": "#00E676", "medium": "#FFD166", "hard": "#FF4757"}.get(difficulty, "#FFD166")
        is_answered = i in answers
        is_revealed = revealed.get(i, False)

        st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.09);
border-radius:16px;padding:1.25rem;margin-bottom:1rem;">
  <div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.75rem;">
    <div>
      <span style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
      color:#3A5A7A;">Q{i+1} · {marks} marks</span>
      {"<span style='font-size:0.62rem;margin-left:8px;padding:1px 6px;border-radius:4px;" +
       f"background:rgba(255,107,26,0.1);color:#6ECAEC;'>{topic_tag}</span>" if topic_tag else ""}
    </div>
    <span style="font-size:0.65rem;color:{diff_color};text-transform:uppercase;
    letter-spacing:0.08em;">{difficulty}</span>
  </div>
  <div style="font-size:0.9rem;font-weight:500;line-height:1.6;margin-bottom:1rem;">
    {q_text}
  </div>
</div>
""", unsafe_allow_html=True)

        if q_type == "mcq" and options:
            for j, opt in enumerate(options):
                is_correct_opt = (j == correct)
                user_picked = (answers.get(i) == j)

                if is_revealed:
                    if is_correct_opt:
                        cls = "opt-correct"
                    elif user_picked and not is_correct_opt:
                        cls = "opt-wrong"
                    else:
                        cls = ""
                    st.markdown(
                        f'<div style="padding:8px 12px;border-radius:8px;margin-bottom:4px;'
                        f'font-size:0.85rem;border:1px solid rgba(74,183,224,0.09);"'
                        f' class="{cls}">{chr(65+j)}. {opt}</div>',
                        unsafe_allow_html=True
                    )
                else:
                    if st.button(
                        f"{chr(65+j)}. {opt}",
                        key=f"opt_{i}_{j}",
                        use_container_width=True,
                        disabled=is_answered,
                    ):
                        answers[i] = j
                        st.session_state.practice_answers = answers
                        is_correct = (j == correct)
                        _process_answer(i, topic_tag, is_correct, q_text, opt, explanation)
                        revealed[i] = True
                        st.session_state.practice_revealed = revealed
                        st.rerun()

        elif q_type == "short":
            model_answer = q.get("model_answer", explanation)
            if not is_answered:
                ans_text = st.text_area(
                    f"Your answer (Q{i+1})",
                    placeholder="Write your answer here...",
                    key=f"short_{i}",
                    height=100,
                    label_visibility="collapsed",
                )
                if st.button(f"Submit Answer →", key=f"sub_{i}",
                             use_container_width=False):
                    if ans_text.strip():
                        answers[i] = ans_text
                        st.session_state.practice_answers = answers
                        # Get AI feedback
                        with st.spinner("Evaluating your answer…"):
                            fb_prompt = (
                                f"Question: {q_text}\n"
                                f"Student's answer: {ans_text}\n"
                                f"Model answer: {model_answer}"
                            )
                            fb = call_bedrock(
                                FEEDBACK_SYSTEM, fb_prompt,
                                use_sonnet=False, max_tokens=200,
                                use_cache=False,
                            )
                        feedbacks[i] = fb
                        st.session_state.practice_feedbacks = feedbacks
                        is_correct = "✓" in fb or "correct" in fb.lower()
                        _process_answer(i, topic_tag, is_correct, q_text, ans_text, model_answer)
                        revealed[i] = True
                        st.session_state.practice_revealed = revealed
                        st.rerun()
            else:
                st.markdown(
                    f'<div style="background:rgba(255,255,255,0.03);border-radius:8px;'
                    f'padding:0.75rem;font-size:0.85rem;color:#5A7FA8;margin-bottom:0.5rem;">'
                    f'Your answer: {answers[i]}</div>',
                    unsafe_allow_html=True
                )

        # Show feedback/explanation
        if is_revealed:
            is_correct_final = (answers.get(i) == correct) if q_type == "mcq" else None
            if q_type == "mcq":
                if is_correct_final:
                    st.success(f"✓ Correct! {explanation}")
                else:
                    correct_opt = options[correct] if correct < len(options) else "N/A"
                    st.error(f"✗ Incorrect. Correct answer: {chr(65+correct)}. {correct_opt}")
                    if explanation:
                        st.markdown(
                            f'<div style="font-size:0.82rem;color:#5A7FA8;padding:0.5rem 0;">'
                            f'💡 {explanation}</div>',
                            unsafe_allow_html=True
                        )
            elif i in feedbacks:
                fb = feedbacks[i]
                if "✓" in fb or "correct" in fb.lower():
                    st.success(fb)
                else:
                    st.warning(fb)

        st.markdown("</div>", unsafe_allow_html=True)

    # ── SUMMARY ──
    if len(revealed) == len(questions):
        _show_test_summary(questions, answers, revealed)


def _process_answer(q_idx, topic_tag, is_correct, question, user_answer, explanation):
    attempted = st.session_state.get("questions_attempted", 0) + 1
    st.session_state.questions_attempted = attempted

    if is_correct:
        correct_count = st.session_state.get("correct_count", 0) + 1
        st.session_state.correct_count = correct_count
        flag_strong(topic_tag)
        log_interaction("practice", topic_tag, correct=True)
        add_xp(10, "correct answer")
    else:
        flag_weak(topic_tag)
        log_interaction("practice", topic_tag, correct=False)


def _show_test_summary(questions, answers, revealed):
    correct_count = sum(
        1 for i, q in enumerate(questions)
        if q.get("type") == "mcq" and answers.get(i) == q.get("answer", 0)
    )
    mcq_total = sum(1 for q in questions if q.get("type") == "mcq")
    pct = int(correct_count / mcq_total * 100) if mcq_total else 0

    st.markdown("---")
    st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.18);
border-radius:20px;padding:2rem;text-align:center;margin-top:1rem;">
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.4rem;margin-bottom:0.75rem;">
    Test Complete
  </div>
  <div style="font-size:3rem;font-family:JetBrains Mono,monospace;color:#6ECAEC;">
    {correct_count}/{mcq_total}
  </div>
  <div style="color:#3A5A7A;margin-bottom:1rem;">MCQ Accuracy: {pct}%</div>
  <div style="font-size:0.85rem;color:#{'00E676' if pct >= 70 else 'FFD166'};">
    {"Strong performance! Keep it up." if pct >= 70 else "Review flagged topics before your next session."}
  </div>
</div>
""", unsafe_allow_html=True)

    if pct >= 85:
        add_xp(50, "excellent test performance")
        st.success("+50 XP — Excellent test performance!")
    elif pct >= 70:
        add_xp(25, "good test performance")
        st.success("+25 XP — Good performance!")
    save_user_progress()


def _render_performance():
    tc = st.session_state.get("topic_confidence", {})
    attempted = st.session_state.get("questions_attempted", 0)
    correct = st.session_state.get("correct_count", 0)
    accuracy = round(correct / attempted * 100) if attempted else 0
    log = st.session_state.get("interaction_log", [])
    practice_log = [l for l in log if l.get("type") == "practice"]

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Questions Attempted", attempted)
    with c2:
        st.metric("Correct Answers", correct)
    with c3:
        st.metric("Overall Accuracy", f"{accuracy}%")

    if tc:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="sec-label">Topic-wise Confidence</span>',
                    unsafe_allow_html=True)
        for topic, data in sorted(tc.items(), key=lambda x: x[1].get("score", 0)):
            score = data.get("score", 0)
            status = data.get("status", "learning")
            color = {"strong": "#00E676", "learning": "#FFD166", "weak": "#FF4757"}.get(status, "#FFD166")
            st.markdown(f"""
<div style="margin-bottom:0.75rem;">
  <div style="display:flex;justify-content:space-between;font-size:0.82rem;margin-bottom:4px;">
    <span style="color:#5A7FA8;">{topic}</span>
    <span style="font-family:JetBrains Mono,monospace;color:{color};">{int(score)}%</span>
  </div>
  <div style="height:5px;background:rgba(74,183,224,0.08);border-radius:3px;">
    <div style="width:{int(score)}%;height:100%;background:{color};border-radius:3px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)
    else:
        st.info("Complete practice sessions to see topic-wise performance.")

    if practice_log:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown('<span class="sec-label">Recent Practice Activity</span>',
                    unsafe_allow_html=True)
        for item in practice_log[-8:]:
            correct_icon = "✓" if item.get("correct") else "✗"
            color = "#00E676" if item.get("correct") else "#FF4757"
            st.markdown(
                f'<div style="font-size:0.78rem;padding:4px 0;border-bottom:'
                f'1px solid rgba(255,255,255,0.04);color:#5A7FA8;">'
                f'<span style="color:{color};">{correct_icon}</span> '
                f'{item.get("topic","?")} <span style="float:right;color:#2A3A50;">'
                f'{item.get("timestamp","")}</span></div>',
                unsafe_allow_html=True
            )
