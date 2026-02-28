"""BharatiyaAI × LearnOS — Learn & Live Doubt Solver"""

import streamlit as st
from utils.ai import call_claude, call_claude_json, STYLE_SYSTEM, DOUBT_SOLVER_SYSTEM
from utils.session import (
    add_topic_studied, set_tab, get_weak_context_string,
    get_recommended_mode, log_interaction
)
from utils.pdf_reader import extract_text, build_context_block


def _get_week_context():
    curriculum = st.session_state.get("curriculum", {})
    weeks = curriculum.get("weeks", [])
    idx = st.session_state.get("active_week", 0)
    if idx < len(weeks):
        w = weeks[idx]
        return w.get("name", ""), w.get("topics", []), w.get("mode_tip", "")
    return "", [], ""


def _build_doubt_system(style: str) -> str:
    style_map = {
        "stepbystep": "structured step-by-step explanations",
        "flashcard":  "quick conceptual answers with key terms highlighted",
        "summary":    "concise, bullet-rich responses",
        "visual":     "analogies, diagrams, and mental models",
    }
    style_desc = style_map.get(style, "clear explanations")
    weak_ctx = get_weak_context_string()
    topics_studied = st.session_state.get("topics_studied", [])
    subject = st.session_state.get("subject", "")
    name = st.session_state.get("student_name", "the student")

    system = DOUBT_SOLVER_SYSTEM
    system += f"\n\nStudent profile:\n"
    system += f"- Name: {name}\n- Subject: {subject}\n"
    system += f"- Preferred style: {style_desc}\n"
    if topics_studied:
        system += f"- Topics studied: {', '.join(topics_studied)}\n"
    if weak_ctx:
        system += f"\n{weak_ctx}\n"
    file_text = st.session_state.get("uploaded_text", "")
    if file_text and not file_text.startswith("[PDF"):
        system += f"\nUploaded material (first 2000 chars):\n{file_text[:2000]}"
    return system


