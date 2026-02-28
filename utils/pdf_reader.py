"""PDF & file text extraction for BharatiyaAI"""

import io


def extract_text(uploaded_file) -> str:
    """Extract text from uploaded PDF or TXT file."""
    if uploaded_file is None:
        return ""

    name = uploaded_file.name.lower()

    if name.endswith(".txt"):
        try:
            return uploaded_file.read().decode("utf-8", errors="ignore")
        except Exception:
            return ""

    elif name.endswith(".pdf"):
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(uploaded_file.read()))
            text = ""
            for page in reader.pages:
                text += page.extract_text() or ""
            return text.strip()
        except ImportError:
            # Fallback: try pypdf
            try:
                from pypdf import PdfReader
                reader = PdfReader(io.BytesIO(uploaded_file.read()))
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
                return text.strip()
            except ImportError:
                return f"[PDF uploaded: {uploaded_file.name}. Text extraction requires PyPDF2. Claude will use topic context.]"
        except Exception as e:
            return f"[PDF: {uploaded_file.name} — extraction failed: {e}]"

    return ""


def truncate_context(text: str, max_chars: int = 3000) -> str:
    """Truncate document text for API context window."""
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n\n[...document truncated at {max_chars} chars...]"


def build_context_block(uploaded_text: str, topic: str = "") -> str:
    """Build a context block string for prompts."""
    if not uploaded_text:
        return f"Topic: {topic}" if topic else ""

    if uploaded_text.startswith("[PDF uploaded:") or uploaded_text.startswith("[PDF:"):
        return f"Student uploaded: {uploaded_text}\nTopic asked: {topic}"

    truncated = truncate_context(uploaded_text)
    return f"Student's uploaded study material:\n{truncated}\n\nTopic/Question: {topic}"
