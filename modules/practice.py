"""BharatiyaAI × LearnOS — Practice Test Page"""

import streamlit as st
from utils.ai import call_claude_json, call_claude, PRACTICE_SYSTEM, FEEDBACK_SYSTEM
from utils.session import flag_weak, flag_strong
from utils.pdf_reader import build_context_block


def _get_week_info():
    curriculum = st.session_state.get("curriculum", {})
    weeks = curriculum.get("weeks", [])
    idx = st.session_state.get("active_week", 0)
    if idx < len(weeks):
        w = weeks[idx]
        return w.get("name", ""), ", ".join(w.get("topics", []))
    return "", ""


def render_practice():
    week_name, week_topics = _get_week_info()

    st.markdown(f"""
<div style="margin-bottom:1.5rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.8rem;font-weight:600;">✏️ Practice Test</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">{week_name} · Adaptive Assessment</div>
</div>
""", unsafe_allow_html=True)

    questions = st.session_state.get("practice_questions", [])
    generated = st.session_state.get("practice_generated", False)
    topics_studied = st.session_state.get("topics_studied", [])

    # ── GENERATE PANEL ──
    if not generated:
        # Topics to test
        all_topics = list(set(topics_studied + ([week_topics] if week_topics else [])))

        st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,107,43,0.12);
border-left:3px solid #FF6B2B;border-radius:14px;padding:1.5rem;margin-bottom:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#6B7A99;margin-bottom:0.75rem;">
    Topics for this test
  </div>
""", unsafe_allow_html=True)

        if topics_studied:
            chips = "".join(
                f'<span style="display:inline-flex;font-size:0.75rem;padding:3px 10px;border-radius:20px;margin:2px;'
                f'background:rgba(255,107,43,0.1);border:1px solid rgba(255,107,43,0.2);color:#FF8F5A;">{t}</span>'
                for t in topics_studied
            )
            st.markdown(chips + "</div>", unsafe_allow_html=True)
        else:
            st.markdown(
                '<div style="font-size:0.8rem;color:#6B7A99;margin-bottom:0.75rem;">'
                'No topics studied yet. A test will be generated from your week\'s syllabus.</div></div>',
                unsafe_allow_html=True
            )

        if st.button("✏️ Generate Practice Questions", key="pq_generate", use_container_width=True):
            topic_list = ", ".join(topics_studied) if topics_studied else week_topics
            if not topic_list:
                topic_list = st.session_state.get("subject", "general")

            context = build_context_block(
                st.session_state.get("uploaded_text", ""),
                topic_list
            )

            with st.spinner("Crafting adaptive questions from your material…"):
                data = call_claude_json(PRACTICE_SYSTEM, context, max_tokens=1400)

            if data and isinstance(data, list):
                st.session_state.practice_questions = data
                st.session_state.practice_answers = {}
                st.session_state.practice_feedbacks = {}
                st.session_state.practice_revealed = {}
                st.session_state.practice_generated = True
                st.rerun()
            else:
                st.error("Could not generate questions. Check your API key.")
        return

    # ── QUESTIONS ──
    answers = st.session_state.get("practice_answers", {})
    feedbacks = st.session_state.get("practice_feedbacks", {})
    revealed = st.session_state.get("practice_revealed", {})

    total_q = len(questions)
    answered = len(revealed)
    correct_so_far = sum(1 for v in feedbacks.values() if v.get("correct"))

    # Top stats bar
    col_stat1, col_stat2, col_stat3, col_stat4 = st.columns(4)
    with col_stat1:
        st.metric("Questions", total_q)
    with col_stat2:
        st.metric("Answered", answered)
    with col_stat3:
        st.metric("Correct", correct_so_far)
    with col_stat4:
        score = round(correct_so_far / answered * 100) if answered else 0
        st.metric("Score", f"{score}%" if answered else "—")

    st.markdown("<br>", unsafe_allow_html=True)

    # Adaptive test banner
    weak = st.session_state.get("weak_concepts", [])
    if weak:
        st.markdown(f"""
<div style="background:rgba(255,107,43,0.04);border:1px solid rgba(255,107,43,0.12);
border-radius:10px;padding:0.75rem 1rem;margin-bottom:1rem;font-size:0.78rem;color:#8892BB;">
  ✦ Adaptive test — includes questions targeting your weak areas:
  {"".join(f'<span style="display:inline-flex;font-size:0.7rem;padding:1px 7px;border-radius:10px;margin:2px;background:rgba(245,200,66,0.1);border:1px solid rgba(245,200,66,0.2);color:#F5C842;">⚑ {w}</span>' for w in weak[:4])}
