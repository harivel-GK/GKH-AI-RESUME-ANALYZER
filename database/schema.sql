-- AI Resume Analyzer Database Schema
-- SQLite

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
    skills TEXT,  -- JSON array
    education TEXT,  -- JSON array
    experience TEXT,  -- JSON array
    certifications TEXT,  -- JSON array
    total_experience_years REAL DEFAULT 0,
    highest_degree TEXT,
    uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_session) REFERENCES users(session_id)
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
    matched_skills TEXT,  -- JSON array
    missing_skills TEXT,  -- JSON array
    recommendation TEXT,
    ai_strengths TEXT,  -- JSON array
    ai_gaps TEXT,  -- JSON array
    ai_suggestions TEXT,  -- JSON array
    ai_ats_tips TEXT,  -- JSON array
    ai_summary TEXT,
    analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (resume_id) REFERENCES resumes(id)
);

CREATE TABLE IF NOT EXISTS skills (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    skill_name TEXT UNIQUE NOT NULL,
    category TEXT DEFAULT 'general',
    frequency INTEGER DEFAULT 1,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_resumes_session ON resumes(user_session);
CREATE INDEX IF NOT EXISTS idx_analysis_resume ON analysis_results(resume_id);
CREATE INDEX IF NOT EXISTS idx_skills_name ON skills(skill_name);
