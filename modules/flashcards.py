"""BharatiyaAI × LearnOS — Flashcards Page"""

import streamlit as st
from utils.ai import call_claude_json, STYLE_SYSTEM
from utils.session import flag_weak, flag_strong, add_topic_studied
from utils.pdf_reader import build_context_block


def _get_week_info():
    curriculum = st.session_state.get("curriculum", {})
    weeks = curriculum.get("weeks", [])
    idx = st.session_state.get("active_week", 0)
    if idx < len(weeks):
        w = weeks[idx]
        return w.get("name", ""), ", ".join(w.get("topics", []))
    return "", ""


def render_flashcards():
    week_name, week_topics = _get_week_info()

    st.markdown(f"""
<div style="margin-bottom:1.5rem;">
  <div style="font-family:'Noto Serif',serif;font-size:1.8rem;font-weight:600;">🃏 Flashcards</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-top:2px;">{week_name} · Active Recall Session</div>
</div>
""", unsafe_allow_html=True)

    cards = st.session_state.get("fc_cards", [])

    # ── GENERATE IF EMPTY ──
    if not cards:
        st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:14px;padding:1.5rem;margin-bottom:1.25rem;">
  <div style="font-size:0.68rem;text-transform:uppercase;letter-spacing:0.1em;color:#6B7A99;margin-bottom:0.75rem;">
    Generate flashcards for
  </div>
  <div style="display:flex;gap:0.625rem;flex-wrap:wrap;">
""", unsafe_allow_html=True)
        chips = week_topics.split(", ") if week_topics else []
        chips_html = "".join(
            f'<span style="display:inline-flex;font-size:0.75rem;padding:3px 10px;border-radius:20px;margin:2px;'
            f'background:rgba(255,107,43,0.1);border:1px solid rgba(255,107,43,0.2);color:#FF8F5A;">{t}</span>'
            for t in chips
        )
        st.markdown(chips_html + "</div></div>", unsafe_allow_html=True)

        custom_topic = st.text_input("Or enter a custom topic", key="fc_custom_topic",
                                     placeholder="e.g. Laws of Motion, Photosynthesis…")

        if st.button("🃏 Generate Flashcards", key="fc_generate", use_container_width=True):
            topic = custom_topic.strip() or week_topics or st.session_state.get("subject", "")
            context = build_context_block(st.session_state.get("uploaded_text", ""), topic)
            with st.spinner("Generating flashcards…"):
                data = call_claude_json(STYLE_SYSTEM["flashcard"], context, max_tokens=1200)
            if data and isinstance(data, list):
                st.session_state.fc_cards = data
                st.session_state.fc_index = 0
                st.session_state.fc_known = []
                st.session_state.fc_flipped = False
                st.session_state.last_topic = topic
                add_topic_studied(topic)
                st.rerun()
            else:
                st.error("Could not generate flashcards. Check your API key.")
        return

    # ── ACTIVE DECK ──
    fc_idx = st.session_state.get("fc_index", 0)
    fc_known = st.session_state.get("fc_known", [])
    fc_flipped = st.session_state.get("fc_flipped", False)
    total = len(cards)

    # Deck complete
    if fc_idx >= total:
        score_pct = round(len(fc_known) / total * 100) if total else 0
        # Update topic confidence from flashcard results
        topic = st.session_state.get("last_topic", week_name)
        from utils.session import update_fc_confidence, log_interaction
        update_fc_confidence(topic, len(fc_known), total)
        log_interaction("flashcard", topic, correct=(score_pct >= 70))
        st.markdown(f"""
<div style="background:rgba(17,28,56,0.95);border:1px solid rgba(255,255,255,0.07);
border-radius:20px;padding:2.5rem;text-align:center;margin:1rem 0;">
  <div style="font-size:2rem;margin-bottom:0.5rem;">🎉</div>
  <div style="font-family:'Noto Serif',serif;font-size:1.4rem;margin-bottom:0.5rem;">Deck Complete!</div>
  <div style="font-family:'JetBrains Mono',monospace;font-size:3.5rem;color:#FF6B2B;margin:0.5rem 0;">{score_pct}%</div>
  <div style="color:#6B7A99;font-size:0.875rem;margin-bottom:1.5rem;">
    ✓ {len(fc_known)} known · ⚑ {total - len(fc_known)} to review
  </div>
</div>
""", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3)
        with c1:
            if st.button("🔁 Restart Deck", use_container_width=True, key="fc_restart"):
                st.session_state.fc_index = 0
                st.session_state.fc_known = []
                st.session_state.fc_flipped = False
                st.rerun()
        with c2:
            if st.button("✏️ Practice Test", use_container_width=True, key="fc_to_practice"):
                from utils.session import set_tab
                set_tab("practice")
                st.rerun()
        with c3:
            if st.button("New Topic", use_container_width=True, key="fc_new"):
                st.session_state.fc_cards = []
                st.session_state.fc_index = 0
                st.session_state.fc_known = []
                st.rerun()
        return

    # Progress bar
    st.progress(fc_idx / total, text=f"Card {fc_idx + 1} of {total}  ·  ✓ {len(fc_known)} known")
    st.markdown("<br>", unsafe_allow_html=True)

    card = cards[fc_idx]

    # Card face
    if not fc_flipped:
        st.markdown(f"""
<div class="fc-front">
  <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#6B7A99;margin-bottom:1rem;">
    Question
  </div>
  <div style="font-family:'Noto Serif',serif;font-size:1.3rem;line-height:1.6;">
    {card.get('front', '')}
  </div>
  <div style="font-size:0.72rem;color:#6B7A99;margin-top:1.25rem;">
    Click below to reveal answer
  </div>
</div>
""", unsafe_allow_html=True)
        if st.button("👁 Reveal Answer", key="fc_flip", use_container_width=True):
            st.session_state.fc_flipped = True
            st.rerun()
    else:
        st.markdown(f"""
<div class="fc-back">
  <div style="font-size:0.65rem;text-transform:uppercase;letter-spacing:0.12em;color:#FF6B2B;margin-bottom:1rem;">
    Answer
  </div>
  <div style="font-size:0.95rem;line-height:1.7;">
    {card.get('back', '')}
  </div>
</div>
""", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)
        col_review, col_know = st.columns(2)
        topic = st.session_state.get("last_topic", week_name)
        with col_review:
            if st.button("⚑ Needs Review", key="fc_wrong", use_container_width=True):
                flag_weak(topic)
                st.session_state.fc_index += 1
                st.session_state.fc_flipped = False
                st.rerun()
        with col_know:
            if st.button("✓ I Know This", key="fc_correct", use_container_width=True):
                st.session_state.fc_known.append(fc_idx)
                flag_strong(topic)
                st.session_state.fc_index += 1
                st.session_state.fc_flipped = False
                st.rerun()
