# utils/validators.py
"""
Input validation helpers for the Resume Analyzer.
"""

from typing import Tuple


def validate_pdf(file_bytes: bytes, filename: str) -> Tuple[bool, str]:
    """
    Validate uploaded PDF file.
    Returns (is_valid, error_message).
    """
    if not file_bytes:
        return False, "No file uploaded. Please upload a PDF resume."

    if not filename.lower().endswith(".pdf"):
        return False, "Invalid file type. Only PDF files are supported."

    # Check PDF magic bytes
    if not file_bytes.startswith(b"%PDF"):
        return False, "File does not appear to be a valid PDF."

    # Size check: max 10MB
    max_size = 10 * 1024 * 1024
    if len(file_bytes) > max_size:
        return False, f"File too large ({len(file_bytes) / 1024 / 1024:.1f}MB). Maximum is 10MB."

    return True, ""


def validate_job_description(text: str) -> Tuple[bool, str]:
    """
    Validate job description text input.
    Returns (is_valid, error_message).
    """
    if not text or not text.strip():
        return False, "Job description cannot be empty."

    if len(text.strip()) < 50:
        return False, "Job description is too short. Please provide at least 50 characters."

    if len(text) > 50000:
        return False, "Job description is too long. Maximum is 50,000 characters."

    return True, ""


def validate_api_key(key: str, provider: str = "gemini") -> Tuple[bool, str]:
    """
    Basic validation for API key format.
    """
    if not key or not key.strip():
        return False, f"No {provider} API key provided."

    if len(key.strip()) < 20:
        return False, f"Invalid {provider} API key format."

    return True, ""
