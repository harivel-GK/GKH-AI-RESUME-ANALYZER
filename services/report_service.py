import logging
from typing import Dict
from datetime import datetime

logger = logging.getLogger(__name__)

class ReportService:
    def generate_analysis_report(self, resume_data: Dict, jd_data: Dict, analysis_result: Dict) -> bytes:
        from fpdf import FPDF
        
        class SimplePDF(FPDF):
            def header(self):
                self.set_font('Arial', 'B', 16)
                self.cell(0, 10, 'AI Resume Analysis Report', 0, 1, 'C')
                self.ln(2)
                
            def footer(self):
                self.set_y(-15)
                self.set_font('Arial', 'I', 8)
                self.cell(0, 10, f'Page {self.page_no()}', 0, 0, 'C')

        pdf = SimplePDF()
        pdf.set_auto_page_break(auto=True, margin=15)
        pdf.add_page()
        
        def safe(text):
            if not isinstance(text, str): return str(text)
            # Encode and decode to strip emojis/unsupported characters
            return text.encode('latin-1', 'ignore').decode('latin-1')
            
        def add_line(text, bold=False, size=11):
            if bold:
                pdf.set_font("Arial", "B", size)
            else:
                pdf.set_font("Arial", "", size)
            pdf.multi_cell(0, 6, safe(text))
            
        add_line(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
        add_line(f"Candidate Name: {resume_data.get('name', 'Unknown')}")
        add_line(f"Target Role: {jd_data.get('job_title', 'Unknown')}")
        pdf.ln(5)
        
        add_line("1. SCORE BREAKDOWN", bold=True, size=13)
        add_line(f"   Overall Match Score: {analysis_result.get('score_overall', 0):.1f}%")
        add_line(f"   Skills Match: {analysis_result.get('score_skills', 0):.1f}%")
        add_line(f"   Experience Match: {analysis_result.get('score_experience', 0):.1f}%")
        add_line(f"   Education Match: {analysis_result.get('score_education', 0):.1f}%")
        add_line(f"   ATS Readiness Score: {analysis_result.get('ats_score', 0):.1f}%")
        add_line(f"   Verdict: {analysis_result.get('recommendation', 'N/A')}")
        pdf.ln(5)
        
        add_line("2. SKILLS ANALYSIS", bold=True, size=13)
        matched = analysis_result.get('matched_skills', [])
        missing = analysis_result.get('missing_skills', [])
        add_line(f"   Matched Skills ({len(matched)}): {', '.join(matched)}")
        pdf.ln(2)
        add_line(f"   Missing Skills ({len(missing)}): {', '.join(missing)}")
        pdf.ln(5)
        
        add_line("3. AI FEEDBACK & SUMMARY", bold=True, size=13)
        summary = analysis_result.get("ai_summary", "")
        if summary:
            add_line(summary)
            pdf.ln(3)
        
        if analysis_result.get("ai_strengths"):
            add_line("Strengths:", bold=True)
            for s in analysis_result.get("ai_strengths", []):
                add_line(f"  * {s}")
            pdf.ln(2)
            
        if analysis_result.get("ai_gaps"):
            add_line("Gaps & Missing Qualifications:", bold=True)
            for g in analysis_result.get("ai_gaps", []):
                add_line(f"  * {g}")
            pdf.ln(2)
            
        if analysis_result.get("ai_suggestions"):
            add_line("Improvement Suggestions:", bold=True)
            for s in analysis_result.get("ai_suggestions", []):
                add_line(f"  * {s}")
            pdf.ln(2)
            
        if analysis_result.get("ai_ats_tips"):
            add_line("ATS Optimization Tips:", bold=True)
            for a in analysis_result.get("ai_ats_tips", []):
                add_line(f"  * {a}")

        return bytes(pdf.output())
