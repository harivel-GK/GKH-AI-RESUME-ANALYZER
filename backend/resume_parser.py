# backend/resume_parser.py
"""
Resume parsing module.
Extracts structured data: name, contact, skills, education, experience, etc.
"""

import re
import logging
from typing import List, Dict, Tuple
from models.resume_model import ResumeData
from utils.text_cleaner import clean_text, normalize_skill, extract_years, tokenize_skills

logger = logging.getLogger(__name__)

# --- Skill Taxonomy ---
KNOWN_SKILLS = [
    # Programming Languages
    "python", "java", "javascript", "typescript", "c++", "c#", "c", "go", "golang",
    "rust", "ruby", "php", "swift", "kotlin", "scala", "r", "matlab", "perl",
    "bash", "shell", "powershell", "dart", "elixir", "haskell", "lua", "julia",
    # Web Frameworks
    "react", "reactjs", "react.js", "angular", "angularjs", "vue", "vue.js",
    "next.js", "nuxt.js", "svelte", "django", "flask", "fastapi", "express",
    "express.js", "nestjs", "spring", "spring boot", "rails", "laravel", "asp.net",
    # Data / ML / AI
    "machine learning", "deep learning", "nlp", "natural language processing",
    "computer vision", "tensorflow", "pytorch", "keras", "scikit-learn",
    "pandas", "numpy", "matplotlib", "seaborn", "plotly", "opencv", "huggingface",
    "langchain", "openai", "llm", "generative ai", "transformers", "bert", "gpt",
    # Databases
    "sql", "mysql", "postgresql", "mongodb", "redis", "elasticsearch", "cassandra",
    "dynamodb", "firebase", "oracle", "mssql", "sqlite", "neo4j", "influxdb",
    # Cloud & DevOps
    "aws", "azure", "gcp", "google cloud", "docker", "kubernetes", "terraform",
    "ansible", "jenkins", "ci/cd", "github actions", "gitlab ci", "helm", "istio",
    "linux", "unix", "nginx", "apache",
    # Data Engineering
    "spark", "hadoop", "kafka", "airflow", "dbt", "snowflake", "databricks",
    "etl", "data pipeline", "bigquery", "redshift", "hive", "pig",
    # Tools
    "git", "github", "gitlab", "jira", "confluence", "agile", "scrum", "kanban",
    "rest api", "graphql", "grpc", "microservices", "api", "postman", "swagger",
    # Mobile
    "android", "ios", "react native", "flutter", "xamarin",
    # Design
    "figma", "sketch", "adobe xd", "photoshop", "illustrator", "ux", "ui",
    # Security
    "cybersecurity", "penetration testing", "ethical hacking", "ssl", "oauth",
    # Analytics
    "tableau", "power bi", "looker", "excel", "google analytics", "a/b testing",
]

DEGREE_LEVELS = {
    "phd": 5, "ph.d": 5, "doctorate": 5, "doctoral": 5,
    "master": 4, "msc": 4, "m.sc": 4, "mba": 4, "m.tech": 4, "m.e": 4, "ms": 4,
    "bachelor": 3, "bsc": 3, "b.sc": 3, "b.tech": 3, "b.e": 3, "be": 3, "ba": 3, "bca": 3,
    "associate": 2, "diploma": 1,
}


