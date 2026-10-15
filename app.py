# app.py
"""
AI Resume Analyzer - Streamlit Application Entrypoint
A state-of-the-art intelligent resume screening and match evaluation platform.
"""

import streamlit as st
import os
import uuid
import json
import base64
import pandas as pd
from datetime import datetime
from dotenv import load_dotenv

# Import backend components
from backend.pdf_extractor import PDFExtractor
from backend.resume_parser import ResumeParser
from backend.jd_analyzer import JDAnalyzer
from backend.skill_matcher import SkillMatcher
from backend.scoring_engine import ScoringEngine
from database.db_manager import DatabaseManager
from services.ai_service import AIService
from services.report_service import ReportService
import frontend.components as ui

# Load environment variables
load_dotenv()

# --- Page Configuration ---
st.set_page_config(
    page_title="GKH AI RESUME ANALYZER",
    page_icon="✨",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Initialize Session State ---
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "gemini_api_key" not in st.session_state:
    st.session_state.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

if "current_analysis" not in st.session_state:
    st.session_state.current_analysis = None

if "resume_filename" not in st.session_state:
    st.session_state.resume_filename = ""

if "raw_resume_text" not in st.session_state:
    st.session_state.raw_resume_text = ""

if "parsed_resume" not in st.session_state:
    st.session_state.parsed_resume = None

if "batch_results" not in st.session_state:
    st.session_state.batch_results = []

if "show_leaderboard" not in st.session_state:
    st.session_state.show_leaderboard = False

# --- Initialize DB Manager & Services ---
db = DatabaseManager()
db.upsert_user(st.session_state.session_id)
pdf_extractor = PDFExtractor()
resume_parser = ResumeParser()
jd_analyzer = JDAnalyzer()
skill_matcher = SkillMatcher()
scoring_engine = ScoringEngine()
report_service = ReportService()

# --- Load and Inject Custom CSS ---
def inject_custom_css():
    css_path = os.path.join("frontend", "styles.css")
    if os.path.exists(css_path):
        with open(css_path, "r", encoding="utf-8") as f:
            css = f.read()
        st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)
    else:
        st.warning("Custom CSS file not found. Falling back to default Streamlit theme.")

inject_custom_css()

# --- Sidebar Configuration ---
st.sidebar.markdown(
    """
    <div style='text-align: center; padding: 1rem 0;'>
        <h2 style='color: #6366f1; margin: 0;'>🚀 GKH AI RESUME ANALYZER</h2>
        <p style='color: #94a3b8; font-size: 0.8rem; margin: 0;'>Resume Intelligence Hub</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# Sidebar Navigation
navigation = st.sidebar.radio(
    "Navigation",
    ["📊 Dashboard", "🕒 Analysis History", "⚙️ System Settings"],
    label_visibility="collapsed",
)

# System Stats
st.sidebar.markdown("---")
stats = db.get_stats(st.session_state.session_id)
total_runs = stats.get("total_analyses", 0)
avg_score = stats.get("avg_score", 0.0) or 0.0
best_score = stats.get("best_score", 0.0) or 0.0

st.sidebar.markdown("### 📈 Dashboard Stats")
st.sidebar.markdown(
    f"""
    <div style="background: rgba(30,41,59,0.5); border: 1px solid #334155; border-radius: 8px; padding: 10px; margin-bottom: 15px;">
        <div style="font-size: 0.75rem; color: #94a3b8;">Total Screenings</div>
        <div style="font-size: 1.4rem; font-weight: 700; color: #6366f1;">{total_runs}</div>
        <div style="display: flex; justify-content: space-between; margin-top: 8px; border-top: 1px solid #334155; padding-top: 6px;">
            <div>
                <div style="font-size: 0.68rem; color: #94a3b8;">Avg Score</div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #10b981;">{avg_score:.1f}%</div>
            </div>
            <div>
                <div style="font-size: 0.68rem; color: #94a3b8;">Best Score</div>
                <div style="font-size: 0.85rem; font-weight: 600; color: #f59e0b;">{best_score:.1f}%</div>
            </div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)



# Setup Guide / How it works in sidebar
st.sidebar.markdown("---")
ui.render_sidebar_info()

# --- MAIN PAGE ROUTING ---

