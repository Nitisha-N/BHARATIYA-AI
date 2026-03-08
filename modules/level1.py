"""BharatiyaAI Mentor — Level 1: Learn"""

import streamlit as st
from utils.ai import (
    call_bedrock, call_bedrock_json, call_bedrock_stream,
    GUIDED_DISCOVERY_SYSTEM, VISUAL_SYSTEM, SUMMARY_SYSTEM,
    FLASHCARD_SYSTEM, DOUBT_SOLVER_SYSTEM, SPACED_REPETITION_SYSTEM
)
from utils.session import (
    add_topic_studied, flag_weak, flag_strong,
    add_concept_learned, log_interaction, get_weak_context
)
from utils.auth import add_xp, save_user_progress
from utils.pdf_reader import build_context

STYLE_META = {
    "guided":    ("🧭", "Guided Discovery"),
    "visual":    ("🎨", "Visual & Analogy"),
    "summary":   ("📋", "Quick Summary"),
    "flashcard": ("🃏", "Flashcard Mode"),
}

SYSTEM_MAP = {
    "guided":    GUIDED_DISCOVERY_SYSTEM,
    "visual":    VISUAL_SYSTEM,
    "summary":   SUMMARY_SYSTEM,
    "flashcard": FLASHCARD_SYSTEM,
}


def _build_student_context() -> str:
    subject  = st.session_state.get("subject", "")
    uni      = st.session_state.get("university", "")
    style_id = st.session_state.get("learning_style", "guided")
    style_lbl = STYLE_META.get(style_id, ("", "Guided"))[1]
    weak_ctx = get_weak_context()
    uploaded = st.session_state.get("uploaded_text", "")
    excerpt  = uploaded[:1500] if uploaded else ""

    ctx = f"""Student profile:
- Name: {st.session_state.get('user_name', 'Student')}
- Subject: {subject}
- University: {uni}
- Learning style preference: {style_lbl}
{weak_ctx}
{f"Study material excerpt:{chr(10)}{excerpt}" if excerpt else ""}"""
    return ctx


def render_level1():
    st.markdown("""
<div class="page-title">📚 Level 1 — Learn</div>
<div class="page-subtitle">Build conceptual clarity with your chosen learning style</div>
""", unsafe_allow_html=True)

    # ── STYLE SELECTOR ──
    style_id = st.session_state.get("learning_style", "guided")
    icon, style_label = STYLE_META.get(style_id, ("🧭", "Guided Discovery"))

    st.markdown(f"""
<div style="background:rgba(255,107,26,0.06);border:1px solid rgba(255,107,26,0.15);
border-radius:12px;padding:0.75rem 1.1rem;margin-bottom:1rem;
display:flex;align-items:center;justify-content:space-between;">
  <div>
    <span style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.1em;
    color:#4AB7E0;font-weight:700;">Active Mode</span><br>
    <span style="font-size:0.9rem;font-weight:600;">{icon} {style_label}</span>
  </div>
  <div style="font-size:0.75rem;color:#3A5A7A;">Shapes every response</div>
</div>
""", unsafe_allow_html=True)

    change_style = st.expander("↺ Change learning style")
    with change_style:
        cols = st.columns(4)
        for col, (sid, (ic, lbl)) in zip(cols, STYLE_META.items()):
            with col:
                if st.button(f"{ic} {lbl}", key=f"style_sw_{sid}",
                             use_container_width=True):
                    st.session_state.learning_style = sid
                    st.session_state.last_explanation = None
                    st.session_state.fc_cards = []
                    st.rerun()

    st.markdown("---")

    # ── TABS ──
    tab_learn, tab_doubt = st.tabs(["⚡ Learn", "💬 Live Doubt Solver"])

    with tab_learn:
        _render_learn_tab(style_id)

    with tab_doubt:
        _render_doubt_tab()


