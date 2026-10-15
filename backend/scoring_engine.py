# backend/scoring_engine.py
"""
ATS Scoring Engine.
Calculates weighted match score: Skills 50%, Experience 30%, Education 20%.
"""

import logging
from typing import Dict, List
from models.analysis_model import ScoreBreakdown

logger = logging.getLogger(__name__)

DEGREE_HIERARCHY = {
    "phd": 5, "doctorate": 5,
    "master": 4, "mba": 4, "m.sc": 4, "m.tech": 4, "ms": 4,
    "bachelor": 3, "b.sc": 3, "b.tech": 3, "b.e": 3, "bca": 3,
    "associate": 2,
    "diploma": 1,
    "": 0,
}


class ScoringEngine:
    """Calculates ATS match scores with weighted components."""

    SKILL_WEIGHT = 0.50
    EXPERIENCE_WEIGHT = 0.30
    EDUCATION_WEIGHT = 0.20

    def calculate(
        self,
        skill_match: Dict,
        resume_experience_years: float,
        jd_experience_years: float,
        resume_highest_degree: str,
        jd_education_requirement: str,
    ) -> ScoreBreakdown:
        """
        Calculate complete score breakdown.
        Returns ScoreBreakdown with all scores computed.
        """
        score = ScoreBreakdown()

        score.skill_coverage_pct = skill_match.get("coverage_pct", 0.0)
        score.skills_score = self._calc_skills_score(skill_match)
        score.experience_score = self._calc_experience_score(
            resume_experience_years, jd_experience_years
        )
        score.education_score = self._calc_education_score(
            resume_highest_degree, jd_education_requirement
        )

        score.compute_overall()
        return score

    def _calc_skills_score(self, skill_match: Dict) -> float:
        """
        Calculate skill match score (0-100).
        Based on coverage % with bonus for extra relevant skills.
        """
        coverage = skill_match.get("coverage_pct", 0.0)
        matched = len(skill_match.get("matched", []))
        total_jd = matched + len(skill_match.get("missing", []))

        if total_jd == 0:
            return 70.0  # No skills specified: give neutral score

        base = coverage  # 0-100

        # Bonus: extra skills show depth (up to +10)
        extra = len(skill_match.get("extra", []))
        bonus = min(10, extra * 0.5)

        return min(100.0, round(base + bonus, 1))

    def _calc_experience_score(self, resume_years: float, jd_years: float) -> float:
        """
        Calculate experience match score (0-100).
        """
        if jd_years <= 0:
            return 80.0  # No requirement specified

        if resume_years <= 0:
            return 20.0  # No experience found in resume

        ratio = resume_years / jd_years

        if ratio >= 1.0:
            # Meets or exceeds requirement
            return min(100.0, 75.0 + (ratio - 1.0) * 10)
        else:
            # Below requirement
            return max(10.0, ratio * 75.0)

    def _calc_education_score(self, resume_degree: str, jd_requirement: str) -> float:
        """
        Calculate education match score (0-100).
        """
        if not jd_requirement:
            return 80.0  # No requirement

        resume_level = self._degree_level(resume_degree)
        jd_level = self._degree_level(jd_requirement)

        if jd_level == 0:
            return 80.0

        if resume_level == 0:
            return 30.0  # No degree info found

        if resume_level >= jd_level:
            # Meets or exceeds
            bonus = min(20, (resume_level - jd_level) * 10)
            return min(100.0, 80.0 + bonus)
        else:
            # Below requirement
            ratio = resume_level / jd_level
            return max(20.0, ratio * 70.0)

    def _degree_level(self, degree_text: str) -> int:
        """Map degree text to numeric level."""
        if not degree_text:
            return 0
        text_lower = degree_text.lower()
        for key, level in DEGREE_HIERARCHY.items():
            if key and key in text_lower:
                return level
        return 0
