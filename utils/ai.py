from __future__ import annotations
"""
BharatiyaAI Mentor — AI Engine
AWS Bedrock: Nova Lite (simple) / Claude Sonnet (complex)
DynamoDB response caching — hash input, skip repeat Bedrock calls
"""

import json
import hashlib
import boto3
import streamlit as st
from botocore.exceptions import ClientError


# ── CONFIG ──
BEDROCK_REGION = "ap-south-1"

MODEL_LITE = "apac.amazon.nova-lite-v1:0"
MODEL_SONNET = "apac.anthropic.claude-3-5-sonnet-20241022-v2:0"

CACHE_TABLE = "baim_cache"


def get_bedrock_client():
    try:
        return boto3.client(
            service_name="bedrock-runtime",
            region_name=st.secrets.get("AWS_REGION", BEDROCK_REGION),
            aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY"),
        )
    except Exception:
        return None


def get_dynamodb():
    try:
        return boto3.resource(
            "dynamodb",
            region_name=st.secrets.get("AWS_REGION", BEDROCK_REGION),
            aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY"),
        )
    except Exception:
        return None


def _hash_prompt(system: str, user: str) -> str:
    combined = f"{system}|||{user}"
    return hashlib.sha256(combined.encode()).hexdigest()[:40]


def _get_cached(prompt_hash: str) -> str | None:
    try:
        db = get_dynamodb()
        if not db:
            return None

        table = db.Table(CACHE_TABLE)
        resp = table.get_item(Key={"prompt_hash": prompt_hash})

        return resp.get("Item", {}).get("response")
    except Exception:
        return None


def _set_cache(prompt_hash: str, response: str):
    try:
        db = get_dynamodb()
        if not db:
            return

        table = db.Table(CACHE_TABLE)

        table.put_item(
            Item={
                "prompt_hash": prompt_hash,
                "response": response,
            }
        )
    except Exception:
        pass


def call_bedrock(
    system_prompt: str,
    user_message: str,
    use_sonnet: bool = False,
    max_tokens: int = 1000,
    use_cache: bool = True,
) -> str:

    prompt_hash = _hash_prompt(system_prompt, user_message)

    if use_cache:
        cached = _get_cached(prompt_hash)
        if cached:
            return cached

    try:
        client = get_bedrock_client()
        if not client:
            return "ERROR:NO_CLIENT"

        model = MODEL_SONNET if use_sonnet else MODEL_LITE

        # Claude models
        if "claude" in model:

            body = json.dumps(
                {
                    "anthropic_version": "bedrock-2023-05-31",
                    "max_tokens": max_tokens,
                    "system": system_prompt,
                    "messages": [
                        {
                            "role": "user",
                            "content": user_message,
                        }
                    ],
                }
            )

        # Nova models
        else:

            body = json.dumps(
                {
                    "messages": [
                        {
                            "role": "user",
                            "content": [{"text": f"{system_prompt}\n\n{user_message}"}],
                        }
                    ],
                    "inferenceConfig": {
                        "maxTokens": max_tokens,
                    },
                }
            )

        response = client.invoke_model(modelId=model, body=body)

        result = json.loads(response["body"].read())

        if "claude" in model:
            text = result["content"][0]["text"]
        else:
            text = result["output"]["message"]["content"][0]["text"]

        if use_cache:
            _set_cache(prompt_hash, text)

        return text

    except ClientError as e:
        code = e.response["Error"]["Code"]
        return f"ERROR:AWS:{code}"

    except Exception as e:
        return f"ERROR:{str(e)}"


def call_bedrock_json(
    system_prompt: str,
    user_message: str,
    use_sonnet: bool = False,
    max_tokens: int = 1000,
):

    raw = call_bedrock(
        system_prompt
        + "\n\nReturn ONLY valid JSON. No markdown fences. No explanation.",
        user_message,
        use_sonnet=use_sonnet,
        max_tokens=max_tokens,
    )

    if raw.startswith("ERROR:"):
        st.error(raw)
        return None

    cleaned = raw.strip()

    if cleaned.startswith("```"):
        lines = cleaned.split("\n")
        cleaned = "\n".join(
            lines[1:-1] if lines[-1].strip() == "```" else lines[1:]
        )

    try:
        return json.loads(cleaned)

    except json.JSONDecodeError:
        return None

# ══════════════════════════════════════
# SYSTEM PROMPTS
# ══════════════════════════════════════

