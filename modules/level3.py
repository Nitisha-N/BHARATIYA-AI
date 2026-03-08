"""BharatiyaAI Mentor — Level 3: Exam Prep + PYQ Bank"""

import streamlit as st
from utils.ai import (
    call_bedrock, call_bedrock_json,
    PYQ_EXTRACT_SYSTEM, PYQ_GENERATE_SYSTEM, MODEL_ANSWER_SYSTEM
)
from utils.session import log_interaction
from utils.auth import add_xp, save_user_progress
from utils.pdf_reader import extract_text, upload_to_s3


def render_level3():
    st.markdown("""
<div class="page-title">🎯 Level 3 — Exam Prep</div>
<div class="page-subtitle">Own the exam — PYQ analysis, model answers, and frequency heatmap</div>
""", unsafe_allow_html=True)

    tabs = st.tabs(["📋 PYQ Bank", "📊 Frequency Analysis", "✍️ Model Answers"])

    with tabs[0]:
        _render_pyq_bank()
    with tabs[1]:
        _render_frequency()
    with tabs[2]:
        _render_model_answers()


def _render_pyq_bank():
    bank = st.session_state.get("pyq_bank", [])
    uni  = st.session_state.get("university", "")
    subj = st.session_state.get("subject", "")

    # ── UPLOAD OR GENERATE ──
    col_upload, col_gen = st.columns(2)

    with col_upload:
        st.markdown('<span class="sec-label">Upload Past Paper</span>',
                    unsafe_allow_html=True)
        pyq_file = st.file_uploader(
            "Upload PYQ PDF",
            type=["pdf", "txt"],
            key="pyq_upload",
            label_visibility="collapsed",
        )
        if pyq_file:
            if st.button("⚡ Extract Questions", key="pyq_extract",
                         use_container_width=True):
                with st.spinner("Extracting questions from paper…"):
                    text = extract_text(pyq_file)
                    if text and not text.startswith("["):
                        # Upload to S3
                        pyq_file.seek(0)
                        upload_to_s3(pyq_file.read(), pyq_file.name, folder="pyq")
                        # Extract
                        extracted = call_bedrock_json(
                            PYQ_EXTRACT_SYSTEM,
                            f"University: {uni}\nSubject: {subj}\n\n{text[:4000]}",
                            use_sonnet=False,
                            max_tokens=2000,
                        )
                        if extracted and isinstance(extracted, list):
                            existing = bank or []
                            merged = existing + extracted
                            st.session_state.pyq_bank = merged
                            add_xp(20, "PYQ uploaded")
                            st.success(f"✓ Extracted {len(extracted)} questions!")
                            st.rerun()
                        else:
                            st.error("Could not extract questions.")
                    else:
                        st.error("Could not read PDF. Try a different file.")

    with col_gen:
        st.markdown('<span class="sec-label">AI-Generate PYQ Style Questions</span>',
                    unsafe_allow_html=True)
        st.markdown(f"""
<div style="font-size:0.78rem;color:#3A5A7A;margin-bottom:0.75rem;">
  Generate expected questions for <strong>{subj}</strong> based on {uni} pattern
</div>
""", unsafe_allow_html=True)
        if st.button("🤖 Generate Expected Questions", key="pyq_generate",
                     use_container_width=True):
            topics_text = st.session_state.get("topics_text", "")
            curriculum = st.session_state.get("curriculum", {})
            all_topics = []
            if curriculum:
                for w in curriculum.get("weeks", []):
                    all_topics.extend(w.get("topics", []))
            topic_str = topics_text or ", ".join(all_topics[:15])

            with st.spinner(f"Generating expected questions for {uni}…"):
                generated = call_bedrock_json(
                    PYQ_GENERATE_SYSTEM,
                    f"University: {uni}\nSubject: {subj}\nTopics: {topic_str}",
                    use_sonnet=False,
                    max_tokens=2000,
                )
                if generated and isinstance(generated, list):
                    existing = bank or []
                    merged = existing + generated
                    st.session_state.pyq_bank = merged
                    add_xp(15, "PYQ generated")
                    st.success(f"✓ Generated {len(generated)} questions!")
                    st.rerun()
                else:
                    st.error("Generation failed. Check AWS credentials.")

    st.markdown("---")

    if not bank:
        st.markdown("""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.08);
border-radius:16px;padding:3rem;text-align:center;color:#2A3A50;">
  <div style="font-size:2rem;margin-bottom:0.75rem;">📋</div>
  Upload a past paper or generate expected questions to build your PYQ bank.
</div>
""", unsafe_allow_html=True)
        return

    # ── FILTERS ──
    st.markdown('<span class="sec-label">Filter Questions</span>',
                unsafe_allow_html=True)
    f1, f2, f3, f4 = st.columns(4)
    with f1:
        topics = list(set(q.get("topic", "") for q in bank if q.get("topic")))
        topic_filter = st.selectbox("Topic", ["All"] + sorted(topics), key="f_topic")
    with f2:
        diff_filter = st.selectbox("Difficulty", ["All", "easy", "medium", "hard"], key="f_diff")
    with f3:
        marks_filter = st.selectbox("Marks", ["All", "2", "5", "10"], key="f_marks")
    with f4:
        type_filter = st.selectbox("Type", ["All", "short", "long", "mcq", "numerical", "diagram"], key="f_type")

    # Apply filters
    filtered = bank
    if topic_filter != "All":
        filtered = [q for q in filtered if topic_filter.lower() in q.get("topic", "").lower()]
    if diff_filter != "All":
        filtered = [q for q in filtered if q.get("difficulty") == diff_filter]
    if marks_filter != "All":
        filtered = [q for q in filtered if str(q.get("marks", "")) == marks_filter]
    if type_filter != "All":
        filtered = [q for q in filtered if q.get("type") == type_filter]

    st.markdown(f"""
<div style="font-size:0.75rem;color:#3A5A7A;margin-bottom:1rem;">
  Showing <strong style="color:#6ECAEC;">{len(filtered)}</strong> of {len(bank)} questions
</div>
""", unsafe_allow_html=True)

    # ── QUESTION CARDS ──
    for i, q in enumerate(filtered[:20]):
        qtext     = q.get("question", "")
        marks     = q.get("marks", "?")
        qtype     = q.get("type", "long")
        topic     = q.get("topic", "")
        year      = q.get("year", "")
        difficulty = q.get("difficulty", "medium")
        hint      = q.get("hint", "")

        diff_color = {"easy": "#00E676", "medium": "#FFD166", "hard": "#FF4757"}.get(difficulty, "#FFD166")
        year_badge = f'<span style="font-size:0.6rem;padding:1px 5px;border-radius:4px;background:rgba(74,183,224,0.08);color:#6ECAEC;">{year}</span>' if year else ""

        with st.expander(f"Q{i+1}. {qtext[:80]}{'…' if len(qtext) > 80 else ''}"):
            st.markdown(f"""
<div style="padding:0.5rem 0;">
  <div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:0.75rem;">
    <span style="font-size:0.68rem;padding:2px 8px;border-radius:6px;
    background:rgba(255,255,255,0.05);color:#5A7FA8;">{marks} marks</span>
    <span style="font-size:0.68rem;padding:2px 8px;border-radius:6px;
    background:rgba(255,255,255,0.05);color:#5A7FA8;">{qtype}</span>
    <span style="font-size:0.68rem;padding:2px 8px;border-radius:6px;
    background:rgba(255,255,255,0.05);color:{diff_color};">{difficulty}</span>
    {year_badge}
    {f'<span style="font-size:0.68rem;padding:2px 8px;border-radius:6px;background:rgba(255,255,255,0.05);color:#5A7FA8;">{topic}</span>' if topic else ""}
  </div>
  <div style="font-size:0.9rem;line-height:1.7;margin-bottom:0.75rem;">{qtext}</div>
  {f'<div style="font-size:0.78rem;color:#3A5A7A;font-style:italic;">💡 Hint: {hint}</div>' if hint else ""}
</div>
""", unsafe_allow_html=True)

            col_ans, col_attempt = st.columns(2)
            with col_ans:
                if st.button(f"📖 View Model Answer", key=f"pyq_ans_{i}",
                             use_container_width=True):
                    with st.spinner("Generating university-style model answer…"):
                        answer = call_bedrock(
                            MODEL_ANSWER_SYSTEM + f"\nUniversity: {uni}",
                            f"Question ({marks} marks): {qtext}\nTopic: {topic}",
                            use_sonnet=False,
                            max_tokens=1000,
                        )
                    st.markdown(f"""
<div style="background:rgba(255,107,26,0.04);border:1px solid rgba(255,107,26,0.15);
border-left:3px solid #4AB7E0;border-radius:12px;padding:1.25rem;margin-top:0.75rem;
font-size:0.875rem;line-height:1.8;">
<strong style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
color:#4AB7E0;">Model Answer ({marks} marks)</strong><br><br>
{answer}
</div>
""", unsafe_allow_html=True)
                    pyq_count = st.session_state.get("pyq_attempted", 0) + 1
                    st.session_state.pyq_attempted = pyq_count
                    add_xp(5, "PYQ model answer viewed")
                    log_interaction("pyq", topic, correct=None)
                    save_user_progress()

            with col_attempt:
                attempt_key = f"pyq_attempt_txt_{i}"
                sub_key = f"pyq_sub_{i}"
                user_ans = st.text_area(
                    "Your attempt",
                    placeholder="Write your answer here...",
                    key=attempt_key,
                    height=80,
                    label_visibility="collapsed",
                )
                if st.button("Submit →", key=sub_key, use_container_width=True):
                    if user_ans.strip():
                        with st.spinner("Evaluating…"):
                            eval_system = f"""You are a university examiner evaluating a student answer.
University: {uni}. Subject: {q.get('topic','')}.
Return JSON: {{"score": N, "max": {marks}, "grade": "...", "feedback": "...", "missing": ["..."]}}"""
                            result = call_bedrock_json(
                                eval_system,
                                f"Question ({marks} marks): {qtext}\nStudent answer: {user_ans}",
                                use_sonnet=False,
                                max_tokens=500,
                            )
                        if result:
                            score = result.get("score", 0)
                            max_m = result.get("max", marks)
                            grade = result.get("grade", "")
                            feedback = result.get("feedback", "")
                            missing = result.get("missing", [])
                            pct = int(score / max_m * 100) if max_m else 0
                            color = "#00E676" if pct >= 70 else "#FFD166"
                            st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.09);
