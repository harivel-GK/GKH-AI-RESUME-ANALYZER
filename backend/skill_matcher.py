# backend/skill_matcher.py
"""
Skill matching engine.
Compares resume skills against JD requirements using exact + fuzzy matching.
"""

import re
import logging
from typing import List, Set, Tuple, Dict
from utils.text_cleaner import normalize_skill

logger = logging.getLogger(__name__)


class SkillMatcher:
    """Matches resume skills against job description skills."""

    # Skill aliases / synonyms
    ALIASES = {
        "js": "javascript",
        "ts": "typescript",
        "py": "python",
        "ml": "machine learning",
        "dl": "deep learning",
        "ai": "artificial intelligence",
        "k8s": "kubernetes",
        "tf": "tensorflow",
        "sklearn": "scikit-learn",
        "scikit learn": "scikit-learn",
        "node": "node.js",
        "nodejs": "node.js",
        "react js": "react",
        "reactjs": "react",
        "vue js": "vue",
        "vuejs": "vue",
        "postgres": "postgresql",
        "mongo": "mongodb",
        "elastic": "elasticsearch",
        "amazon web services": "aws",
        "google cloud platform": "gcp",
        "microsoft azure": "azure",
    }

    def match(
        self,
        resume_skills: List[str],
        jd_skills: List[str],
        jd_keywords: List[str] = None,
    ) -> Dict:
        """
        Match resume skills against JD skills.
        Returns dict with matched, missing, extra skills and coverage %.
        """
        if not jd_skills:
            return {
                "matched": [],
                "missing": [],
                "extra": resume_skills[:],
                "coverage_pct": 0.0,
                "resume_normalized": set(),
                "jd_normalized": set(),
            }

        # Normalize all skills
        resume_norm = {self._normalize(s) for s in resume_skills if s}
        jd_norm = {self._normalize(s) for s in jd_skills if s}

        # Expand with aliases
        resume_expanded = self._expand_aliases(resume_norm)
        jd_expanded = self._expand_aliases(jd_norm)

        matched_norm = resume_expanded & jd_expanded
        missing_norm = jd_expanded - resume_expanded

        # Map normalized back to original display names
        matched = self._map_to_original(matched_norm, resume_skills)
        missing = self._map_to_original(missing_norm, jd_skills)
        extra = [s for s in resume_skills if self._normalize(s) not in jd_expanded]

        coverage = (len(matched) / len(jd_skills)) * 100 if jd_skills else 0.0

        return {
            "matched": sorted(matched),
            "missing": sorted(missing),
            "extra": sorted(extra),
            "coverage_pct": round(coverage, 1),
        }

    def _normalize(self, skill: str) -> str:
        """Normalize a skill name for matching."""
        s = normalize_skill(skill)
        return self.ALIASES.get(s, s)

    def _expand_aliases(self, skills: Set[str]) -> Set[str]:
        """Expand skill set with known aliases."""
        expanded = set(skills)
        for skill in list(skills):
            alias = self.ALIASES.get(skill)
            if alias:
                expanded.add(alias)
            # Reverse alias lookup
            for k, v in self.ALIASES.items():
                if v == skill:
                    expanded.add(k)
        return expanded

    def _map_to_original(self, normalized: Set[str], originals: List[str]) -> List[str]:
        """Map normalized skill names back to original display strings."""
        result = []
        for orig in originals:
            if self._normalize(orig) in normalized:
                result.append(orig)
        # Add any that were not in originals
        orig_norm = {self._normalize(o) for o in originals}
        for norm in normalized:
            if norm not in orig_norm:
                result.append(norm.title())
        return result
