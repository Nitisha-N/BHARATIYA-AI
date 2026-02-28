# 🚀 AI-Powered Learning Assistant  
### Prototype Phase – AWS Integration in Progress  

This repository contains the working prototype of **BharatiyaAI**, a personalized adaptive learning assistant built for the AI for Bharat Hackathon (Student Track – AI for Learning & Developer Productivity).

The project has transitioned from design to active prototype development. System documentation is included, and AWS-based implementation is currently underway.

---

## 🎯 Overview

BharatiyaAI is a personalized AI learning assistant that adapts to each student’s study style.  

Students can:
- Upload their own study materials (PDFs)
- Select their preferred learning approach
- Receive adaptive explanations
- Generate practice questions
- Get live feedback on answers
- Track weak concepts during the session

The goal is to create a guided, adaptive learning experience rather than a generic document-based chatbot.

---

## 🧠 Problem Statement

Students often struggle with static lecture notes and PDFs. Existing tools provide generic explanations that do not adapt to individual learning styles.

This project addresses that gap by combining:
- Student learning profile
- Uploaded academic content
- Adaptive response formatting
- Session-level feedback

---

## 💡 Proposed Solution

The system personalizes how content is delivered based on the learner’s selected study style:

- Structured step-by-step explanations  
- Recall-focused flashcards  
- Concise summaries  

It also generates mini assessments and provides immediate feedback, helping students identify weak areas during the learning session.

---

## 🏗️ System Architecture (High-Level)

The system follows a layered architecture:

- **Presentation Layer** – Streamlit-based UI  
- **Input Processing Layer** – PDF extraction and query handling  
- **Intelligence Layer** – Amazon Bedrock (Claude 3 Sonnet planned)  
- **Data Layer** – Amazon S3 (file storage) + DynamoDB (session metadata)  
- **Response Layer** – Personalized explanation and feedback generation  

Detailed design decisions are available in the `/Documents` directory.

---

## 🛠️ Prototype Implementation

The repository currently includes:

- Streamlit-based UI scaffold (`/app/app.py`)
- Learning style personalization logic
- PDF upload and text extraction setup
- Practice question generation placeholder
- Live feedback flow placeholder
- AWS integration setup (S3, Lambda, Bedrock planned)

This phase focuses on validating the adaptive learning pipeline before scaling features.

---

## ☁️ AWS Integration Plan

The prototype will integrate:

- **Amazon S3** – Study material storage  
- **AWS Lambda** – Backend processing  
- **Amazon Bedrock (Claude 3 Sonnet)** – Adaptive content generation  
- **Amazon DynamoDB** – Session-level performance tracking  

Deployment and Bedrock invocation are currently in progress.

---

## 📊 Current Build Status

## Roadmap

Phase 1 – Core Adaptive Flow (Completed)
Phase 2 – Weak Topic Intelligence Engine (In Progress)
Phase 3 – Bedrock LLM Integration
Phase 4 – Personality Modes (Coach / Strict / Friendly)
Phase 5 – Performance Optimization & Cloud Deployment  

---

## 👤 Team

**Team Name:** BharatiyaAI  
**Team Lead:** Nitisha Mandar Naigaonkar  

---

## 📌 Hackathon Context

This project aligns with the AI for Learning & Developer Productivity track by focusing on:

- Faster learning  
- Conceptual clarity  
- Student-centric AI usage  
- Practical academic support  
