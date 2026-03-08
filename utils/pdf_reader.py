"""BharatiyaAI Mentor — PDF Reader + S3 Upload"""

import boto3
import streamlit as st
import io

S3_BUCKET = "baim-uploads"
REGION = "ap-south-1"


def get_s3():
    try:
        return boto3.client(
            "s3",
            region_name=st.secrets.get("AWS_REGION", REGION),
            aws_access_key_id=st.secrets.get("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=st.secrets.get("AWS_SECRET_ACCESS_KEY"),
        )
    except Exception:
        return None


def extract_text(uploaded_file) -> str:
    """Extract text from PDF or TXT file safely."""
    if not uploaded_file:
        return ""

    try:
        # Read file bytes once
        file_bytes = uploaded_file.read()

        # Handle TXT
        if uploaded_file.name.endswith(".txt"):
            return file_bytes.decode("utf-8", errors="ignore")

        # Try PyPDF2 first
        try:
            import PyPDF2
            reader = PyPDF2.PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

            if text.strip():
                return text.strip()

        except Exception:
            pass

        # Try pypdf as fallback
        try:
            import pypdf
            reader = pypdf.PdfReader(io.BytesIO(file_bytes))
            text = "\n".join(page.extract_text() or "" for page in reader.pages)

            if text.strip():
                return text.strip()

        except Exception:
            pass

        # If extraction failed
        return f"[PDF uploaded: {uploaded_file.name} — text extraction returned empty]"

    except Exception as e:
        return f"[Error reading file: {str(e)}]"


def upload_to_s3(file_bytes: bytes, filename: str, folder: str = "uploads") -> str | None:
    """Upload file to S3. Returns S3 key or None."""
    try:
        s3 = get_s3()
        if not s3:
            return None

        username = st.session_state.get("username", "unknown")
        key = f"{folder}/{username}/{filename}"

        s3.put_object(
            Bucket=S3_BUCKET,
            Key=key,
            Body=file_bytes,
            ContentType="application/pdf",
        )

        return key

    except Exception:
        return None


def build_context(text: str, topic: str, max_chars: int = 3000) -> str:
    """Build prompt context from uploaded text."""
    if not text or text.startswith("["):
        return f"Topic: {topic}"

    excerpt = text[:max_chars]

    return f"""Study material context:
{excerpt}

Topic to explain: {topic}
"""
