# backend/jd_analyzer.py
"""
Job Description analyzer module.
Extracts required skills, experience, education requirements, and keywords.
"""

import re
import logging
from typing import List, Dict, Set
from utils.text_cleaner import clean_text, normalize_skill, extract_years, tokenize_skills
from backend.resume_parser import KNOWN_SKILLS

logger = logging.getLogger(__name__)


class JDAnalyzer:
    """Analyzes job description text to extract requirements."""

    def analyze(self, jd_text: str) -> Dict:
        """
        Main entry: parse job description into structured requirements.
        Returns dict with required_skills, preferred_skills, experience_years,
        education_requirement, keywords, job_title.
        """
        jd_text = clean_text(jd_text)

        return {
            "job_title": self._extract_job_title(jd_text),
            "required_skills": self._extract_required_skills(jd_text),
            "preferred_skills": self._extract_preferred_skills(jd_text),
            "experience_years": self._extract_experience_requirement(jd_text),
            "education_requirement": self._extract_education_requirement(jd_text),
            "keywords": self._extract_keywords(jd_text),
            "all_skills": self._extract_all_skills(jd_text),
        }

    def _extract_job_title(self, text: str) -> str:
        """Extract job title from first meaningful line."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:3]:
            if 3 <= len(line.split()) <= 8:
                return line.strip()
        return lines[0][:80] if lines else "Position"

    def _extract_required_skills(self, text: str) -> List[str]:
        """Extract skills from Required/Must-have sections."""
        required_section = self._extract_section(text, [
            "required", "requirements", "must have", "must-have",
            "qualifications", "what you need", "minimum"
        ])
        target_text = required_section if required_section else text
        return self._extract_skills_from_text(target_text)

    def _extract_preferred_skills(self, text: str) -> List[str]:
        """Extract skills from Preferred/Nice-to-have sections."""
        preferred_section = self._extract_section(text, [
            "preferred", "nice to have", "nice-to-have", "bonus",
            "additional", "plus", "desired"
        ])
        if not preferred_section:
            return []
        return self._extract_skills_from_text(preferred_section)

    def _extract_all_skills(self, text: str) -> List[str]:
        """Extract all skills mentioned in JD (union of required + preferred + full text scan)."""
        skills = set()

        # Scan full text against known skill taxonomy
        text_lower = text.lower()
        for skill in KNOWN_SKILLS:
            pattern = r"(?<![a-z])" + re.escape(skill) + r"(?![a-z])"
            if re.search(pattern, text_lower):
                skills.add(skill)

        # Also extract from any skills section
        skills_section = self._extract_section(text, [
            "skills", "technical skills", "technologies", "tech stack"
        ])
        if skills_section:
            for s in tokenize_skills(skills_section):
                normalized = normalize_skill(s)
                if 2 <= len(normalized) <= 50:
                    skills.add(normalized)

        return sorted(list(skills))

    def _extract_skills_from_text(self, text: str) -> List[str]:
        """Extract skill names from a text block."""
        skills = set()
        text_lower = text.lower()

        for skill in KNOWN_SKILLS:
            pattern = r"(?<![a-z])" + re.escape(skill) + r"(?![a-z])"
            if re.search(pattern, text_lower):
                skills.add(skill)

        # Also tokenize comma-separated items
        for s in tokenize_skills(text):
            normalized = normalize_skill(s)
            if 2 <= len(normalized) <= 50:
                skills.add(normalized)

        return sorted(list(skills))

    def _extract_experience_requirement(self, text: str) -> float:
        """Extract required years of experience."""
        return extract_years(text)

    def _extract_education_requirement(self, text: str) -> str:
        """Extract required education level."""
        degree_patterns = [
            (r"ph\.?d|doctorate", "PhD"),
            (r"master|mba|m\.?sc|m\.?tech|ms\b", "Master''s Degree"),
            (r"bachelor|b\.?sc|b\.?tech|b\.?e\b|bs\b|ba\b", "Bachelor''s Degree"),
            (r"associate", "Associate Degree"),
            (r"diploma", "Diploma"),
            (r"high school|secondary", "High School"),
        ]
        text_lower = text.lower()
        for pattern, label in degree_patterns:
            if re.search(pattern, text_lower):
                return label
        return ""

    def _extract_keywords(self, text: str) -> List[str]:
        """Extract important domain keywords from JD."""
        # Remove common words
        stop_words = {
            "the", "and", "for", "are", "with", "this", "that", "have",
            "will", "you", "our", "your", "team", "work", "role", "job",
            "position", "candidate", "company", "must", "able", "experience",
            "year", "years", "strong", "good", "plus", "etc", "such", "use",
        }
        words = re.findall(r"\b[a-zA-Z][a-zA-Z+#\.]{2,}\b", text)
        keywords = []
        seen = set()
        for w in words:
            w_lower = w.lower()
            if w_lower not in stop_words and w_lower not in seen:
                keywords.append(w)
                seen.add(w_lower)

        return keywords[:50]  # top 50 keywords

    def _extract_section(self, text: str, headers: List[str]) -> str:
        """Extract content of named section from JD text."""
        for header in headers:
            pattern = r"(?i)(?:^|\n)\s*" + re.escape(header) + r"[s]?\s*[:\-]?\s*\n(.*?)(?=\n\s*[A-Z][A-Za-z ]+[:\-]|$)"
            match = re.search(pattern, text, re.DOTALL | re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return ""
