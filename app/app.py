# Basic Prototype outline
import streamlit as st
import PyPDF2
import io

st.set_page_config(page_title="BharatiyaAI", layout="wide")

st.title("BharatiyaAI – Adaptive Learning Assistant")
st.write("Upload your notes, choose how you like to study, and get personalized help.")

# learning style selection
st.subheader("How do you prefer to learn?")

learning_style = st.radio(
    "Select one:",
    [
        "Step-by-step structured explanation",
        "Quick recall / flashcards",
        "Concise summary"
    ]
)

# file upload
st.subheader("Upload your study material (PDF)")

uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])

pdf_text = ""

if uploaded_file:
    reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pdf_text += text

    st.success("PDF uploaded successfully.")

# question input
st.subheader("Ask something from your notes")

question = st.text_input("Enter your question")

def generate_response(style, content, question):
    if not content:
        return "Please upload your study material first."

    if not question:
        return "Ask a question based on your uploaded content."

    # placeholder logic (will connect to Bedrock later)
    if style == "Step-by-step structured explanation":
        return f"Here’s a structured explanation for: {question}"

    if style == "Quick recall / flashcards":
        return f"Flashcard-style response for: {question}"

    if style == "Concise summary":
        return f"Short summary for: {question}"

if st.button("Generate explanation"):
    response = generate_response(learning_style, pdf_text, question)
    st.write(response)

# mini test section
st.subheader("Want to test yourself?")

if st.button("Generate 3 practice questions"):
    st.write("1. Practice question based on your uploaded content")
    st.write("2. Another concept-check question")
    st.write("3. One application-based question")

# feedback section
st.subheader("Submit your answer for feedback")

student_answer = st.text_input("Type your answer")

if st.button("Check answer"):
    if student_answer.strip() == "":
        st.warning("Enter an answer first.")
    else:
        st.write("Thanks for answering.")
        st.write("In the next version, this will evaluate correctness and highlight weak concepts.")
