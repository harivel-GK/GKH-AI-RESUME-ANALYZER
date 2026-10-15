# services/ai_service.py
"""
AI Analysis Service using Google Gemini API.
Generates resume strengths, gaps, improvement suggestions, and ATS tips.
Falls back gracefully if no API key is provided.
"""

import os
import json
import logging
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

GEMINI_PROMPT_TEMPLATE = """
You are an expert ATS (Applicant Tracking System) analyst and career coach.

RESUME TEXT:
{resume_text}

JOB DESCRIPTION:
{job_description}

CURRENT MATCH SCORE: {overall_score:.1f}/100
MATCHED SKILLS: {matched_skills}
MISSING SKILLS: {missing_skills}

Please analyze this resume against the job description and provide:

1. STRENGTHS (3-5 bullet points): What the candidate does well for this role
2. GAPS (3-5 bullet points): Missing qualifications and areas of concern  
3. IMPROVEMENT_SUGGESTIONS (4-6 bullet points): Specific, actionable ways to improve the resume
4. ATS_TIPS (3-5 bullet points): How to optimize the resume for ATS systems
5. SUMMARY (2-3 sentences): Overall assessment and recommendation

Respond ONLY with valid JSON in this exact format:
{{
    "strengths": ["point 1", "point 2", "point 3"],
    "gaps": ["gap 1", "gap 2", "gap 3"],
    "improvement_suggestions": ["suggestion 1", "suggestion 2", "suggestion 3"],
    "ats_tips": ["tip 1", "tip 2", "tip 3"],
    "summary": "Overall assessment text here."
}}
"""


class AIService:
    """Gemini API-powered AI analysis service."""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY", "")
        self.model = None
        self._initialized = False
        self._init_client()

    def _init_client(self):
        """Initialize Gemini API client."""
        if not self.api_key:
            logger.warning("No GEMINI_API_KEY found. AI analysis will use offline mode.")
            return

        try:
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            self.model = genai.GenerativeModel("gemini-1.5-flash")
            self._initialized = True
            logger.info("Gemini API client initialized successfully.")
        except ImportError:
            logger.error("google-generativeai not installed. Run: pip install google-generativeai")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini API: {e}")

    def is_available(self) -> bool:
        """Check if AI service is ready."""
        return self._initialized and self.model is not None

    def analyze(
        self,
        resume_text: str,
        job_description: str,
        matched_skills: List[str],
        missing_skills: List[str],
        overall_score: float,
    ) -> Dict:
        """
        Generate AI-powered resume analysis.
        Returns dict with strengths, gaps, suggestions, ats_tips, summary.
        Falls back to rule-based analysis if API unavailable.
        """
        if not self.is_available():
            return self._offline_analysis(
                matched_skills, missing_skills, overall_score
            )

        try:
            prompt = GEMINI_PROMPT_TEMPLATE.format(
                resume_text=resume_text[:3000],  # Limit tokens
                job_description=job_description[:2000],
                overall_score=overall_score,
                matched_skills=", ".join(matched_skills[:15]),
                missing_skills=", ".join(missing_skills[:15]),
            )

            response = self.model.generate_content(
                prompt,
                generation_config={
                    "temperature": 0.7,
                    "max_output_tokens": 1500,
                    "response_mime_type": "application/json",
                },
            )

            response_text = response.text.strip()

            # Parse JSON response
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:]

            result = json.loads(response_text)
            return self._validate_response(result)

        except json.JSONDecodeError as e:
            logger.warning(f"JSON parse error in AI response: {e}")
            return self._offline_analysis(matched_skills, missing_skills, overall_score)
        except Exception as e:
            logger.error(f"AI analysis failed: {e}")
            return self._offline_analysis(matched_skills, missing_skills, overall_score)

    def _offline_analysis(
        self,
        matched_skills: List[str],
        missing_skills: List[str],
        overall_score: float,
    ) -> Dict:
        """Rule-based fallback analysis when API is unavailable."""
        strengths = []
        gaps = []
        suggestions = []
        ats_tips = []

        if matched_skills:
            strengths.append(
                f"Strong skill alignment with {len(matched_skills)} matching skills: "
                + ", ".join(matched_skills[:5])
            )
        if overall_score >= 70:
            strengths.append("Overall resume demonstrates good fit for this position.")
        if overall_score >= 80:
            strengths.append("Excellent match score indicating strong candidacy.")

        if missing_skills:
            gaps.append(
                f"Missing {len(missing_skills)} key required skills: "
                + ", ".join(missing_skills[:5])
            )
        if overall_score < 60:
            gaps.append("Significant gaps exist between resume and job requirements.")

        suggestions.append("Tailor your resume specifically for this job posting.")
        suggestions.append("Add quantifiable achievements (e.g., 'Increased performance by 30%').")
        suggestions.append("Include all keywords from the job description naturally in your resume.")
        if missing_skills:
            suggestions.append(
                f"Consider acquiring skills in: {', '.join(missing_skills[:3])}"
            )
        suggestions.append("Use action verbs to start bullet points (Led, Built, Implemented, etc.).")

        ats_tips.append("Use standard section headers: Skills, Experience, Education.")
        ats_tips.append("Avoid tables, graphics, and columns that ATS systems cannot parse.")
        ats_tips.append("Include exact keywords from the job description in your resume.")
        ats_tips.append("Save your resume as a clean, text-based PDF.")

        if overall_score >= 80:
            summary = (
                f"Excellent match! Your resume aligns strongly with this role "
                f"(Score: {overall_score:.1f}/100). You have most required qualifications."
            )
        elif overall_score >= 60:
            summary = (
                f"Moderate match (Score: {overall_score:.1f}/100). Your resume shows potential "
                f"but has some gaps. Address the missing skills and tailor your content."
            )
        else:
            summary = (
                f"Low match score ({overall_score:.1f}/100). Significant improvements needed. "
                f"Focus on acquiring the missing skills and rewriting for this specific role."
            )

        return {
            "strengths": strengths if strengths else ["Resume has been submitted successfully."],
            "gaps": gaps if gaps else ["No major gaps detected without AI analysis."],
            "improvement_suggestions": suggestions,
            "ats_tips": ats_tips,
            "summary": summary,
        }

    def _validate_response(self, data: Dict) -> Dict:
        """Ensure response has all required fields."""
        required_keys = ["strengths", "gaps", "improvement_suggestions", "ats_tips", "summary"]
        for key in required_keys:
            if key not in data:
                data[key] = [] if key != "summary" else "Analysis completed."
            if key != "summary" and not isinstance(data[key], list):
                data[key] = [str(data[key])]
        return data