border-radius:12px;padding:1rem;margin-top:0.5rem;">
  <div style="font-size:1.5rem;font-family:JetBrains Mono,monospace;color:{color};">
    {score}/{max_m} <span style="font-size:0.8rem;color:#3A5A7A;">{grade}</span>
  </div>
  <div style="font-size:0.82rem;margin:0.5rem 0;color:#5A7FA8;">{feedback}</div>
  {f'<div style="font-size:0.78rem;color:#FFD166;">Missing: {", ".join(missing[:3])}</div>' if missing else ""}
</div>
""", unsafe_allow_html=True)
                            pyq_count = st.session_state.get("pyq_attempted", 0) + 1
                            st.session_state.pyq_attempted = pyq_count
                            add_xp(8, "PYQ attempted")
                            save_user_progress()


def _render_frequency():
    bank = st.session_state.get("pyq_bank", [])

    if not bank:
        st.info("Add questions to your PYQ bank first to see frequency analysis.")
        return

    st.markdown('<span class="sec-label">📊 Topic Frequency Analysis</span>',
                unsafe_allow_html=True)
    st.markdown("""
<div style="font-size:0.825rem;color:#3A5A7A;margin-bottom:1.25rem;">
  Topics that appear most often in your PYQ bank — likely to appear in your exam.
