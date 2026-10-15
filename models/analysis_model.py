# models/analysis_model.py
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime


@dataclass
class ScoreBreakdown:
    """Detailed score breakdown by category."""
    skills_score: float = 0.0       # 0-100
    experience_score: float = 0.0   # 0-100
    education_score: float = 0.0    # 0-100
    overall_score: float = 0.0      # 0-100 (weighted)
    ats_score: float = 0.0          # 0-100
    skill_coverage_pct: float = 0.0 # % of JD skills matched

    def compute_overall(self) -> float:
        """Compute weighted overall score: Skills 50%, Experience 30%, Education 20%."""
        self.overall_score = (
            self.skills_score * 0.50
            + self.experience_score * 0.30
            + self.education_score * 0.20
        )
        self.ats_score = round(self.overall_score, 1)
        return self.overall_score

    def get_recommendation(self) -> str:
        """Return match recommendation based on overall score."""
        if self.overall_score >= 80:
            return "Strong Match"
        elif self.overall_score >= 60:
            return "Moderate Match"
        else:
            return "Weak Match"

    def get_recommendation_color(self) -> str:
        """Return color associated with recommendation."""
        if self.overall_score >= 80:
            return "#00D4AA"
        elif self.overall_score >= 60:
            return "#F5A623"
        else:
            return "#FF4B4B"


@dataclass
class AnalysisResult:
    """Complete analysis result for a resume-JD pair."""
    resume_name: str = ""
    job_title: str = ""
    matched_skills: List[str] = field(default_factory=list)
    missing_skills: List[str] = field(default_factory=list)
    extra_skills: List[str] = field(default_factory=list)
    jd_required_skills: List[str] = field(default_factory=list)
    jd_preferred_skills: List[str] = field(default_factory=list)
    score: ScoreBreakdown = field(default_factory=ScoreBreakdown)
    ai_strengths: List[str] = field(default_factory=list)
    ai_gaps: List[str] = field(default_factory=list)
    ai_suggestions: List[str] = field(default_factory=list)
    ai_ats_tips: List[str] = field(default_factory=list)
    ai_summary: str = ""
    recommendation: str = ""
    analyzed_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return {
            "resume_name": self.resume_name,
            "job_title": self.job_title,
            "matched_skills": self.matched_skills,
            "missing_skills": self.missing_skills,
            "extra_skills": self.extra_skills,
            "jd_required_skills": self.jd_required_skills,
            "score_overall": self.score.overall_score,
            "score_skills": self.score.skills_score,
            "score_experience": self.score.experience_score,
            "score_education": self.score.education_score,
            "ats_score": self.score.ats_score,
            "ai_strengths": self.ai_strengths,
            "ai_gaps": self.ai_gaps,
            "ai_suggestions": self.ai_suggestions,
            "recommendation": self.recommendation,
            "analyzed_at": self.analyzed_at,
        }
