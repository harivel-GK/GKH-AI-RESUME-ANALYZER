# database/db_manager.py
"""
SQLite database manager for AI Resume Analyzer.
Handles all CRUD operations for Users, Resumes, AnalysisResults, and Skills.
"""

import sqlite3
import json
import os
import logging
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent / "resume_analyzer.db"
SCHEMA_PATH = Path(__file__).parent / "schema.sql"


class DatabaseManager:
    """Manages SQLite database operations."""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or str(DB_PATH)
        self._ensure_db()

    def _get_connection(self) -> sqlite3.Connection:
        """Get a database connection with row_factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        return conn

    def _ensure_db(self):
        """Initialize database with schema if not exists."""
        try:
            with self._get_connection() as conn:
                if SCHEMA_PATH.exists():
                    schema = SCHEMA_PATH.read_text(encoding="utf-8")
                    conn.executescript(schema)
                else:
                    self._create_schema_inline(conn)
                conn.commit()
            logger.info(f"Database initialized at {self.db_path}")
        except Exception as e:
            logger.error(f"Database init error: {e}")
            raise

    def _create_schema_inline(self, conn: sqlite3.Connection):
        """Fallback: create schema directly if SQL file not found."""
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS resumes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_session TEXT NOT NULL,
                filename TEXT NOT NULL,
                raw_text TEXT,
                parsed_name TEXT,
                parsed_email TEXT,
                parsed_phone TEXT,
                skills TEXT,
                education TEXT,
                experience TEXT,
                certifications TEXT,
                total_experience_years REAL DEFAULT 0,
                highest_degree TEXT,
                uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS analysis_results (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                resume_id INTEGER NOT NULL,
                job_title TEXT,
                job_description TEXT,
                overall_score REAL,
                skills_score REAL,
                experience_score REAL,
                education_score REAL,
                ats_score REAL,
                matched_skills TEXT,
                missing_skills TEXT,
                recommendation TEXT,
                ai_strengths TEXT,
                ai_gaps TEXT,
                ai_suggestions TEXT,
                ai_ats_tips TEXT,
                ai_summary TEXT,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
            CREATE TABLE IF NOT EXISTS skills (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                skill_name TEXT UNIQUE NOT NULL,
                category TEXT DEFAULT 'general',
                frequency INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            );
        """)

    # --- Users ---

    def upsert_user(self, session_id: str) -> int:
        """Create or update a user session. Returns user id."""
        with self._get_connection() as conn:
            conn.execute(
                """INSERT INTO users (session_id, last_active)
                   VALUES (?, CURRENT_TIMESTAMP)
                   ON CONFLICT(session_id) DO UPDATE SET last_active=CURRENT_TIMESTAMP""",
                (session_id,),
            )
            row = conn.execute(
                "SELECT id FROM users WHERE session_id = ?", (session_id,)
            ).fetchone()
            return row["id"] if row else -1

    # --- Resumes ---

    def save_resume(
        self,
        session_id: str,
        filename: str,
        raw_text: str,
        parsed_data: dict,
    ) -> int:
        """Save a parsed resume. Returns resume id."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO resumes
                   (user_session, filename, raw_text, parsed_name, parsed_email,
                    parsed_phone, skills, education, experience, certifications,
                    total_experience_years, highest_degree)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    session_id,
                    filename,
                    raw_text,
                    parsed_data.get("name", ""),
                    parsed_data.get("email", ""),
                    parsed_data.get("phone", ""),
                    json.dumps(parsed_data.get("skills", [])),
                    json.dumps(parsed_data.get("education", [])),
                    json.dumps(parsed_data.get("experience", [])),
                    json.dumps(parsed_data.get("certifications", [])),
                    parsed_data.get("total_experience_years", 0),
                    parsed_data.get("highest_degree", ""),
                ),
            )
            return cursor.lastrowid

    def get_resumes_by_session(self, session_id: str) -> List[Dict]:
        """Get all resumes for a session."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT id, filename, parsed_name, total_experience_years,
                          highest_degree, uploaded_at
                   FROM resumes WHERE user_session = ?
                   ORDER BY uploaded_at DESC""",
                (session_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_resume_by_id(self, resume_id: int) -> Optional[Dict]:
        """Get full resume details by id."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM resumes WHERE id = ?", (resume_id,)
            ).fetchone()
            if row:
                d = dict(row)
                for field in ["skills", "education", "experience", "certifications"]:
                    if d.get(field):
                        try:
                            d[field] = json.loads(d[field])
                        except Exception:
                            d[field] = []
                return d
            return None

    # --- Analysis Results ---

    def save_analysis(
        self,
        resume_id: int,
        job_title: str,
        job_description: str,
        result: dict,
    ) -> int:
        """Save analysis result. Returns analysis id."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                """INSERT INTO analysis_results
                   (resume_id, job_title, job_description, overall_score,
                    skills_score, experience_score, education_score, ats_score,
                    matched_skills, missing_skills, recommendation,
                    ai_strengths, ai_gaps, ai_suggestions, ai_ats_tips, ai_summary)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    resume_id,
                    job_title,
                    job_description[:2000],
                    result.get("score_overall", 0),
                    result.get("score_skills", 0),
                    result.get("score_experience", 0),
                    result.get("score_education", 0),
                    result.get("ats_score", 0),
                    json.dumps(result.get("matched_skills", [])),
                    json.dumps(result.get("missing_skills", [])),
                    result.get("recommendation", ""),
                    json.dumps(result.get("ai_strengths", [])),
                    json.dumps(result.get("ai_gaps", [])),
                    json.dumps(result.get("ai_suggestions", [])),
                    json.dumps(result.get("ai_ats_tips", [])),
                    result.get("ai_summary", ""),
                ),
            )
            return cursor.lastrowid

    def get_analysis_history(self, session_id: str, limit: int = 20) -> List[Dict]:
        """Get analysis history for a session."""
        with self._get_connection() as conn:
            rows = conn.execute(
                """SELECT ar.id, r.filename, ar.job_title, ar.overall_score,
                          ar.ats_score, ar.recommendation, ar.analyzed_at
                   FROM analysis_results ar
                   JOIN resumes r ON ar.resume_id = r.id
                   WHERE r.user_session = ?
                   ORDER BY ar.analyzed_at DESC
                   LIMIT ?""",
                (session_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_analysis_by_id(self, analysis_id: int) -> Optional[Dict]:
        """Get full analysis details by id."""
        with self._get_connection() as conn:
            row = conn.execute(
                "SELECT * FROM analysis_results WHERE id = ?", (analysis_id,)
            ).fetchone()
            if row:
                d = dict(row)
                for field in ["matched_skills", "missing_skills", "ai_strengths",
                               "ai_gaps", "ai_suggestions", "ai_ats_tips"]:
                    if d.get(field):
                        try:
                            d[field] = json.loads(d[field])
                        except Exception:
                            d[field] = []
                return d
            return None

    def get_stats(self, session_id: str) -> Dict:
        """Get summary statistics for a session."""
        with self._get_connection() as conn:
            stats = conn.execute(
                """SELECT COUNT(*) as total_analyses,
                          AVG(ar.overall_score) as avg_score,
                          MAX(ar.overall_score) as best_score
                   FROM analysis_results ar
                   JOIN resumes r ON ar.resume_id = r.id
                   WHERE r.user_session = ?""",
                (session_id,),
            ).fetchone()
            return dict(stats) if stats else {}

    # --- Skills ---

    def upsert_skills(self, skills: List[str]):
        """Insert or increment frequency of known skills."""
        with self._get_connection() as conn:
            for skill in skills:
                conn.execute(
                    """INSERT INTO skills (skill_name) VALUES (?)
                       ON CONFLICT(skill_name) DO UPDATE SET frequency = frequency + 1""",
                    (skill.lower().strip(),),
                )

    def get_top_skills(self, limit: int = 20) -> List[Dict]:
        """Get most frequently seen skills."""
        with self._get_connection() as conn:
            rows = conn.execute(
                "SELECT skill_name, frequency FROM skills ORDER BY frequency DESC LIMIT ?",
                (limit,),
            ).fetchall()
            return [dict(r) for r in rows]
