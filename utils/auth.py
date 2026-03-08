from __future__ import annotations
"""
BharatiyaAI Mentor — Auth & User Management
DynamoDB backed. No email. Username + password.
"""

import hashlib
import boto3
import streamlit as st
from datetime import datetime
from botocore.exceptions import ClientError

USERS_TABLE = "baim_users"
REGION = "ap-south-1"


def get_db():
    try:
        return boto3.resource(
            "dynamodb",
            region_name=st.secrets.get("AWS_REGION", REGION),
            aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY"),
        )
    except Exception:
        return None


def _hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()


def is_logged_in() -> bool:
    return st.session_state.get("logged_in", False)


def signup(name: str, username: str, password: str) -> tuple[bool, str]:
    """Create new user. Returns (success, message)."""
    if not name or not username or not password:
        return False, "All fields are required."
    if len(password) < 6:
        return False, "Password must be at least 6 characters."
    if len(username) < 3:
        return False, "Username must be at least 3 characters."

    try:
        db = get_db()
        if not db:
            return False, "Database connection failed. Check AWS credentials."

        table = db.Table(USERS_TABLE)

        # Check if username exists
        existing = table.get_item(Key={"username": username.lower()})
        if "Item" in existing:
            return False, "Username already taken. Please choose another."

        # Create user
        table.put_item(Item={
            "username": username.lower(),
            "name": name,
            "password_hash": _hash_password(password),
            "created_at": datetime.now().isoformat(),
            "onboarded": False,
            "xp": 0,
            "streak": 0,
            "last_active": datetime.now().strftime("%Y-%m-%d"),
            "badges": [],
            "topics_studied": [],
            "weak_concepts": [],
            "strong_concepts": [],
            "topic_confidence": {},
            "questions_attempted": 0,
            "correct_count": 0,
            "viva_sessions": 0,
            "pyq_attempted": 0,
        })

        # Set session
        st.session_state.logged_in = True
        st.session_state.username = username.lower()
        st.session_state.user_name = name
        return True, "Account created successfully!"

    except ClientError as e:
        return False, f"Error: {e.response['Error']['Message']}"
    except Exception as e:
        return False, f"Error: {str(e)}"


def login(username: str, password: str) -> tuple[bool, str]:
    """Login existing user. Returns (success, message)."""
    if not username or not password:
        return False, "Please enter username and password."

    try:
        db = get_db()
        if not db:
            return False, "Database connection failed. Check AWS credentials."

        table = db.Table(USERS_TABLE)
        resp = table.get_item(Key={"username": username.lower()})

        if "Item" not in resp:
            return False, "Username not found."

        user = resp["Item"]
        if user["password_hash"] != _hash_password(password):
            return False, "Incorrect password."

        # Load user into session
        st.session_state.logged_in = True
        st.session_state.username = username.lower()
        st.session_state.user_name = user["name"]
        st.session_state.onboarded = user.get("onboarded", False)
        st.session_state.xp = int(user.get("xp", 0))
        st.session_state.streak = int(user.get("streak", 0))
        st.session_state.badges = user.get("badges", [])
        st.session_state.topics_studied = user.get("topics_studied", [])
        st.session_state.weak_concepts = user.get("weak_concepts", [])
        st.session_state.strong_concepts = user.get("strong_concepts", [])
        st.session_state.topic_confidence = user.get("topic_confidence", {})
        st.session_state.questions_attempted = int(user.get("questions_attempted", 0))
        st.session_state.correct_count = int(user.get("correct_count", 0))
        st.session_state.viva_sessions = int(user.get("viva_sessions", 0))
        st.session_state.pyq_attempted = int(user.get("pyq_attempted", 0))

        # Update streak
        _update_streak(username.lower(), user)

        return True, f"Welcome back, {user['name']}!"

    except Exception as e:
        return False, f"Error: {str(e)}"


def logout():
    """Clear session."""
    keys = [
        "logged_in", "username", "user_name", "onboarded",
        "xp", "streak", "badges", "topics_studied", "weak_concepts",
        "strong_concepts", "topic_confidence", "curriculum",
        "active_tab", "doubt_history", "viva_history",
    ]
    for k in keys:
        st.session_state.pop(k, None)


