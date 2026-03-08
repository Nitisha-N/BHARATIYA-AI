"""BharatiyaAI Mentor — Session State"""

import streamlit as st


def init_session():
    defaults = {
        # Auth
        "logged_in": False,
        "username": "",
        "user_name": "",

        # Onboarding
        "onboarded": False,
        "onboard_step": 0,
        "university": "",
        "subject": "",
        "topics_text": "",
        "learning_style": "guided",
        "exam_date": "",
        "target_score": "",
        "hours_per_day": 2,
        "uploaded_filename": "",
        "uploaded_text": "",

        # Navigation
        "active_tab": "home",

        # Curriculum
        "curriculum": None,
        "active_week": 0,

        # Level 1
        "last_topic": "",
        "last_explanation": None,
        "doubt_history": [],
        "spaced_rep_due": [],
        "concepts_learned": [],

        # Flashcards
        "fc_cards": [],
        "fc_index": 0,
        "fc_known": [],
        "fc_flipped": False,

        # Level 2
        "practice_questions": [],
        "practice_answers": {},
        "practice_feedbacks": {},
        "practice_revealed": {},
        "practice_generated": False,

        # Level 3 PYQ
        "pyq_bank": [],
        "pyq_filter_topic": "",
        "pyq_filter_difficulty": "",
        "pyq_filter_marks": 0,

        # Viva
        "viva_active": False,
        "viva_history": [],
        "viva_topic": "",
        "viva_question_count": 0,
        "viva_scores": [],
        "viva_scorecard": None,
        "viva_failed_attempts": 0,

        # Profile & Gamification
        "xp": 0,
        "streak": 0,
        "badges": [],
        "topics_studied": [],
        "weak_concepts": [],
        "strong_concepts": [],
        "topic_confidence": {},
        "questions_attempted": 0,
        "correct_count": 0,
        "viva_sessions": 0,
        "pyq_attempted": 0,

        # Adaptive Engine
        "interaction_log": [],
        "revision_queue": [],
        "adaptation_triggered": False,
        "curriculum_priority": [],
        "recommended_mode": {},

        # UI
        "session_start": None,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val

    # Session timer
    if st.session_state.session_start is None:
        from datetime import datetime
        st.session_state.session_start = datetime.now()


def set_tab(tab: str):
    st.session_state.active_tab = tab


def add_topic_studied(topic: str):
    if not topic:
        return
    topics = st.session_state.topics_studied
    if topic not in topics:
        topics.append(topic)
        st.session_state.topics_studied = topics
    _ensure_topic_confidence(topic)


def flag_weak(concept: str):
    if not concept:
        return
    wc = st.session_state.weak_concepts
    if concept not in wc:
        wc.append(concept)
        st.session_state.weak_concepts = wc
    sc = st.session_state.strong_concepts
    if concept in sc:
        sc.remove(concept)
        st.session_state.strong_concepts = sc
    _update_confidence(concept, correct=False)
    _add_revision(concept)


def flag_strong(concept: str):
    if not concept:
        return
    sc = st.session_state.strong_concepts
    if concept not in sc:
        sc.append(concept)
        st.session_state.strong_concepts = sc
    _update_confidence(concept, correct=True)
    _remove_revision(concept)


def add_concept_learned(concept: str):
    """Track concepts learned for spaced repetition."""
    learned = st.session_state.concepts_learned
    if concept and concept not in learned:
        learned.append(concept)
        st.session_state.concepts_learned = learned
    # Every 3 concepts, trigger spaced rep check
    if len(learned) > 0 and len(learned) % 3 == 0:
        due = st.session_state.spaced_rep_due
        # Add earliest concept not already due
        for c in learned[:-3]:
            if c not in due:
                due.append(c)
                break
        st.session_state.spaced_rep_due = due


def log_interaction(itype: str, topic: str, correct=None):
    from datetime import datetime
    log = st.session_state.interaction_log
    log.append({
        "type": itype,
        "topic": topic,
        "correct": correct,
        "timestamp": datetime.now().strftime("%H:%M"),
    })
    st.session_state.interaction_log = log[-50:]


def get_weak_context() -> str:
    weak = st.session_state.get("weak_concepts", [])
    tc = st.session_state.get("topic_confidence", {})
    if not weak:
        return ""
    lines = [f"- {w} (confidence: {tc.get(w, {}).get('score', '?')}%)" for w in weak[:5]]
    return "Student's weak areas:\n" + "\n".join(lines)


def get_session_time() -> str:
    start = st.session_state.get("session_start")
    if not start:
        return "0m"
    from datetime import datetime
    delta = datetime.now() - start
    mins = int(delta.total_seconds() / 60)
    if mins < 60:
        return f"{mins}m"
    return f"{mins // 60}h {mins % 60}m"


def get_viva_readiness() -> int:
    tc = st.session_state.get("topic_confidence", {})
    if not tc:
        return 0
    scores = [d.get("score", 0) for d in tc.values()]
    return int(sum(float(s) for s in scores) / len(scores)) if scores else 0


# ── ADAPTIVE ENGINE ──

def _ensure_topic_confidence(topic: str):
    tc = st.session_state.topic_confidence
    if topic and topic not in tc:
        tc[topic] = {"score": 50, "attempts": 0, "correct": 0, "status": "learning"}
    st.session_state.topic_confidence = tc


def _update_confidence(topic: str, correct: bool):
    _ensure_topic_confidence(topic)
    tc = st.session_state.topic_confidence
    entry = tc[topic]
    entry["attempts"] = entry.get("attempts", 0) + 1
    if correct:
        entry["correct"] = entry.get("correct", 0) + 1
        delta = max(3, 8 * (1 - entry["score"] / 100))
        entry["score"] = min(100, entry["score"] + delta)
    else:
        entry["score"] = max(0, entry["score"] - 10)
    s = entry["score"]
    entry["status"] = "strong" if s >= 75 else ("learning" if s >= 40 else "weak")
    tc[topic] = entry
    st.session_state.topic_confidence = tc
    _reorder_curriculum()


def _add_revision(topic: str):
    rq = st.session_state.revision_queue
    if topic and topic not in rq:
        rq.append(topic)
    st.session_state.revision_queue = rq


def _remove_revision(topic: str):
    rq = st.session_state.revision_queue
    if topic in rq:
        rq.remove(topic)
    st.session_state.revision_queue = rq


def _reorder_curriculum():
    curriculum = st.session_state.get("curriculum")
    if not curriculum:
        return
    weeks = curriculum.get("weeks", [])
    tc = st.session_state.topic_confidence
    weak_set = set(st.session_state.weak_concepts)
    scored = []
    for i, week in enumerate(weeks):
        topics = week.get("topics", [])
        scores = [tc[t]["score"] for t in topics if t in tc]
        avg = sum(float(s) for s in scores) / len(scores) if scores else 50
        weak_overlap = len([t for t in topics if t in weak_set])
        urgency = (100 - avg) + (weak_overlap * 15)
        scored.append((i, urgency))
    scored.sort(key=lambda x: x[1], reverse=True)
    priority = [idx for idx, _ in scored]
    if priority != st.session_state.curriculum_priority:
        st.session_state.curriculum_priority = priority
        if len(weak_set) >= 2:
            st.session_state.adaptation_triggered = True