</div>
""", unsafe_allow_html=True)

    # Count by topic
    topic_counts = {}
    marks_map = {}
    for q in bank:
        t = q.get("topic", "Unknown")
        m = q.get("marks", 0)
        topic_counts[t] = topic_counts.get(t, 0) + 1
        marks_map[t] = marks_map.get(t, 0) + int(m)

    sorted_topics = sorted(topic_counts.items(), key=lambda x: x[1], reverse=True)
    max_count = max(c for _, c in sorted_topics) if sorted_topics else 1

    for topic, count in sorted_topics:
        pct = int(count / max_count * 100)
        likelihood = "🔴 High" if count >= 3 else ("🟡 Medium" if count >= 2 else "⚪ Low")
        total_marks = marks_map.get(topic, 0)
        st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.08);
border-radius:12px;padding:0.875rem 1.1rem;margin-bottom:0.625rem;">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:6px;">
    <div>
      <span style="font-size:0.875rem;font-weight:500;">{topic}</span>
      <span style="font-size:0.68rem;color:#3A5A7A;margin-left:8px;">
        {count} question{'s' if count != 1 else ''} · {total_marks} total marks
      </span>
    </div>
    <span style="font-size:0.72rem;">{likelihood}</span>
  </div>
  <div style="height:4px;background:rgba(255,255,255,0.05);border-radius:2px;">
    <div style="width:{pct}%;height:100%;
    background:{'#FF4757' if count >= 3 else ('#FFD166' if count >= 2 else '#2A3A50')};
    border-radius:2px;"></div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Marks distribution
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<span class="sec-label">Marks Distribution</span>',
                unsafe_allow_html=True)
    marks_dist = {}
    for q in bank:
        m = str(q.get("marks", "?"))
        marks_dist[m] = marks_dist.get(m, 0) + 1

    m_cols = st.columns(len(marks_dist))
    for col, (marks, cnt) in zip(m_cols, sorted(marks_dist.items())):
        with col:
            st.metric(f"{marks}-mark Qs", cnt)


def _render_model_answers():
    st.markdown("""