def render_learn():
    week_name, week_topics, mode_tip = _get_week_context()
    style = st.session_state.get("learning_style", "stepbystep")

    st.markdown(f"""
<div style="margin-bottom:1.25rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.8rem;font-weight:600;">⚡ Learn & Doubt Solver</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">
    {week_name} · Live contextual tutor · Weak-topic aware
  </div>
</div>
""", unsafe_allow_html=True)

    # ── UPLOAD ──
    with st.expander("📂 Upload / Change Study Material",
                     expanded=not st.session_state.get("uploaded_filename")):
        uploaded = st.file_uploader("PDF or TXT", type=["pdf", "txt"], key="learn_upload")
        if uploaded:
            text = extract_text(uploaded)
            st.session_state.uploaded_filename = uploaded.name
            st.session_state.uploaded_text = text
            st.success(f"✓ Loaded: {uploaded.name}")

    file_name = st.session_state.get("uploaded_filename", "")
    if file_name:
        st.markdown(
            f'<div style="display:inline-flex;align-items:center;gap:6px;'
            f'background:rgba(255,107,43,0.1);border:1px solid rgba(255,107,43,0.2);'
            f'border-radius:8px;padding:4px 12px;font-size:0.78rem;color:#FF8F5A;margin-bottom:1rem;">'
            f'📄 {file_name}</div>',
            unsafe_allow_html=True
        )

    # ── ADAPTIVE BANNER ──
    revision_queue = st.session_state.get("revision_queue", [])
    adaptation_triggered = st.session_state.get("adaptation_triggered", False)
    if adaptation_triggered and revision_queue:
        top_rev = revision_queue[0]
        rec_mode = get_recommended_mode(top_rev)
        mode_labels = {"stepbystep": "Step-by-Step 🪜", "visual": "Visual 🎨",
                       "flashcard": "Flashcard 🃏", "summary": "Summary 📋"}
        st.markdown(f"""
<div style="background:rgba(74,144,217,0.07);border:1px solid rgba(74,144,217,0.22);
border-radius:12px;padding:0.875rem 1rem;margin-bottom:1rem;">
  <div style="font-size:0.68rem;font-weight:600;color:#4A90D9;margin-bottom:2px;">🔄 Adaptive Suggestion</div>
  <div style="font-size:0.8rem;color:#8892BB;">
    Based on your performance, try <strong style="color:#E8EDF8;">{mode_labels.get(rec_mode)}</strong>
    for <strong style="color:#F5C842;">"{top_rev}"</strong> — it needs more attention.
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button(f"Switch to {mode_labels.get(rec_mode)} for '{top_rev}'",
                     key="adapt_switch"):
            st.session_state.learning_style = rec_mode
            st.session_state.adaptation_triggered = False
            st.rerun()

    # ── MODE SELECTOR ──
    st.markdown('<span class="sec-label">Learning Mode</span>', unsafe_allow_html=True)
    style_opts = {
        "stepbystep": "🪜 Step-by-Step",
        "flashcard":  "🃏 Flashcard",
        "summary":    "📋 Quick Summary",
        "visual":     "🎨 Visual & Analogy",
    }
    mode_cols = st.columns(4)
    for col, (sid, slabel) in zip(mode_cols, style_opts.items()):
        with col:
            is_sel = style == sid
            if st.button(slabel, key=f"mode_{sid}", use_container_width=True,
                         type="primary" if is_sel else "secondary"):
                st.session_state.learning_style = sid
                st.session_state.last_explanation = None
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)

    if mode_tip:
        st.markdown(
            f'<div style="background:rgba(245,200,66,0.07);border:1px solid rgba(245,200,66,0.15);'
            f'border-radius:10px;padding:0.75rem 1rem;font-size:0.8rem;color:#F5C842;margin-bottom:1rem;">'
            f'💡 {mode_tip}</div>', unsafe_allow_html=True
        )

    # ── TWO TABS ──
    explain_tab, doubt_tab = st.tabs(["📚 Get Explanation", "🔴 Live Doubt Solver"])

    # ═══════════════════════════════
    # TAB 1 — EXPLAIN
    # ═══════════════════════════════
    with explain_tab:
        if week_topics:
            chips = "".join(
                f'<span style="display:inline-flex;font-size:0.75rem;padding:3px 10px;'
                f'border-radius:20px;margin:2px;background:rgba(255,107,43,0.1);'
                f'border:1px solid rgba(255,107,43,0.2);color:#FF8F5A;">{t}</span>'
                for t in week_topics
            )
            st.markdown(f'<div style="margin-bottom:0.875rem;">{chips}</div>',
                        unsafe_allow_html=True)

        topic = st.text_input(
            "",
            placeholder="e.g. Explain Newton's Third Law, Summarise photosynthesis…",
            key="learn_topic", label_visibility="collapsed",
        )
        col_ask, col_clear = st.columns([4, 1])
        with col_ask:
            ask_btn = st.button("⚡ Explain This", key="learn_ask",
                                disabled=not topic.strip(), use_container_width=True)
        with col_clear:
            if st.button("Clear", key="learn_clear"):
                st.session_state.last_explanation = None
                st.rerun()

        if ask_btn and topic.strip():
            current_style = st.session_state.get("learning_style", "stepbystep")
            system = STYLE_SYSTEM[current_style]
            weak_ctx = get_weak_context_string()
            if weak_ctx:
                system = system + f"\n\n{weak_ctx}"
            context = build_context_block(st.session_state.get("uploaded_text", ""), topic)

            with st.spinner(f"BharatiyaAI thinking in {style_opts.get(current_style)} mode…"):
                if current_style == "flashcard":
                    data = call_claude_json(system, context, max_tokens=1200)
                    if data and isinstance(data, list):
                        st.session_state.fc_cards = data
                        st.session_state.fc_index = 0
                        st.session_state.fc_known = []
                        st.session_state.fc_flipped = False
                        st.session_state.last_explanation = None
                        add_topic_studied(topic)
                        st.session_state.last_topic = topic
                        log_interaction("flashcard", topic)
                        set_tab("flashcards")
                        st.rerun()
                else:
                    text = call_claude(system, context, max_tokens=1200)
                    if text.startswith("ERROR:AUTH"):
                        st.error("Invalid API key. Add ANTHROPIC_API_KEY to .streamlit/secrets.toml")
                    elif text.startswith("ERROR:"):
                        st.error(f"API Error: {text}")
                    else:
                        st.session_state.last_explanation = {
                            "text": text, "style": current_style, "topic": topic
                        }
                        st.session_state.last_topic = topic
                        add_topic_studied(topic)
                        log_interaction("explain", topic)

        expl = st.session_state.get("last_explanation")
        if expl:
            _render_explanation(expl)

    # ═══════════════════════════════
    # TAB 2 — LIVE DOUBT SOLVER
    # ═══════════════════════════════
    with doubt_tab:
        _render_doubt_chat(style, style_opts)


def _render_explanation(expl: dict):
    expl_style = expl.get("style", "stepbystep")
    topic_label = expl.get("topic", "")
    style_config = {
        "summary":    ("#1FAD0F", "rgba(19,136,8,0.04)",    "rgba(19,136,8,0.15)",    "📋 Quick Summary"),
        "visual":     ("#4A90D9", "rgba(74,144,217,0.04)",  "rgba(74,144,217,0.15)",  "🎨 Visual"),
        "stepbystep": ("#FF6B2B", "rgba(255,107,43,0.03)",  "rgba(255,107,43,0.12)",  "🪜 Step-by-Step"),
    }
    color, bg, border_col, label = style_config.get(
        expl_style, ("#FF6B2B", "rgba(255,107,43,0.03)", "rgba(255,107,43,0.12)", "Explanation")
    )
    st.markdown(f"""
<div style="background:{bg};border:1px solid {border_col};
border-left:3px solid {color};border-radius:14px;padding:1.5rem;margin-top:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:{color};margin-bottom:1rem;">{label} · {topic_label}</div>
  <div style="font-size:0.875rem;line-height:1.9;white-space:pre-wrap;">{expl['text']}</div>
</div>
""", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("✏️ Practice Questions", key="learn_to_practice"):
            set_tab("practice")
            st.rerun()
    with c2:
        if st.button("🗓️ Curriculum", key="learn_to_curr"):
            set_tab("curriculum")
            st.rerun()
    with c3:
        if st.button("Ask something else", key="learn_new"):
            st.session_state.last_explanation = None
            st.rerun()


def _render_doubt_chat(style: str, style_opts: dict):
    doubt_history = st.session_state.get("doubt_history", [])
    weak = st.session_state.get("weak_concepts", [])

    st.markdown(f"""
<div style="background:rgba(255,107,43,0.04);border:1px solid rgba(255,107,43,0.12);
border-radius:12px;padding:0.875rem 1rem;margin-bottom:1rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;
  color:#FF6B2B;margin-bottom:4px;">🔴 Live Doubt Solver — Active</div>
  <div style="font-size:0.78rem;color:#8892BB;line-height:1.5;">
    Context-aware · Uses your PDF · Knows your weak areas ·
    Mode: <strong style="color:#E8EDF8;">{style_opts.get(style, style)}</strong>
    {"· ⚑ " + ", ".join(weak[:3]) + ("…" if len(weak) > 3 else "") if weak else ""}
  </div>
</div>
""", unsafe_allow_html=True)

    # Chat history
    if not doubt_history:
        st.markdown("""
<div style="text-align:center;padding:2rem;color:#6B7A99;font-size:0.875rem;">
  <div style="font-size:1.5rem;margin-bottom:0.5rem;">💬</div>
  Ask any doubt. BharatiyaAI knows your weak areas and study material.
</div>
""", unsafe_allow_html=True)
    else:
        for msg in doubt_history:
            if msg["role"] == "user":
                st.markdown(f"""
<div style="display:flex;justify-content:flex-end;margin-bottom:0.75rem;">
  <div style="background:rgba(255,107,43,0.12);border:1px solid rgba(255,107,43,0.2);
  border-radius:14px 14px 4px 14px;padding:0.75rem 1rem;max-width:80%;font-size:0.875rem;">
    {msg['text']}
  </div>
</div>
""", unsafe_allow_html=True)
            else:
                dot_colors = {"stepbystep": "#FF6B2B", "summary": "#1FAD0F",
                              "visual": "#4A90D9", "flashcard": "#F5C842"}
                dot = dot_colors.get(msg.get("style", "stepbystep"), "#FF6B2B")
                st.markdown(f"""
<div style="display:flex;justify-content:flex-start;margin-bottom:0.75rem;">
  <div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.08);
  border-radius:4px 14px 14px 14px;padding:0.875rem 1rem;max-width:85%;">
    <div style="font-size:0.65rem;color:{dot};text-transform:uppercase;
    letter-spacing:0.08em;margin-bottom:0.5rem;">● BharatiyaAI</div>
    <div style="font-size:0.875rem;line-height:1.8;white-space:pre-wrap;">{msg['text']}</div>
  </div>
