# GKH AI Resume Analyzer

An intelligent, state-of-the-art SaaS application built with Python, Streamlit, and Google Gemini AI.
This application allows recruiters and hiring managers to batch-process PDF resumes, extract key information, and compare them against a specific Job Description.

## Features
- **Batch Processing**: Upload up to 25 PDFs at once.
- **Smart Scoring**: Automatically calculates a 0-100% Match Score based on Skills, Experience, and Education.
- **Generative AI Feedback**: Uses Google's Gemini LLM to analyze gaps, extract strengths, and suggest improvements.
- **Interactive UI**: Features a modern, frosted glassmorphism dashboard with responsive leaderboards.
- **PDF Export**: Download clean, robust text-based PDF reports for any candidate.

## Installation
1. Clone this repository.
2. Install dependencies: `pip install -r requirements.txt` *(Note: you may need to freeze your pip list)*
3. Create a `.env` file in the root directory and add your Gemini API Key:
   `GEMINI_API_KEY="your_api_key_here"`
4. Run the app: `streamlit run app.py`