def _render_learn_tab(style_id: str):
    curriculum = st.session_state.get("curriculum", {})
    weeks = curriculum.get("weeks", []) if curriculum else []
    active_week = st.session_state.get("active_week", 0)

    # Topic input
    col_topic, col_btn = st.columns([4, 1])
    with col_topic:
        # Pre-fill from current week topics
        default_topic = ""
        if weeks and active_week < len(weeks):
            week_topics = weeks[active_week].get("topics", [])
            if week_topics:
                default_topic = week_topics[0]

        topic = st.text_input(
            "What do you want to learn?",
            placeholder="e.g. Virtualization, OSI Model, Deadlock...",
            value=st.session_state.get("last_topic", default_topic),
            key="l1_topic_input",
        )
    with col_btn:
        st.markdown("<br>", unsafe_allow_html=True)
        generate = st.button("Generate ⚡", key="l1_generate",
                             use_container_width=True)

    # ── SPACED REPETITION CHECK ──
    due = st.session_state.get("spaced_rep_due", [])
    if due:
        rep_topic = due[0]
        st.markdown(f"""
<div style="background:rgba(255,209,102,0.06);border:1px solid rgba(255,209,102,0.2);
border-radius:12px;padding:0.875rem 1rem;margin-bottom:1rem;">
  <div style="font-size:0.62rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#FFD166;font-weight:700;margin-bottom:4px;">🔄 Spaced Repetition Check</div>
  <div style="font-size:0.85rem;color:#F0F7F2;">
    Do you still remember: <strong>{rep_topic}</strong>?
  </div>
</div>
""", unsafe_allow_html=True)
        rc1, rc2, rc3 = st.columns([2, 1, 1])
        with rc1:
            recall_answer = st.text_input(
                "Your recall answer",
                placeholder="Explain it briefly...",
                key="recall_answer",
                label_visibility="collapsed",
            )
        with rc2:
            if st.button("✓ I Remember", key="recall_yes"):
                flag_strong(rep_topic)
                due.pop(0)
                st.session_state.spaced_rep_due = due
                add_xp(15, "spaced repetition correct")
                log_interaction("recall", rep_topic, correct=True)
                st.success(f"+15 XP — Great recall of {rep_topic}!")
                st.rerun()
        with rc3:
            if st.button("✗ Forgot", key="recall_no"):
                flag_weak(rep_topic)
                due.pop(0)
                st.session_state.spaced_rep_due = due
                log_interaction("recall", rep_topic, correct=False)
                st.warning(f"{rep_topic} added to revision queue.")
                st.rerun()

    # ── GENERATE ──
    if generate and topic.strip():
        st.session_state.last_topic = topic.strip()
        add_topic_studied(topic.strip())
        log_interaction("explain", topic.strip())

        student_ctx = _build_student_context()
        system = SYSTEM_MAP.get(style_id, GUIDED_DISCOVERY_SYSTEM)
        full_system = system + f"\n\n{student_ctx}"

        if style_id == "flashcard":
            # JSON mode for flashcards
            with st.spinner("Generating flashcards…"):
                cards = call_bedrock_json(
                    full_system,
                    f"Generate flashcards for: {topic}",
                    use_sonnet=False,
                    max_tokens=1200,
                )
                if cards and isinstance(cards, list):
                    st.session_state.fc_cards = cards
                    st.session_state.fc_index = 0
                    st.session_state.fc_known = []
                    st.session_state.fc_flipped = False
                    st.session_state.last_explanation = "__flashcards__"
                else:
                    st.error("Could not generate flashcards. Try again.")
        else:
            # Streaming text response
            st.session_state.last_explanation = None
            box = st.empty()
            full_text = ""
            with st.spinner("BharatiyaAI is thinking…"):
                for chunk in call_bedrock_stream(
                    full_system,
                    f"Topic: {topic}\nBegin.",
                    use_sonnet=False,
                    max_tokens=900,
                ):
                    if chunk.startswith("ERROR:"):
                        st.error(f"Bedrock error: {chunk}")
                        break
                    full_text += chunk
                    box.markdown(f"""
<div class="baim-card baim-card-orange animate-fade" style="line-height:1.9;font-size:0.9rem;">
{full_text}▊
</div>
""", unsafe_allow_html=True)

            if full_text and not full_text.startswith("ERROR"):
                st.session_state.last_explanation = full_text
                add_concept_learned(topic.strip())
                add_xp(10, "concept learned")
                save_user_progress()

    # ── SHOW EXISTING EXPLANATION ──
    explanation = st.session_state.get("last_explanation")
    topic_shown = st.session_state.get("last_topic", "")

    if explanation == "__flashcards__":
        _render_flashcards(topic_shown)
    elif explanation:
        st.markdown(f"""
<div class="baim-card baim-card-orange" style="line-height:1.9;font-size:0.9rem;">
{explanation}
</div>
""", unsafe_allow_html=True)

        # Feedback buttons
        if topic_shown:
            col_w, col_s, col_more = st.columns([1, 1, 3])
            with col_w:
                if st.button("⚑ Flag as Weak", key="flag_weak_btn"):
                    flag_weak(topic_shown)
                    log_interaction("flag", topic_shown, correct=False)
                    st.warning(f"'{topic_shown}' added to revision queue.")
            with col_s:
                if st.button("✓ Got It!", key="flag_strong_btn"):
                    flag_strong(topic_shown)
                    log_interaction("flag", topic_shown, correct=True)
                    add_xp(5, "concept confirmed")
                    st.success(f"+5 XP — '{topic_shown}' marked as understood!")
            with col_more:
                if style_id == "guided":
                    followup = st.text_input(
                        "Your answer / follow-up",
                        placeholder="Type your response to the AI's question...",
                        key="l1_followup",
                    )
                    if st.button("Send →", key="l1_send_followup"):
                        if followup.strip():
                            student_ctx = _build_student_context()
                            system = SYSTEM_MAP[style_id] + f"\n\n{student_ctx}"
                            history_context = f"Previous exchange:\n{explanation}\n\nStudent's response: {followup}"
                            with st.spinner("…"):
                                resp = call_bedrock(
                                    system, history_context,
                                    use_sonnet=False, max_tokens=600
                                )
                            if not resp.startswith("ERROR"):
                                st.session_state.last_explanation = explanation + f"\n\n---\n\n**You:** {followup}\n\n**BharatiyaAI:** {resp}"
                                st.rerun()

    # ── WEEK TOPICS ──
    if weeks and active_week < len(weeks):
        week = weeks[active_week]
        wk_topics = week.get("topics", [])
        if wk_topics:
            st.markdown("---")
            st.markdown(
                f'<span class="sec-label">📅 {week.get("name","Current Week")} — Topics</span>',
                unsafe_allow_html=True
            )
            cols = st.columns(min(len(wk_topics), 4))
            for col, t in zip(cols, wk_topics):
                with col:
                    tc = st.session_state.get("topic_confidence", {})
                    conf = tc.get(t, {}).get("score", None)
                    badge = f' <span style="color:#00E676;font-size:0.65rem;">{int(conf)}%</span>' if conf else ""
                    if st.button(f"📖 {t}{badge}", key=f"wk_topic_{t}",
                                 use_container_width=True):
                        st.session_state.last_topic = t
                        st.session_state.last_explanation = None
                        st.session_state.fc_cards = []
                        st.rerun()


