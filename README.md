# 🔵 BharatiyaAI × LearnOS
### Personalized AI Learning Assistant — Built for Bharat
**AI for Bharat Hackathon · Student Track · AI for Learning & Developer Productivity**
Team: BharatiyaAI | Lead: Nitisha Mandar Naigaonkar

---

## ✦ What is BharatiyaAI × LearnOS?

BharatiyaAI × LearnOS is the fusion of two ideas:
- **BharatiyaAI** — an adaptive learning assistant that personalizes *how* content is delivered based on each student's learning style
- **LearnOS** — a full learning operating system that designs a week-by-week personalized curriculum, tracks progress, and adapts over time

Together, they create something no existing tool does: **a personalized curriculum engine + adaptive AI tutor in one**.

---

## 🎯 Features

| Feature | Description |
|---|---|
| **4-Step Onboarding** | Name → Subject + Syllabus upload → Learning Style → Exam timeline |
| **AI Curriculum Builder** | Claude designs a complete week-by-week study plan from your syllabus |
| **Adaptive Learning Modes** | Step-by-Step / Flashcard / Quick Summary / Visual & Analogy |
| **PDF Upload + Context** | Upload study material; Claude uses it as context for all responses |
| **Flashcard Deck** | Active recall with spaced repetition — "Know it / Review it" tracking |
| **Mind Map Generator** | Visual SVG mind maps for any topic |
| **Practice Test** | Adaptive MCQs with live per-answer AI feedback |
| **Session Insights** | Personalized analytics: strengths, weak areas, topic mastery bars |
| **Weak Concept Tracker** | Auto-flagged from wrong answers and flashcard reviews |

---

## 🏗️ Architecture

```
bharatiyaai/
├── app.py                    # Main entry point
├── requirements.txt
├── .streamlit/
│   ├── config.toml           # Theme: saffron/navy palette
│   └── secrets.toml          # API keys (git-ignored)
├── utils/
│   ├── ai.py                 # Anthropic / Bedrock API wrapper + all prompts
│   ├── session.py            # Streamlit session state management
│   ├── styles.py             # Full CSS design system injection
│   ├── sidebar.py            # Sidebar navigation component
│   └── pdf_reader.py         # PDF/TXT extraction + context building
└── pages/
    ├── onboarding.py         # 4-step wizard + curriculum generation
    ├── dashboard.py          # Home: roadmap + quick access tiles
    ├── learn.py              # Adaptive explanations with file context
    ├── curriculum.py         # Weekly roadmap detail view
    ├── flashcards.py         # Active recall card deck
    ├── mindmap.py            # SVG visual mind map
    ├── practice.py           # MCQ test with live AI feedback
    └── insights.py           # Session analytics and recommendations
```

---

## 🚀 Quick Start

### 1. Clone and install
```bash
git clone <your-repo>
cd bharatiyaai
pip install -r requirements.txt
```

### 2. Add your API key
Edit `.streamlit/secrets.toml`:
```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```
Get your key at: https://console.anthropic.com/

### 3. Run
```bash
streamlit run app.py
```

Open http://localhost:8501

---

## ☁️ AWS Bedrock Integration (Production)

To swap from Anthropic API to Amazon Bedrock, edit `utils/ai.py`:

```python
import boto3, json

def call_claude_bedrock(system_prompt, user_message, max_tokens=1200):
    bedrock = boto3.client("bedrock-runtime", region_name="us-east-1")
    body = json.dumps({
        "anthropic_version": "bedrock-2023-05-31",
        "max_tokens": max_tokens,
        "system": system_prompt,
        "messages": [{"role": "user", "content": user_message}],
    })
    response = bedrock.invoke_model(
        modelId="anthropic.claude-3-sonnet-20240229-v1:0",
        body=body,
    )
    result = json.loads(response["body"].read())
    return result["content"][0]["text"]
```

Full AWS stack:
- **S3** → Store uploaded PDFs
- **Lambda** → Trigger PDF extraction on upload
- **Bedrock** → Claude 3 Sonnet inference
- **DynamoDB** → Persist session metadata and progress

---

## 🧠 Learning Modes

| Mode | How Claude Responds |
|---|---|
| 🪜 Step-by-Step | Numbered, structured, builds on itself |
| 🃏 Flashcard | 7 Q&A pairs for active recall |
| 📋 Quick Summary | TL;DR + bullets + single "Remember:" |
| 🎨 Visual & Analogy | Mental images, ASCII diagrams, comparisons |

---

## 📊 Session Tracking

Every student session tracks:
- Topics studied (auto-logged on every Ask)
- Flashcard known/review split
- Questions attempted, correct count, live score %
- Weak concepts (from wrong answers + "Needs Review" flashcards)
- Strong concepts (from correct answers + "I Know This" flashcards)

All feeds into the **Insights** page for personalized Claude-generated recommendations.

---

## 🎨 Design System

Palette inspired by the Indian Tricolour:
- **Saffron** `#FF6B2B` — Primary actions, active states
- **Navy** `#060D1F` — Background
- **Green** `#138808` — Success, strong concepts
- **Gold** `#F5C842` — Warnings, weak concepts, highlights
- Typography: **Sora** (UI) + **Noto Serif** (headings) + **JetBrains Mono** (numbers)

---

## 👤 Team

**Team Name:** BharatiyaAI
**Team Lead:** Nitisha Mandar Naigaonkar
**Track:** AI for Learning & Developer Productivity
**Hackathon:** AI for Bharat