class ResumeParser:
    """Parses raw resume text into structured ResumeData."""

    def parse(self, text: str, filename: str = "") -> ResumeData:
        """Main entry point: parse raw text into structured ResumeData."""
        text = clean_text(text)
        resume = ResumeData(raw_text=text)

        resume.name = self._extract_name(text)
        resume.email = self._extract_email(text)
        resume.phone = self._extract_phone(text)
        resume.linkedin = self._extract_linkedin(text)
        resume.github = self._extract_github(text)
        resume.skills = self._extract_skills(text)
        resume.education = self._extract_education(text)
        resume.experience = self._extract_experience(text)
        resume.certifications = self._extract_certifications(text)
        resume.projects = self._extract_projects(text)
        resume.total_experience_years = self._calculate_experience_years(resume.experience, text)
        resume.highest_degree = self._get_highest_degree(resume.education)

        return resume

    def _extract_name(self, text: str) -> str:
        """Extract candidate name from top of resume."""
        lines = [l.strip() for l in text.split("\n") if l.strip()]
        for line in lines[:5]:
            # Skip lines that look like contact info or section headers
            if re.search(r"[@|\d{3}|resume|curriculum|cv]", line, re.IGNORECASE):
                continue
            # Name: typically 2-4 words, each capitalized
            words = line.split()
            if 2 <= len(words) <= 5 and all(w[0].isupper() for w in words if w):
                # Avoid common section headers
                if not any(kw in line.lower() for kw in [
                    "objective", "summary", "profile", "experience", "education",
                    "skill", "project", "contact"
                ]):
                    return line.strip()
        return lines[0][:50] if lines else ""

    def _extract_email(self, text: str) -> str:
        """Extract email address."""
        match = re.search(
            r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}", text
        )
        return match.group(0) if match else ""

    def _extract_phone(self, text: str) -> str:
        """Extract phone number."""
        patterns = [
            r"\+?\d[\d\s\-\.\(\)]{8,15}\d",
            r"\(?\d{3}\)?[\s\-\.]?\d{3}[\s\-\.]?\d{4}",
        ]
        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(0).strip()
        return ""

    def _extract_linkedin(self, text: str) -> str:
        """Extract LinkedIn profile URL."""
        match = re.search(
            r"(?:linkedin\.com/in/|linkedin:\s*)([a-zA-Z0-9\-]+)", text, re.IGNORECASE
        )
        return f"linkedin.com/in/{match.group(1)}" if match else ""

    def _extract_github(self, text: str) -> str:
        """Extract GitHub profile URL."""
        match = re.search(
            r"(?:github\.com/)([a-zA-Z0-9\-]+)", text, re.IGNORECASE
        )
        return f"github.com/{match.group(1)}" if match else ""

    def _extract_skills(self, text: str) -> List[str]:
        """Extract skills using section detection + known taxonomy."""
        skills = set()

        # Try to find Skills section first
        skills_section = self._extract_section(text, [
            "skills", "technical skills", "core competencies",
            "technologies", "tech stack", "tools"
        ])

        if skills_section:
            # Parse skills from section
            section_skills = tokenize_skills(skills_section)
            for s in section_skills:
                normalized = normalize_skill(s)
                if 2 <= len(normalized) <= 50:
                    skills.add(s.strip())

        # Also scan full text for known skill keywords
        text_lower = text.lower()
        for skill in KNOWN_SKILLS:
            # Word boundary match
            pattern = r"(?<![a-z])" + re.escape(skill) + r"(?![a-z])"
            if re.search(pattern, text_lower):
                # Prefer original casing from text
                skills.add(skill.title() if not "+" in skill and not "." in skill else skill.upper())

        return sorted(list(skills))

    def _extract_education(self, text: str) -> List[Dict]:
        """Extract education entries."""
        section = self._extract_section(text, ["education", "academic", "qualification"])
        if not section:
            section = text

        entries = []
        degree_pattern = r"(?i)(ph\.?d|doctorate|master|mba|m\.?sc|m\.?tech|bachelor|b\.?sc|b\.?tech|b\.?e|bca|associate|diploma)[^\.\n]*"
        matches = re.finditer(degree_pattern, section)

        for m in matches:
            degree_text = m.group(0).strip()
            # Find nearby university name
            context = section[max(0, m.start() - 100):m.end() + 200]
            year_match = re.search(r"(19|20)\d{2}", context)
            year = year_match.group(0) if year_match else ""

            entries.append({
                "degree": degree_text[:100],
                "year": year,
                "raw": context[:200].strip(),
            })

        return entries[:5]  # Cap at 5 entries

    def _extract_experience(self, text: str) -> List[Dict]:
        """Extract work experience entries."""
        section = self._extract_section(text, [
            "experience", "work experience", "employment", "work history",
            "professional experience", "career"
        ])
        if not section:
            return []

        entries = []
        # Split on date patterns that indicate new job entries
        blocks = re.split(
            r"\n(?=.*(?:19|20)\d{2})", section
        )

        for block in blocks[:10]:
            block = block.strip()
            if len(block) < 20:
                continue

            lines = [l.strip() for l in block.split("\n") if l.strip()]
            title = lines[0][:100] if lines else ""
            company = lines[1][:100] if len(lines) > 1 else ""

            date_match = re.search(
                r"(\w+ ?\d{4}|\d{4})\s*[-to]+\s*(\w+ ?\d{4}|present|current|now)",
                block, re.IGNORECASE
            )
            date_range = date_match.group(0) if date_match else ""

            entries.append({
                "title": title,
                "company": company,
                "date_range": date_range,
                "description": block[:500],
            })

        return entries

    def _extract_certifications(self, text: str) -> List[str]:
        """Extract certifications."""
        section = self._extract_section(text, [
            "certification", "certifications", "certificates", "credentials", "licenses"
        ])
        if not section:
            # Look for cert keywords in full text
            pattern = r"(?i)(?:certified|certification|certificate)[^\n]{3,80}"
            matches = re.findall(pattern, text)
            return matches[:10]

        lines = [l.strip() for l in section.split("\n") if l.strip() and len(l.strip()) > 5]
        return lines[:10]

    def _extract_projects(self, text: str) -> List[str]:
        """Extract project titles/descriptions."""
        section = self._extract_section(text, [
            "projects", "personal projects", "academic projects",
            "portfolio", "side projects"
        ])
        if not section:
            return []

        lines = [l.strip() for l in section.split("\n") if l.strip() and len(l.strip()) > 5]
        return lines[:10]

    def _extract_section(self, text: str, headers: List[str]) -> str:
        """Extract content of a named section from resume text."""
        section_pattern = r"(?i)^({headers})\s*[:\-]?\s*$".format(
            headers="|".join(re.escape(h) for h in headers)
        )
        common_next = [
            "experience", "education", "skills", "projects", "certifications",
            "summary", "objective", "awards", "publications", "references",
            "languages", "interests", "contact"
        ]
        next_pattern = r"(?im)^({}) *[:\-]?$".format("|".join(common_next))

        lines = text.split("\n")
        start = -1

        for i, line in enumerate(lines):
            if re.match(section_pattern, line.strip(), re.IGNORECASE):
                start = i + 1
                break

        if start == -1:
            return ""

        # Find end: next section header
        section_lines = lines[start:]
        end = len(section_lines)
        for j, line in enumerate(section_lines):
            if j > 0 and re.match(next_pattern, line.strip(), re.IGNORECASE):
                end = j
                break

        return "\n".join(section_lines[:end]).strip()

    def _calculate_experience_years(self, experience: List[Dict], raw_text: str) -> float:
        """Calculate total years of experience."""
        # Try to extract from experience entries
        total = 0.0
        for exp in experience:
            date_range = exp.get("date_range", "")
            if not date_range:
                continue
            years = re.findall(r"(19|20)(\d{2})", date_range)
            if len(years) >= 2:
                year_nums = [int(y[0] + y[1]) for y in years]
                diff = max(year_nums) - min(year_nums)
                total += max(0, diff)

        if total > 0:
            return min(total, 40.0)  # cap at 40 years

        # Fallback: scan raw text for experience mentions
        return extract_years(raw_text)

    def _get_highest_degree(self, education: List[Dict]) -> str:
        """Determine highest degree from education list."""
        if not education:
            return ""

        best_level = 0
        best_degree = ""

        for edu in education:
            degree_text = edu.get("degree", "").lower()
            for degree, level in DEGREE_LEVELS.items():
                if degree in degree_text and level > best_level:
                    best_level = level
                    best_degree = edu.get("degree", "")

        return best_degree