</div>
""", unsafe_allow_html=True)

    for qi, q in enumerate(questions):
        is_revealed = revealed.get(qi, False)
        answer_idx = answers.get(qi)
        feedback = feedbacks.get(qi)

        st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:16px;padding:1.5rem;margin-bottom:1.25rem;">
  <div style="font-family:'JetBrains Mono',monospace;font-size:0.7rem;color:#6B7A99;margin-bottom:0.625rem;">
    Q{qi+1} of {total_q}
  </div>
  <div style="font-family:'Noto Serif',serif;font-size:1.1rem;line-height:1.5;margin-bottom:1.25rem;">
    {q.get('question', '')}
  </div>
""", unsafe_allow_html=True)

        options = q.get("options", [])
        correct_idx = q.get("answer", 0)

        for oi, opt in enumerate(options):
            if not is_revealed:
                # Clickable button
                btn_style = "primary" if answer_idx == oi else "secondary"
                if st.button(opt, key=f"pq_{qi}_{oi}", use_container_width=True):
                    # Record answer and get feedback
                    st.session_state.practice_answers[qi] = oi
                    st.session_state.practice_revealed[qi] = True

                    is_correct = oi == correct_idx
                    st.session_state.questions_attempted += 1
                    topic_tag = q.get("topic_tag", st.session_state.get("last_topic", week_name))
                    if is_correct:
                        st.session_state.correct_count += 1
                        flag_strong(topic_tag)
                    else:
                        flag_weak(topic_tag)

                    # Log to interaction history for adaptive engine
                    from utils.session import log_interaction
                    log_interaction("practice", topic_tag, correct=is_correct)

                    # Compute session score
                    attempted = st.session_state.questions_attempted
                    correct_total = st.session_state.correct_count
                    if attempted > 0:
                        st.session_state.session_score = round(correct_total / attempted * 100)

                    # Get AI feedback
                    with st.spinner("Getting feedback…"):
                        fb_text = call_claude(
                            FEEDBACK_SYSTEM,
                            f"Question: {q.get('question')}\n"
                            f"Student picked: {opt}\n"
                            f"Correct answer: {options[correct_idx]}\n"
                            f"Hint: {q.get('explanation', '')}",
                            max_tokens=200,
                        )
                    st.session_state.practice_feedbacks[qi] = {
                        "text": fb_text,
                        "correct": is_correct,
                    }
                    st.rerun()
            else:
                # Show results
                if oi == correct_idx:
                    style_class = "opt-correct"
                    prefix = "✓ "
                elif oi == answer_idx:
                    style_class = "opt-wrong"
                    prefix = "✗ "
                else:
                    style_class = ""
                    prefix = ""

                border_map = {
                    "opt-correct": "border:1.5px solid #1FAD0F;background:rgba(19,136,8,0.10);color:#1FAD0F;",
                    "opt-wrong":   "border:1.5px solid #F76F6F;background:rgba(247,111,111,0.08);color:#F76F6F;",
                    "":            "border:1.5px solid rgba(255,255,255,0.07);background:rgba(22,34,68,1);color:#6B7A99;",
                }
                st.markdown(
                    f'<div style="padding:0.75rem 1rem;border-radius:10px;margin-bottom:0.5rem;font-size:0.875rem;'
                    f'{border_map.get(style_class, "")}">{prefix}{opt}</div>',
                    unsafe_allow_html=True
                )

        # Feedback box
        if feedback:
            fb_color = "rgba(19,136,8,0.12)" if feedback["correct"] else "rgba(247,111,111,0.08)"
            fb_border = "rgba(19,136,8,0.2)" if feedback["correct"] else "rgba(247,111,111,0.2)"
            fb_text_color = "#6ff7c4" if feedback["correct"] else "#f9a0a0"
            st.markdown(
                f'<div style="background:{fb_color};border:1px solid {fb_border};'
                f'border-radius:10px;padding:0.875rem 1rem;font-size:0.825rem;'
                f'color:{fb_text_color};margin-top:0.5rem;line-height:1.6;">'
                f'{feedback["text"]}</div>',
                unsafe_allow_html=True
            )

        st.markdown("</div>", unsafe_allow_html=True)

    # ── RESULT BANNER ──
    if answered == total_q and total_q > 0:
        final_score = round(correct_so_far / total_q * 100)
        st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,107,43,0.2);
border-radius:20px;padding:2.5rem;text-align:center;margin-top:1rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.3rem;margin-bottom:0.5rem;">Test Complete!</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:3.5rem;color:#FF6B2B;margin:0.5rem 0;">{final_score}%</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-bottom:1.5rem;">
    {correct_so_far} correct · {total_q - correct_so_far} to revise
  </div>
</div>
""", unsafe_allow_html=True)

        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("◈ View Insights", use_container_width=True, key="pq_insights"):
                from utils.session import set_tab
                set_tab("insights")
                st.rerun()
        with c2:
            if st.button("🔁 Try Again", use_container_width=True, key="pq_retry"):
                st.session_state.practice_questions = []
                st.session_state.practice_generated = False
                st.rerun()
        with c3:
            if st.button("New Topic Set", use_container_width=True, key="pq_new"):
                st.session_state.practice_questions = []
                st.session_state.practice_generated = False
                st.rerun()