def _render_flashcards(topic: str):
    cards = st.session_state.get("fc_cards", [])
    idx = st.session_state.get("fc_index", 0)
    known = st.session_state.get("fc_known", [])
    flipped = st.session_state.get("fc_flipped", False)

    if not cards:
        return

    # Completed
    if idx >= len(cards):
        correct_count = sum(1 for k in known if k)
        pct = int(correct_count / len(cards) * 100)
        st.markdown(f"""
<div style="background:rgba(30,41,59,0.95);border:1px solid rgba(74,183,224,0.18);
border-radius:20px;padding:2.5rem;text-align:center;">
  <div style="font-size:2.5rem;margin-bottom:0.75rem;">
    {"🎉" if pct >= 70 else "📚"}
  </div>
  <div style="font-family:'Space Grotesk',sans-serif;font-size:1.5rem;margin-bottom:0.5rem;">
    Flashcard Session Complete
  </div>
  <div style="font-size:3rem;font-family:JetBrains Mono,monospace;color:#6ECAEC;margin:0.5rem 0;">
    {correct_count}/{len(cards)}
  </div>
  <div style="color:#3A5A7A;margin-bottom:1.5rem;">
    Score: {pct}% · {topic}
  </div>
</div>
""", unsafe_allow_html=True)
        if pct >= 70:
            flag_strong(topic)
            add_xp(25, "flashcard session")
            st.success(f"+25 XP — Great session on {topic}!")
        else:
            flag_weak(topic)
            st.warning(f"'{topic}' needs more practice. Added to revision queue.")
        log_interaction("flashcard", topic, correct=(pct >= 70))
        save_user_progress()

        c1, c2 = st.columns(2)
        with c1:
            if st.button("🔄 Retry", key="fc_retry", use_container_width=True):
                st.session_state.fc_index = 0
                st.session_state.fc_known = []
                st.session_state.fc_flipped = False
                st.rerun()
        with c2:
            if st.button("✓ Done", key="fc_done", use_container_width=True):
                st.session_state.last_explanation = None
                st.session_state.fc_cards = []
                st.rerun()
        return

    card = cards[idx]
    progress_pct = int(idx / len(cards) * 100)

    st.markdown(f"""
<div style="display:flex;align-items:center;justify-content:space-between;margin-bottom:0.75rem;">
  <div style="font-size:0.75rem;color:#3A5A7A;">Card {idx+1} of {len(cards)} · {topic}</div>
  <div style="font-size:0.7rem;font-family:JetBrains Mono,monospace;color:#6ECAEC;">
    ✓ {sum(1 for k in known if k)} known
  </div>
</div>
<div style="height:3px;background:rgba(74,183,224,0.08);border-radius:2px;margin-bottom:1.25rem;">
  <div style="width:{progress_pct}%;height:100%;
  background:linear-gradient(90deg,#4AB7E0,#FFD166);border-radius:2px;"></div>
</div>
""", unsafe_allow_html=True)

    # Card display
    diff_color = {"easy": "#00E676", "medium": "#FFD166", "hard": "#FF4757"}.get(
        card.get("difficulty", "medium"), "#FFD166"
    )
    if not flipped:
        st.markdown(f"""
<div class="fc-card animate-fade">
  <div style="font-size:0.62rem;color:{diff_color};text-transform:uppercase;
  letter-spacing:0.1em;margin-bottom:1rem;">{card.get('difficulty','medium').upper()}</div>
  <div style="font-size:1.05rem;font-weight:600;line-height:1.6;color:#F0F7F2;">
    {card.get('front', '')}
  </div>
  <div style="font-size:0.72rem;color:#2A3A50;margin-top:1.25rem;">
    Tap "Reveal Answer" when ready
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("👁 Reveal Answer", key="fc_flip", use_container_width=True):
            st.session_state.fc_flipped = True
            st.rerun()
    else:
        st.markdown(f"""
<div class="fc-card fc-card-back animate-fade">
  <div style="font-size:0.62rem;color:#4AB7E0;text-transform:uppercase;
  letter-spacing:0.1em;margin-bottom:1rem;">ANSWER</div>
  <div style="font-size:0.95rem;line-height:1.7;color:#F0F7F2;">
    {card.get('back', '')}
  </div>
</div>
""", unsafe_allow_html=True)

        c1, c2 = st.columns(2)
        with c1:
            if st.button("✓ I Knew This", key="fc_known_btn",
                         use_container_width=True):
                known.append(True)
                st.session_state.fc_known = known
                st.session_state.fc_index = idx + 1
                st.session_state.fc_flipped = False
                add_xp(5, "flashcard known")
                st.rerun()
        with c2:
            if st.button("✗ Still Learning", key="fc_unknown_btn",
                         use_container_width=True):
                known.append(False)
                st.session_state.fc_known = known
                st.session_state.fc_index = idx + 1
                st.session_state.fc_flipped = False
                st.rerun()


def _render_doubt_tab():
    st.markdown("""
<div style="margin-bottom:1rem;">
  <div style="font-size:0.875rem;color:#3A5A7A;line-height:1.7;">
    Ask any doubt about your subject. BharatiyaAI knows your syllabus,
    your weak areas, and your uploaded material.
  </div>
</div>
""", unsafe_allow_html=True)

    history = st.session_state.get("doubt_history", [])

    # ── RENDER CHAT HISTORY ──
    for msg in history:
        role = msg.get("role", "user")
        content = msg.get("content", "")
        if role == "user":
            st.markdown(
                f'<div class="chat-user">{content}</div>',
                unsafe_allow_html=True
            )
        else:
            st.markdown(
                f'<div class="chat-ai">{content}</div>',
                unsafe_allow_html=True
            )

    # ── REVISION QUEUE SHORTCUTS ──
    rq = st.session_state.get("revision_queue", [])
    if rq and not history:
        st.markdown("""
<div style="font-size:0.72rem;color:#3A5A7A;margin-bottom:0.5rem;">
  Quick revision — tap a weak topic:
</div>
""", unsafe_allow_html=True)
        cols = st.columns(min(len(rq), 4))
        for col, t in zip(cols, rq[:4]):
            with col:
                if st.button(f"⚑ {t[:15]}", key=f"rq_doubt_{t}",
                             use_container_width=True):
                    st.session_state.doubt_history = [{
                        "role": "user",
                        "content": f"Please revise {t} for me — I'm struggling with this."
                    }]
                    st.rerun()

    # ── INPUT ──
    col_in, col_send = st.columns([5, 1])
    with col_in:
        user_input = st.text_input(
            "Your doubt",
            placeholder="Ask anything about your subject...",
            key="doubt_input",
            label_visibility="collapsed",
        )
    with col_send:
        send = st.button("Send →", key="doubt_send", use_container_width=True)

    if send and user_input.strip():
        history.append({"role": "user", "content": user_input.strip()})
        st.session_state.doubt_history = history
        log_interaction("doubt", user_input.strip()[:30])

        # Build rich context
        student_ctx = _build_student_context()
        weak_ctx = get_weak_context()
        system = f"{DOUBT_SOLVER_SYSTEM}\n\n{student_ctx}"

        # Include last 3 exchanges
        convo_hist = []
        for msg in history[-6:]:
            convo_hist.append(msg["content"])
        convo_str = "\n\n".join(
            f"{'Student' if i%2==0 else 'BharatiyaAI'}: {c}"
            for i, c in enumerate(convo_hist)
        )

        with st.spinner("BharatiyaAI is thinking…"):
            resp = call_bedrock(
                system,
                f"Conversation:\n{convo_str}",
                use_sonnet=False,
                max_tokens=700,
                use_cache=False,
            )

        if not resp.startswith("ERROR"):
            history.append({"role": "assistant", "content": resp})
            st.session_state.doubt_history = history
            add_xp(3, "doubt asked")
        else:
            st.error(f"Error: {resp}")
        st.rerun()

    if history:
        if st.button("🗑 Clear Chat", key="doubt_clear"):
            st.session_state.doubt_history = []
            st.rerun()