if "📊 Dashboard" in navigation:
    ui.render_header()

    # If displaying the Leaderboard (Batch View)
    if st.session_state.show_leaderboard and st.session_state.batch_results:
        st.markdown("## 🏆 Candidate Leaderboard")
        st.markdown("Select a candidate to view their deep-dive evaluation.")
        
        col_btn1, _ = st.columns([2, 8])
        with col_btn1:
            if st.button("⬅️ Back to Upload", use_container_width=True):
                st.session_state.show_leaderboard = False
                st.session_state.batch_results = []
                st.rerun()
                
        # Render cards for each candidate
        sorted_results = sorted(st.session_state.batch_results, key=lambda x: x["analysis"]["score_overall"], reverse=True)
        
        for idx, rec in enumerate(sorted_results):
            col_info, col_load = st.columns([10, 2])
            
            with col_info:
                overall_score = rec["analysis"].get("score_overall", 0.0)
                rec_text = rec["analysis"].get("recommendation", "N/A")
                if overall_score >= 80:
                    badge_color = "#10b981"
                elif overall_score >= 60:
                    badge_color = "#f59e0b"
                else:
                    badge_color = "#ef4444"
                    
                st.markdown(
                    f"""
                    <div class="leaderboard-row">
                        <div style="display:flex; align-items:center;">
                            <span style="font-size: 1.4rem; font-weight: 800; color: #e2e8f0; margin-right: 20px; opacity: 0.8;">#{idx + 1}</span>
                            <div style="display:flex; flex-direction: column;">
                                <span style="font-weight:800; color:#818cf8; font-size:1.2rem; letter-spacing: 0.5px;">{rec['parsed_resume'].get('name', 'Unknown')}</span>
                                <span style="color:#94a3b8; font-size:0.8rem; margin-top:2px;">📄 {rec.get('filename')}</span>
                            </div>
                        </div>
                        <div style="display:flex; align-items:center; gap: 15px;">
                            <span class="badge" style="background:{badge_color}33; color:{badge_color}; border: 1px solid {badge_color}66;">{rec_text}</span>
                            <span style="font-weight:800; color:{badge_color}; font-size:1.3rem;">{overall_score:.1f}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_load:
                st.markdown("<div style='margin-top: 15px;'></div>", unsafe_allow_html=True)
                if st.button("🔍 View Details", key=f"view_{idx}", use_container_width=True):
                    st.session_state.current_analysis = rec["analysis"]
                    st.session_state.resume_filename = rec["filename"]
                    st.session_state.raw_resume_text = rec["raw_text"]
                    st.session_state.parsed_resume = rec["parsed_resume"]
                    st.session_state.show_leaderboard = False
                    st.rerun()


    # If an analysis results is currently loaded (Detailed View)
    elif st.session_state.current_analysis:
        analysis = st.session_state.current_analysis
        resume = st.session_state.parsed_resume
        
        # Candidate Name Header
        cand_name = analysis.get("resume_name") or resume.get("name", "Unknown Candidate")
        st.markdown(f"## 👤 Candidate Evaluation: <span style='color:#6366f1;'>{cand_name}</span>", unsafe_allow_html=True)
        st.markdown(f"**Target Role:** {analysis.get('job_title', 'Position')}")
        st.markdown("<br>", unsafe_allow_html=True)

        # Display Action Buttons in header row
        col_btn1, col_btn2, col_btn3 = st.columns([2, 2, 8])
        with col_btn1:
            if st.session_state.batch_results:
                btn_text = "🏆 Back to Leaderboard"
            else:
                btn_text = "🔄 Analyze New Resume"
                
            if st.button(btn_text, use_container_width=True):
                st.session_state.current_analysis = None
                st.session_state.resume_filename = ""
                st.session_state.raw_resume_text = ""
                st.session_state.parsed_resume = None
                if st.session_state.batch_results:
                    st.session_state.show_leaderboard = True
                st.rerun()

        # PDF Report Download button
        with col_btn2:
            try:
                # Prepare data objects for report generator
                res_data = resume if resume else {
                    "name": analysis.get("resume_name", "Candidate"),
                    "email": "",
                    "phone": "",
                    "skills": analysis.get("matched_skills", []) + analysis.get("extra_skills", []),
                    "education": [],
                    "experience": [],
                    "certifications": [],
                    "total_experience_years": 0.0,
                    "highest_degree": ""
                }
                
                jd_data = {"job_title": analysis.get("job_title", "Position")}
                
                # Run report generator
                pdf_bytes = report_service.generate_analysis_report(
                    res_data, jd_data, analysis
                )
                
                st.download_button(
                    label="📄 Download PDF Report",
                    data=pdf_bytes,
                    file_name=f"ATS_Report_{analysis.get('resume_name','Candidate').replace(' ', '_')}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            except Exception as e:
                st.error(f"Error generating PDF report: {e}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Dashboard Visuals Layout
        col_gauge, col_donut = st.columns([1, 1])

        with col_gauge:
            st.plotly_chart(
                ui.render_score_gauge(analysis.get("score_overall", 0)),
                use_container_width=True,
                config={'displayModeBar': False}
            )

        with col_donut:
            matched = len(analysis.get("matched_skills", []))
            missing = len(analysis.get("missing_skills", []))
            st.plotly_chart(
                ui.render_ats_score_donut(matched, missing),
                use_container_width=True,
                config={'displayModeBar': False}
            )

        st.markdown("<br>", unsafe_allow_html=True)

        # Tabs for deep-dive analysis
        tab1, tab2, tab3 = st.tabs(["📊 Score Breakdown", "💡 AI Feedback", "🔧 Skill Matcher"])

        with tab1:
            st.markdown("### Scoring Mechanics")
            col_s1, col_s2, col_s3, col_s4 = st.columns(4)
            col_s1.metric("Overall Match", f"{analysis.get('score_overall', 0):.1f}%")
            col_s2.metric("Skills Alignment", f"{analysis.get('score_skills', 0):.1f}%")
            col_s3.metric("Experience Match", f"{analysis.get('score_experience', 0):.1f}%")
            col_s4.metric("Education Match", f"{analysis.get('score_education', 0):.1f}%")
            
            st.markdown("#### Category Analysis")
            st.plotly_chart(
                ui.render_score_breakdown_chart(
                    analysis.get('score_skills', 0),
                    analysis.get('score_experience', 0),
                    analysis.get('score_education', 0)
                ),
                use_container_width=True,
                config={'displayModeBar': False}
            )

        with tab2:
            st.markdown("### 🤖 Generative AI Evaluation")
            col_ai1, col_ai2 = st.columns(2)
            with col_ai1:
                st.markdown("#### 🌟 Candidate Strengths")
                for s in analysis.get("ai_strengths", []):
                    st.markdown(f"- ✅ {s}")
            with col_ai2:
                st.markdown("#### 🚩 Identifiable Gaps")
                for g in analysis.get("ai_gaps", []):
                    st.markdown(f"- ⚠️ {g}")

            st.markdown("#### 📝 Improvement Suggestions")
            for sug in analysis.get("ai_suggestions", []):
                st.markdown(f"- 💡 {sug}")

            st.markdown("#### ⚙️ ATS Optimization Tips")
            for tip in analysis.get("ai_ats_tips", []):
                st.markdown(f"- 🎯 {tip}")

        with tab3:
            st.markdown("### Skill Inventory")
            col_k1, col_k2, col_k3 = st.columns(3)
            with col_k1:
                st.markdown("#### ✅ Matched Skills")
                for skill in analysis.get("matched_skills", []):
                    st.markdown(f"- {skill}")
            with col_k2:
                st.markdown("#### ❌ Missing Requirements")
                for skill in analysis.get("missing_skills", []):
                    st.markdown(f"- <span style='color: #ef4444;'>{skill}</span>", unsafe_allow_html=True)
            with col_k3:
                st.markdown("#### ➕ Additional Skills")
                for skill in analysis.get("extra_skills", []):
                    st.markdown(f"- <span style='color: #64748b;'>{skill}</span>", unsafe_allow_html=True)

    # Normal View - Upload Section
    else:
        st.markdown(
            "Upload one or more candidate resumes and a job description to initiate the AI evaluation pipeline."
        )

        col_left, col_right = st.columns([1, 1], gap="large")

        with col_left:
            st.markdown("### 📄 Step 1: Upload PDF Resume(s)")
            uploaded_files = st.file_uploader(
                "Drag and drop or select up to 25 PDF resume files",
                type=["pdf"],
                accept_multiple_files=True
            )

        with col_right:
            st.markdown("### 💼 Step 2: Paste Job Description")
            jd_text = st.text_area(
                "Enter the complete job description here...",
                height=200,
                placeholder="We are looking for a Software Engineer with experience in Python, React...",
            )

        st.markdown("<br>", unsafe_allow_html=True)
        col_btn1, col_btn2, col_btn3 = st.columns([3, 4, 3])
        with col_btn2:
            run_analysis = st.button("⚡ Run Intelligent Batch Analysis", use_container_width=True)

        if run_analysis:
            if not uploaded_files:
                st.warning("Please upload at least one PDF resume.")
            elif not jd_text.strip():
                st.warning("Please provide a Job Description.")
            else:
                progress_container = st.empty()
                
                try:
                    # Parse Job Description Once
                    jd_data = jd_analyzer.analyze(jd_text)
                    
                    batch_results = []
                    total_files = len(uploaded_files)
                    ai_service = AIService(api_key=st.session_state.gemini_api_key)
                    
                    for idx, uploaded_file in enumerate(uploaded_files):
                        filename = uploaded_file.name
                        
                        # Render Dynamic Progress Bar
                        with progress_container.container():
                            st.markdown(f"### ⚙️ Processing {idx + 1} of {total_files}: `{filename}`")
                            progress_bar = st.progress((idx) / total_files)
                            
                        # Extract Text
                        pdf_bytes = uploaded_file.read()
                        resume_text = pdf_extractor.extract(pdf_bytes, filename)
                        
                        # Parse Resume
                        resume_data = resume_parser.parse(resume_text)
                        
                        # Match Skills
                        match_result = skill_matcher.match(resume_data.skills, jd_data["all_skills"])
                        
                        # Calculate Score
                        score_breakdown = scoring_engine.calculate(
                            match_result,
                            resume_data.total_experience_years,
                            jd_data["experience_years"],
                            resume_data.highest_degree,
                            jd_data["education_requirement"],
                        )
                        
                        # AI service analysis
                        try:
                            ai_result = ai_service.analyze(
                                resume_text,
                                jd_text,
                                match_result["matched"],
                                match_result["missing"],
                                score_breakdown.overall_score,
                            )
                        except Exception as ai_e:
                            # Fallback if AI fails (e.g., rate limits on batch)
                            ai_result = {
                                "strengths": ["AI Evaluation Skipped"],
                                "gaps": ["AI Evaluation Skipped"],
                                "improvement_suggestions": [f"AI Error: {ai_e}"],
                                "ats_tips": [],
                                "summary": "Could not generate AI summary for this resume.",
                            }
                            
                        # Assemble analysis object
                        analysis_result = {
                            "resume_name": resume_data.name,
                            "job_title": jd_data.get("job_title", "Position"),
                            "score_overall": score_breakdown.overall_score,
                            "score_skills": score_breakdown.skills_score,
                            "score_experience": score_breakdown.experience_score,
                            "score_education": score_breakdown.education_score,
                            "ats_score": score_breakdown.ats_score,
                            "recommendation": score_breakdown.get_recommendation(),
                            "matched_skills": match_result["matched"],
                            "missing_skills": match_result["missing"],
                            "extra_skills": match_result["extra"],
                            "ai_strengths": ai_result.get("strengths", []),
                            "ai_gaps": ai_result.get("gaps", []),
                            "ai_suggestions": ai_result.get("improvement_suggestions", []),
                            "ai_ats_tips": ai_result.get("ats_tips", []),
                            "ai_summary": ai_result.get("summary", ""),
                        }

                        # Store in Database
                        resume_id = db.save_resume(
                            st.session_state.session_id,
                            filename,
                            resume_text,
                            resume_data.to_dict()
                        )
                        db.save_analysis(
                            resume_id,
                            analysis_result["job_title"],
                            jd_text,
                            analysis_result
                        )
                        db.upsert_skills(resume_data.skills)
                        
                        # Append to batch
                        batch_results.append({
                            "filename": filename,
                            "raw_text": resume_text,
                            "parsed_resume": resume_data.to_dict(),
                            "analysis": analysis_result
                        })
                    
                    # Batch complete
                    with progress_container.container():
                        st.progress(1.0)
                        st.success(f"Batch Analysis Completed for {total_files} resumes!", icon="✅")
                        
                    st.session_state.batch_results = batch_results
                    
                    if total_files > 1:
                        st.session_state.show_leaderboard = True
                    else:
                        st.session_state.show_leaderboard = False
                        st.session_state.current_analysis = batch_results[0]["analysis"]
                        st.session_state.resume_filename = batch_results[0]["filename"]
                        st.session_state.raw_resume_text = batch_results[0]["raw_text"]
                        st.session_state.parsed_resume = batch_results[0]["parsed_resume"]
                        
                    st.rerun()

                except Exception as e:
                    progress_container.empty()
                    st.error(f"Analysis Failed: {str(e)}")
                    st.exception(e)

elif "🕒 Analysis History" in navigation:
    st.markdown("## 🕒 Evaluation History")
    st.markdown("Load or review past candidates and job description matches evaluated in this session.")
    
    history_records = db.get_analysis_history(st.session_state.session_id, limit=30)
    
    if not history_records:
        st.info("No resume matches evaluated yet in this session. Go to the Dashboard to run an analysis.")
    else:
        # Custom display with Load Buttons
        for rec in history_records:
            col_info, col_load = st.columns([10, 2])
            
            with col_info:
                overall_score = rec.get("overall_score", 0.0)
                rec_text = rec.get("recommendation", "N/A")
                if overall_score >= 80:
                    badge_color = "#10b981"
                elif overall_score >= 60:
                    badge_color = "#f59e0b"
                else:
                    badge_color = "#ef4444"
                    
                st.markdown(
                    f"""
                    <div class="leaderboard-row">
                        <div style="display:flex; flex-direction: column;">
                            <span style="font-weight:800; color:#f1f5f9; font-size:1.1rem; letter-spacing: 0.5px;">📄 {rec.get('filename')}</span>
                            <span style="color:#94a3b8; font-size:0.85rem; margin-top:3px;">Target: <span style="color:#a5b4fc;">{rec.get('job_title')}</span> | Analyzed: {rec.get('analyzed_at')}</span>
                        </div>
                        <div style="display:flex; align-items:center; gap: 15px;">
                            <span class="badge" style="background:{badge_color}33; color:{badge_color}; border: 1px solid {badge_color}66;">{rec_text}</span>
                            <span style="font-weight:800; color:{badge_color}; font-size:1.25rem;">{overall_score:.1f}%</span>
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
            with col_load:
                if st.button("🔍 View Details", key=f"load_{rec.get('id')}", use_container_width=True):
                    # Fetch full details
                    details = db.get_analysis_by_id(rec.get("id"))
                    resume_record = db.get_resume_by_id(details.get("resume_id"))
                    
                    # Update session state and route
                    st.session_state.resume_filename = resume_record.get("filename")
                    st.session_state.raw_resume_text = resume_record.get("raw_text")
                    st.session_state.parsed_resume = resume_record
                    st.session_state.current_analysis = details
                    st.session_state.show_leaderboard = False
                    
                    st.toast("Loaded details successfully!", icon="✅")
                    st.rerun()

elif "⚙️ System Settings" in navigation:
    st.markdown("## ⚙️ Configuration Settings")
    
    st.markdown("### 🧹 Database Management", unsafe_allow_html=True)
    st.warning("Clearing session data will permanently wipe the upload logs, resumes, and matched evaluation histories.")
    if st.button("🗑️ Wipe Session Data"):
        # Reset database by deleting rows
        try:
            with db._get_connection() as conn:
                conn.execute("DELETE FROM analysis_results")
                conn.execute("DELETE FROM resumes")
                conn.execute("DELETE FROM users")
                conn.commit()
            st.session_state.current_analysis = None
            st.session_state.resume_filename = ""
            st.session_state.raw_resume_text = ""
            st.session_state.parsed_resume = None
            st.session_state.batch_results = []
            st.session_state.show_leaderboard = False
            st.success("All session logs successfully cleared.")
            st.rerun()
        except Exception as e:
            st.error(f"Error resetting database: {e}")

# Footer
st.markdown("<br><hr>", unsafe_allow_html=True)
st.markdown(
    """
    <div style="text-align: center; color: #64748b; font-size: 0.8rem; padding-bottom: 20px;">
        ✨ GKH AI RESUME ANALYZER Platform | Built with Python, Streamlit, and Google Gemini API.
    </div>
    """,
    unsafe_allow_html=True,
)