</div>
""", unsafe_allow_html=True)

    # Input row
    doubt_input = st.text_input(
        "",
        placeholder="Type your doubt… e.g. 'Why does entropy always increase?' or 'Explain recursion differently'",
        key="doubt_input", label_visibility="collapsed",
    )
    col_send, col_clear = st.columns([5, 1])
    with col_send:
        send_btn = st.button("Send →", key="doubt_send",
                             disabled=not doubt_input.strip(), use_container_width=True)
    with col_clear:
        if st.button("Clear Chat", key="doubt_clear"):
            st.session_state.doubt_history = []
            st.rerun()

    if send_btn and doubt_input.strip():
        current_style = st.session_state.get("learning_style", "stepbystep")
        system = _build_doubt_system(current_style)
        history = st.session_state.get("doubt_history", [])
        # Build multi-turn messages
        messages = []
        for h in history[-6:]:
            role = "user" if h["role"] == "user" else "assistant"
            messages.append({"role": role, "content": h["text"]})
        messages.append({"role": "user", "content": doubt_input.strip()})
        history.append({"role": "user", "text": doubt_input.strip()})

        with st.spinner("BharatiyaAI solving your doubt…"):
            try:
                from utils.ai import get_client
                client = get_client()
                response = client.messages.create(
                    model="claude-opus-4-5",
                    max_tokens=600,
                    system=system,
                    messages=messages,
                )
                ai_reply = response.content[0].text
                history.append({"role": "ai", "text": ai_reply, "style": current_style})
                st.session_state.doubt_history = history
                log_interaction("doubt", doubt_input.strip()[:40])
                add_topic_studied(doubt_input.strip()[:40])
            except Exception as e:
                st.error(f"Error: {e}")
        st.rerun()

    # Revision quick-fire buttons
    revision_queue = st.session_state.get("revision_queue", [])
    if revision_queue:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            '<div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;'
            'color:#F5C842;margin-bottom:0.5rem;">⚑ Tap to revise a flagged topic</div>',
            unsafe_allow_html=True
        )
        cols = st.columns(min(len(revision_queue), 3))
        for col, rev_topic in zip(cols, revision_queue[:3]):
            with col:
                if st.button(f"⚑ {rev_topic[:20]}", key=f"revq_{rev_topic}",
                             use_container_width=True):
                    current_style = st.session_state.get("learning_style", "stepbystep")
                    system = _build_doubt_system(current_style)
                    history = st.session_state.get("doubt_history", [])
                    history.append({
                        "role": "user",
                        "text": f"I need to revise '{rev_topic}' — I'm weak on this."
                    })
                    with st.spinner("Targeted revision loading…"):
                        try:
                            from utils.ai import get_client
                            client = get_client()
                            response = client.messages.create(
                                model="claude-opus-4-5",
                                max_tokens=500,
                                system=system,
                                messages=[{"role": "user",
                                           "content": f"Targeted revision for weak topic: {rev_topic}"}],
                            )
                            history.append({
                                "role": "ai",
                                "text": response.content[0].text,
                                "style": current_style
                            })
                            st.session_state.doubt_history = history
                        except Exception as e:
                            st.error(str(e))
                    st.rerun()
