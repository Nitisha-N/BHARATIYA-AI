"""Session state initialiser for BharatiyaAI × LearnOS"""

import streamlit as st


def init_session():
    defaults = {
        # Onboarding
        "onboarded": False,
        "onboard_step": 0,

        # Profile
        "student_name": "",
        "subject": "",
        "syllabus_text": "",
        "learning_style": "stepbystep",
        "exam_weeks": 4,
        "uploaded_filename": "",
        "uploaded_text": "",

        # Navigation
        "active_tab": "dashboard",

        # Curriculum
        "curriculum": None,
        "active_week": 0,

        # Learn tab
        "last_topic": "",
        "last_explanation": None,
        "last_flashcards": [],
        "topics_studied": [],

        # Doubt chat history — list of {"role": "user"|"ai", "text": str, "style": str}
        "doubt_history": [],

        # Flashcard session
        "fc_index": 0,
        "fc_known": [],
        "fc_flipped": False,
        "fc_cards": [],

        # Mind map
        "mindmap_data": None,

        # Practice
        "practice_questions": [],
        "practice_answers": {},
        "practice_feedbacks": {},
        "practice_revealed": {},
        "practice_generated": False,

        # Insights
        "insights_data": None,

        # ── ADAPTIVE INTELLIGENCE ENGINE ──
        # topic_confidence: {topic_name: {"score": 0-100, "attempts": int, "correct": int,
        #                                  "fc_known": int, "fc_total": int, "status": "weak|learning|strong"}}
        "topic_confidence": {},

        # interaction_log: list of {"type": "practice|flashcard|doubt", "topic": str,
        #                            "correct": bool|None, "timestamp": str}
        "interaction_log": [],

        # curriculum_priority: list of week indices sorted by urgency (weakest first)
        "curriculum_priority": [],

        # recommended_mode: AI-suggested learning style override per topic
        "recommended_mode": {},

        # adaptation_triggered: bool — did the system reorder this session?
        "adaptation_triggered": False,

        # revision_queue: list of topics flagged for targeted revision
        "revision_queue": [],

        # Session tracking
        "weak_concepts": [],
        "strong_concepts": [],
        "questions_attempted": 0,
        "correct_count": 0,
        "session_score": None,
    }

    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def set_tab(tab_name: str):
    st.session_state.active_tab = tab_name


def add_topic_studied(topic: str):
    if topic and topic not in st.session_state.topics_studied:
        st.session_state.topics_studied.append(topic)
    _ensure_topic_confidence(topic)


def flag_weak(concept: str):
    if not concept:
        return
    if concept not in st.session_state.weak_concepts:
        st.session_state.weak_concepts.append(concept)
    if concept in st.session_state.strong_concepts:
        st.session_state.strong_concepts.remove(concept)
    _update_topic_confidence(concept, correct=False)
    _add_to_revision_queue(concept)


def flag_strong(concept: str):
    if not concept:
        return
    if concept not in st.session_state.strong_concepts:
        st.session_state.strong_concepts.append(concept)
    _update_topic_confidence(concept, correct=True)
    _remove_from_revision_queue(concept)


# ── ADAPTIVE ENGINE INTERNALS ──

def _ensure_topic_confidence(topic: str):
    """Initialise topic confidence entry if missing."""
    tc = st.session_state.topic_confidence
    if topic and topic not in tc:
        tc[topic] = {
            "score": 50,          # start neutral
            "attempts": 0,
            "correct": 0,
            "fc_known": 0,
            "fc_total": 0,
            "status": "learning",
        }
    st.session_state.topic_confidence = tc


def _update_topic_confidence(topic: str, correct: bool):
    """Update topic confidence score based on performance signal."""
    _ensure_topic_confidence(topic)
    tc = st.session_state.topic_confidence
    entry = tc[topic]
    entry["attempts"] += 1
    if correct:
        entry["correct"] += 1
        # Weighted: each correct answer +8, diminishing returns near 100
        delta = max(3, 8 * (1 - entry["score"] / 100))
        entry["score"] = min(100, entry["score"] + delta)
    else:
        # Each wrong answer -10
        entry["score"] = max(0, entry["score"] - 10)

    # Update status
    s = entry["score"]
    if s >= 75:
        entry["status"] = "strong"
    elif s >= 40:
        entry["status"] = "learning"
    else:
        entry["status"] = "weak"

    tc[topic] = entry
    st.session_state.topic_confidence = tc
    _reorder_curriculum_priority()