def save_user_progress():
    """Persist current session state back to DynamoDB."""
    username = st.session_state.get("username")
    if not username:
        return
    try:
        db = get_db()
        if not db:
            return
        table = db.Table(USERS_TABLE)
        table.update_item(
            Key={"username": username},
            UpdateExpression="""SET
                xp = :xp,
                streak = :streak,
                badges = :badges,
                topics_studied = :ts,
                weak_concepts = :wc,
                strong_concepts = :sc,
                topic_confidence = :tc,
                questions_attempted = :qa,
                correct_count = :cc,
                viva_sessions = :vs,
                pyq_attempted = :pa,
                last_active = :la
            """,
            ExpressionAttributeValues={
                ":xp": st.session_state.get("xp", 0),
                ":streak": st.session_state.get("streak", 0),
                ":badges": st.session_state.get("badges", []),
                ":ts": st.session_state.get("topics_studied", [])[-50:],
                ":wc": st.session_state.get("weak_concepts", []),
                ":sc": st.session_state.get("strong_concepts", []),
                ":tc": st.session_state.get("topic_confidence", {}),
                ":qa": st.session_state.get("questions_attempted", 0),
                ":cc": st.session_state.get("correct_count", 0),
                ":vs": st.session_state.get("viva_sessions", 0),
                ":pa": st.session_state.get("pyq_attempted", 0),
                ":la": datetime.now().strftime("%Y-%m-%d"),
            }
        )
    except Exception:
        pass


def save_onboarding_data():
    """Save onboarding profile to DynamoDB."""
    username = st.session_state.get("username")
    if not username:
        return
    try:
        db = get_db()
        if not db:
            return
        table = db.Table(USERS_TABLE)
        table.update_item(
            Key={"username": username},
            UpdateExpression="""SET
                onboarded = :o,
                university = :u,
                subject = :s,
                topics = :t,
                learning_style = :ls,
                exam_date = :ed,
                target_score = :ts,
                hours_per_day = :hpd,
                curriculum = :c
            """,
            ExpressionAttributeValues={
                ":o": True,
                ":u": st.session_state.get("university", ""),
                ":s": st.session_state.get("subject", ""),
                ":t": st.session_state.get("topics_text", ""),
                ":ls": st.session_state.get("learning_style", "guided"),
                ":ed": st.session_state.get("exam_date", ""),
                ":ts": st.session_state.get("target_score", ""),
                ":hpd": st.session_state.get("hours_per_day", 2),
                ":c": st.session_state.get("curriculum", {}),
            }
        )
    except Exception:
        pass


def _update_streak(username: str, user: dict):
    """Update daily streak."""
    today = datetime.now().strftime("%Y-%m-%d")
    last_active = user.get("last_active", "")
    current_streak = int(user.get("streak", 0))

    from datetime import date, timedelta
    try:
        last_date = date.fromisoformat(last_active) if last_active else None
        today_date = date.today()
        if last_date == today_date - timedelta(days=1):
            new_streak = current_streak + 1
        elif last_date == today_date:
            new_streak = current_streak
        else:
            new_streak = 1
        st.session_state.streak = new_streak
    except Exception:
        st.session_state.streak = current_streak


def add_xp(points: int, reason: str = ""):
    """Add XP and check badge eligibility."""
    current = st.session_state.get("xp", 0)
    st.session_state.xp = current + points
    save_user_progress()
    _check_badges()


def _check_badges():
    """Award badges based on milestones."""
    badges = st.session_state.get("badges", [])
    tc = st.session_state.get("topic_confidence", {})
    streak = st.session_state.get("streak", 0)
    viva = st.session_state.get("viva_sessions", 0)
    pyq = st.session_state.get("pyq_attempted", 0)
    accuracy = 0
    attempted = st.session_state.get("questions_attempted", 0)
    correct = st.session_state.get("correct_count", 0)
    if attempted > 0:
        accuracy = (correct / attempted) * 100

    mastered = len([t for t, d in tc.items() if d.get("score", 0) >= 80])

    new_badges = []
    if mastered >= 10 and "Concept Master" not in badges:
        new_badges.append("Concept Master")
    if streak >= 5 and "Practice Streak" not in badges:
        new_badges.append("Practice Streak")
    if viva >= 1 and "Viva Ready" not in badges:
        new_badges.append("Viva Ready")
    if pyq >= 20 and "PYQ Analyst" not in badges:
        new_badges.append("PYQ Analyst")
    if accuracy >= 85 and attempted >= 10 and "Top Performer" not in badges:
        new_badges.append("Top Performer")

    if new_badges:
        st.session_state.badges = badges + new_badges
        for badge in new_badges:
            st.toast(f"🏆 Badge unlocked: {badge}!", icon="🎉")
