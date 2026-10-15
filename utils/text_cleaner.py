# utils/text_cleaner.py
"""
Text preprocessing and cleaning utilities.
"""

import re
import unicodedata
from typing import List


def clean_text(text: str) -> str:
    """
    Clean and normalize raw text from PDF extraction.
    Removes excessive whitespace, special chars, and normalizes unicode.
    """
    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKD", text)

    # Replace non-printable / control characters with space
    text = re.sub(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]", " ", text)

    # Collapse multiple spaces/tabs
    text = re.sub(r"[ \t]+", " ", text)

    # Normalize multiple newlines (max 2)
    text = re.sub(r"\n{3,}", "\n\n", text)

    return text.strip()


def normalize_skill(skill: str) -> str:
    """
    Normalize a skill string for comparison:
    lowercase, strip whitespace, remove special chars.
    """
    skill = skill.lower().strip()
    skill = re.sub(r"[^a-z0-9\s+#\.]", "", skill)
    skill = re.sub(r"\s+", " ", skill)
    return skill


def extract_years(text: str) -> float:
    """
    Extract total years of experience from text.
    Handles patterns like ''5+ years'', ''3-5 years'', ''2 years of experience''.
    Returns the average/max found or 0.0.
    """
    patterns = [
        r"(\d+)\+?\s*(?:to|-)\s*(\d+)\s*years?",  # range: 3-5 years
        r"(\d+)\+\s*years?",                         # 5+ years
        r"(\d+)\s*years?\s*(?:of\s*)?(?:experience|exp)",  # 5 years experience
        r"(\d+)\s*years?",                            # plain: 5 years
    ]

    found = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for m in matches:
            if isinstance(m, tuple):
                nums = [float(x) for x in m if x]
                found.append(max(nums))
            else:
                found.append(float(m))

    return max(found) if found else 0.0


def extract_bullet_items(text: str) -> List[str]:
    """
    Extract bullet/list items from a block of text.
    """
    lines = text.split("\n")
    items = []
    for line in lines:
        line = line.strip()
        # Remove bullet markers
        line = re.sub(r"^[\u2022\u2023\u25e6\u2043\u2219\-\*\>\+\u2022\u25aa\u25a0\u25e6\u00b7]\s*", "", line)
        if len(line) > 3:
            items.append(line)
    return items


def tokenize_skills(skills_text: str) -> List[str]:
    """
    Tokenize a comma/newline/semicolon separated skills string into individual skills.
    """
    # Split on common delimiters
    parts = re.split(r"[,;|\n\r]+", skills_text)
    skills = []
    for p in parts:
        p = p.strip().strip("\u2022\u00b7\-*")
        if 2 <= len(p) <= 60:  # reasonable skill length
            skills.append(p.strip())
    return [s for s in skills if s]