def update_fc_confidence(topic: str, known: int, total: int):
    """Update confidence from flashcard session results."""
    _ensure_topic_confidence(topic)
    tc = st.session_state.topic_confidence
    entry = tc[topic]
    entry["fc_known"] = known
    entry["fc_total"] = total
    if total > 0:
        fc_ratio = known / total
        # Blend flashcard signal (30%) with existing score (70%)
        entry["score"] = round(0.7 * entry["score"] + 0.3 * fc_ratio * 100)
    entry["status"] = "strong" if entry["score"] >= 75 else ("learning" if entry["score"] >= 40 else "weak")
    tc[topic] = entry
    st.session_state.topic_confidence = tc
    _reorder_curriculum_priority()


def log_interaction(interaction_type: str, topic: str, correct=None):
    """Append to interaction log."""
    from datetime import datetime
    log = st.session_state.interaction_log
    log.append({
        "type": interaction_type,
        "topic": topic,
        "correct": correct,
        "timestamp": datetime.now().strftime("%H:%M"),
    })
    st.session_state.interaction_log = log[-50:]  # keep last 50


def _add_to_revision_queue(topic: str):
    rq = st.session_state.revision_queue
    if topic and topic not in rq:
        rq.append(topic)
    st.session_state.revision_queue = rq


def _remove_from_revision_queue(topic: str):
    rq = st.session_state.revision_queue
    if topic in rq:
        rq.remove(topic)
    st.session_state.revision_queue = rq


def _reorder_curriculum_priority():
    """
    Reorder curriculum weeks by urgency.
    Weeks whose topics overlap with weak concepts get higher priority.
    """
    curriculum = st.session_state.get("curriculum")
    if not curriculum:
        return
    weeks = curriculum.get("weeks", [])
    tc = st.session_state.topic_confidence
    weak_set = set(st.session_state.weak_concepts)

    scored_weeks = []
    for i, week in enumerate(weeks):
        topics = week.get("topics", [])
        # Average confidence for topics in this week
        scores = [tc[t]["score"] for t in topics if t in tc]
        avg = sum(scores) / len(scores) if scores else 50
        # Count weak topic overlaps
        weak_overlap = len([t for t in topics if t in weak_set])
        # Priority score: lower confidence + more weak overlaps = higher urgency
        urgency = (100 - avg) + (weak_overlap * 15)
        scored_weeks.append((i, urgency))

    scored_weeks.sort(key=lambda x: x[1], reverse=True)
    priority = [idx for idx, _ in scored_weeks]

    if priority != st.session_state.curriculum_priority:
        st.session_state.curriculum_priority = priority
        if len(weak_set) >= 2:
            st.session_state.adaptation_triggered = True


def get_weak_context_string() -> str:
    """Return a formatted string of weak topics for prompt injection."""
    weak = st.session_state.get("weak_concepts", [])
    tc = st.session_state.get("topic_confidence", {})
    if not weak:
        return ""
    lines = []
    for w in weak[:5]:
        score = tc.get(w, {}).get("score", "?")
        lines.append(f"- {w} (confidence: {score}%)")
    return "Student's known weak areas:\n" + "\n".join(lines)


def get_recommended_mode(topic: str) -> str:
    """
    Recommend a learning mode for a topic based on performance.
    Low confidence → stepbystep. Medium → visual. High → flashcard for retention.
    """
    tc = st.session_state.get("topic_confidence", {})
    entry = tc.get(topic)
    if not entry:
        return st.session_state.get("learning_style", "stepbystep")
    score = entry["score"]
    if score < 40:
        return "stepbystep"    # needs structured scaffolding
    elif score < 70:
        return "visual"        # reinforce with mental models
    else:
        return "flashcard"     # high confidence → test retention