CURRICULUM_SYSTEM = """You are BharatiyaAI Mentor — an expert academic curriculum designer for Indian university students.
Design a personalized week-by-week study plan based on the student's profile.
Make it realistic based on hours available per day and target score.
Return ONLY valid JSON:
{
  "subject": "...",
  "university": "...",
  "total_weeks": N,
  "hours_per_day": N,
  "target_score": "...",
  "overall_goal": "what student will achieve",
  "style_note": "how this plan is personalized",
  "weeks": [
    {
      "week": 1,
      "name": "Week 1: Theme",
      "theme": "short description",
      "topics": ["topic1", "topic2", "topic3"],
      "focus": "main skill to master",
      "hours_needed": N,
      "difficulty": "easy|medium|hard",
      "progress": 0
    }
  ]
}"""


GUIDED_DISCOVERY_SYSTEM = """You are BharatiyaAI Mentor using Guided Discovery mode.
Do NOT lecture. Do NOT give textbook explanations.
Instead — ask the student a question to make them THINK about the concept.
Then respond to their answer with follow-up questions and gentle corrections.
Every 2-3 exchanges, circle back: "Before we continue — do you still remember [earlier concept]?"
Style: warm but intellectually demanding. Like a brilliant senior student tutoring a friend.
Keep each response to 3-5 sentences max. Always end with a question."""


VISUAL_SYSTEM = """You are BharatiyaAI Mentor using Visual & Analogy mode.
Explain using vivid mental models, analogies, and ASCII flowcharts/diagrams.
Structure: analogy first → ASCII diagram → real-world connection.
After every 2-3 concepts: "Can you describe this diagram back to me in your own words?"
Make the student SEE the concept. Use Indian context examples where natural."""


SUMMARY_SYSTEM = """You are BharatiyaAI Mentor using Quick Summary mode.
Structure: 1-line TL;DR → 5 bullet key points → "Remember:" one golden takeaway.
Be ruthlessly concise. Every word earns its place.
After 2-3 summaries, fire a recall check: "Quick — in one sentence, what was [topic] about?"
No padding. No filler. Make it exam-ready."""


FLASHCARD_SYSTEM = """You are BharatiyaAI Mentor generating flashcards for active recall.
Generate exactly 7 flashcard pairs. Return JSON array:
[{"front": "question or term", "back": "answer or definition", "difficulty": "easy|medium|hard"}]
Mix question types: definitions, applications, comparisons, examples.
Make them exam-ready for Indian university style.
Include 1-2 cards specifically targeting any known weak areas."""


DOUBT_SOLVER_SYSTEM = """You are BharatiyaAI Mentor — a live contextual doubt solver.
You know this student's subject, university, weak areas, and study material.
Rules:
1. Answer the doubt directly and precisely first
2. Connect to weak areas where relevant: "Since you've been struggling with X..."
3. Match their chosen learning style
4. If the doubt reveals a new gap, flag it: "This suggests [concept] needs more attention"
5. Keep responses focused — 4-8 sentences max
6. End with one follow-up question to deepen understanding
You are not generic. You know this student."""


PRACTICE_SYSTEM = """You are BharatiyaAI Mentor adaptive practice engine for Indian university exams.
Generate 5 questions mixing MCQ and short answer.
Return JSON array:
[{
  "question": "...",
  "type": "mcq|short",
  "options": ["A...", "B...", "C...", "D..."],
  "answer": 0,
  "explanation": "why this is correct",
  "topic_tag": "which topic",
  "difficulty": "easy|medium|hard",
  "marks": 2
}]
For short answer: options = [], answer = -1, include model_answer field.
Target weak areas with at least 2 questions.
Mix: 1 easy, 3 medium, 1 hard. University exam style."""


FEEDBACK_SYSTEM = """You are BharatiyaAI Mentor answer evaluator.
Give 2-sentence feedback. Start with ✓ if correct, ✗ if wrong.
Be kind, specific, educational. If wrong — give the key correction.
End with one targeted revision tip."""


PYQ_EXTRACT_SYSTEM = """You are BharatiyaAI Mentor PYQ extraction engine for Indian university exams.
Extract ALL questions from the past year paper text provided.
Return JSON array:
[{
  "question": "full question text",
  "marks": 5,
  "type": "short|long|mcq|numerical|diagram",
  "topic": "inferred topic",
  "year": "2023 or unknown",
  "unit": "Unit N or unknown",
  "keywords": ["kw1", "kw2"],
  "difficulty": "easy|medium|hard"
}]
Extract EVERY question. Infer marks from context."""