<div style="font-size:0.825rem;color:#3A5A7A;margin-bottom:1.25rem;">
  Generate a university-style model answer for any question.
</div>
""", unsafe_allow_html=True)

    uni  = st.session_state.get("university", "")
    subj = st.session_state.get("subject", "")

    col1, col2 = st.columns([1, 3])
    with col1:
        marks = st.selectbox("Marks", [2, 5, 10, 15], key="ma_marks")
    with col2:
        question = st.text_area(
            "Your Question",
            placeholder="Type any exam question here...",
            key="ma_question",
            height=100,
            label_visibility="collapsed",
        )

    topic = st.text_input("Topic (optional)", placeholder="e.g. Virtualization", key="ma_topic")

    if st.button("Generate Model Answer →", key="ma_generate",
                 use_container_width=True):
        if question.strip():
            with st.spinner(f"Generating {marks}-mark model answer in {uni} style…"):
                answer = call_bedrock(
                    MODEL_ANSWER_SYSTEM + f"\nUniversity: {uni}\nSubject: {subj}",
                    f"Question ({marks} marks): {question}\nTopic: {topic or subj}",
                    use_sonnet=False,
                    max_tokens=1200,
                )
            if not answer.startswith("ERROR"):
                st.markdown(f"""
<div style="background:rgba(255,107,26,0.04);border:1px solid rgba(255,107,26,0.15);
border-left:3px solid #4AB7E0;border-radius:14px;padding:1.5rem;
font-size:0.9rem;line-height:1.9;margin-top:1rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#4AB7E0;margin-bottom:0.875rem;">
    Model Answer · {marks} marks · {uni} Style
  </div>
  {answer}
</div>
""", unsafe_allow_html=True)
                add_xp(5, "model answer generated")
                save_user_progress()
            else:
                st.error(answer)
        else:
            st.warning("Please enter a question.")
