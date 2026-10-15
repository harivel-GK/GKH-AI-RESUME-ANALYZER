# models/resume_model.py
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResumeData:
    """Structured representation of a parsed resume."""
    raw_text: str = ""
    name: str = ""
    email: str = ""
    phone: str = ""
    linkedin: str = ""
    github: str = ""
    skills: List[str] = field(default_factory=list)
    education: List[dict] = field(default_factory=list)
    experience: List[dict] = field(default_factory=list)
    certifications: List[str] = field(default_factory=list)
    projects: List[str] = field(default_factory=list)
    summary: str = ""
    total_experience_years: float = 0.0
    highest_degree: str = ""

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "name": self.name,
            "email": self.email,
            "phone": self.phone,
            "linkedin": self.linkedin,
            "github": self.github,
            "skills": self.skills,
            "education": self.education,
            "experience": self.experience,
            "certifications": self.certifications,
            "projects": self.projects,
            "summary": self.summary,
            "total_experience_years": self.total_experience_years,
            "highest_degree": self.highest_degree,
        }