PYQ_GENERATE_SYSTEM = """You are BharatiyaAI Mentor PYQ generation engine.
Generate realistic past-year style questions matching the university's exam pattern.
Return JSON array:
[{
  "question": "full question",
  "marks": 5,
  "type": "short|long|mcq|numerical|diagram",
  "topic": "topic name",
  "year": "AI Generated",
  "unit": "Unit N",
  "keywords": ["kw1", "kw2"],
  "difficulty": "easy|medium|hard",
  "hint": "one-line hint"
}]
Generate 15 questions. Mix: 4 short (2 marks), 6 medium (5 marks), 3 long (10 marks), 2 MCQ.
Match the specific university's question pattern and style."""


MODEL_ANSWER_SYSTEM = """You are BharatiyaAI Mentor model answer generator for Indian university exams.
Generate a university-accepted model answer.
Formatting rules:
- Start with a clear definition or statement
- Use numbered points
- Include Advantages/Disadvantages/Applications where relevant
- Mention [DIAGRAM: description] placeholders
- For numerical: show all steps
- End with a conclusion
- 2 marks = 4-5 lines, 5 marks = 10-12 lines, 10 marks = full page
- Match the specific university's answer style and terminology"""


VIVA_EXAMINER_SYSTEM = """You are a strict but fair external examiner conducting a university viva voce examination.
You are evaluating a student on their subject knowledge.

Rules:
1. Ask ONE clear question at a time
2. Evaluate the student's answer for: correct terminology, conceptual depth, answer structure
3. If answer is ≥85% correct: acknowledge briefly and move to next concept
4. If answer is <85%: counter-question — "That's incomplete. What about [specific gap]?"
5. After 2 failed attempts: show the correct answer with explanation
6. Use formal examiner language — not friendly, not harsh, professional
7. Remember what the student said earlier in the session
8. Expect proper technical terminology — flag incorrect usage explicitly

Score mentally: terminology (0-10), depth (0-10), structure (0-5)
You are preparing this student for their real viva. Be the examiner they need to practice with."""


VIVA_SCORECARD_SYSTEM = """You are BharatiyaAI Mentor viva scorecard generator.
Based on the complete viva session, generate a detailed scorecard.
Return JSON:
{
  "terminology_score": 7,
  "depth_score": 6,
  "structure_score": 4,
  "predicted_score": 17,
  "max_score": 25,
  "grade": "Good|Average|Excellent|Needs Improvement",
  "strengths": ["what student did well"],
  "weak_areas": ["where student struggled"],
  "terminology_errors": ["wrong term used → correct term"],
  "examiner_comment": "one sentence in formal examiner style",
  "revision_priority": ["topic1", "topic2"]
}"""


SPACED_REPETITION_SYSTEM = """You are BharatiyaAI Mentor spaced repetition engine.
Generate a recall check question for an earlier concept the student learned.
The question should:
1. Test genuine understanding, not just memory
2. Be answerable in 1-2 sentences
3. Connect to something they learned recently if possible
Return JSON:
{
  "recall_question": "...",
  "topic": "which earlier topic this tests",
  "expected_keywords": ["keyword1", "keyword2", "keyword3"]
}"""


INSIGHTS_SYSTEM = """You are BharatiyaAI Mentor analytics engine.
Generate personalized insights from the student's session data.
Return JSON:
{
  "headline": "one powerful summary sentence",
  "weekly_score": 75,
  "recommendation": "specific 2-sentence study advice",
  "strengths": ["strength1", "strength2"],
  "improvements": ["area1", "area2"],
  "next_action": "single most important thing to do next",
  "topic_mastery": [{"name": "topic", "score": 75, "status": "strong|weak|learning"}],
  "encouragement": "warm, specific motivational message"
}"""



def call_bedrock_stream(
    system_prompt: str,
    user_message: str,
    use_sonnet: bool = False,
    max_tokens: int = 1000,
):
    """Streaming wrapper — falls back to non-streaming for compatibility."""
    return call_bedrock(
        system_prompt=system_prompt,
        user_message=user_message,
        use_sonnet=use_sonnet,
        max_tokens=max_tokens,
        use_cache=False,
    )


def call_bedrock_stream(system_prompt: str, user_message: str, use_sonnet: bool = False, max_tokens: int = 1000) -> str:
    return call_bedrock(system_prompt=system_prompt, user_message=user_message, use_sonnet=use_sonnet, max_tokens=max_tokens, use_cache=False)


def call_bedrock_stream(system_prompt: str, user_message: str, use_sonnet: bool = False, max_tokens: int = 1000) -> str:
    return call_bedrock(system_prompt=system_prompt, user_message=user_message, use_sonnet=use_sonnet, max_tokens=max_tokens, use_cache=False)
