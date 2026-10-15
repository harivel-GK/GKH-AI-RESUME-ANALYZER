# GKH AI Resume Analyzer

An AI-assisted resume analysis application built with Python. The repository includes resume parsing and scoring modules, supporting services, UI components, and related analytics projects.

## Main application

The main Streamlit entry point is `app.py`.

## Setup

1. Create and activate a Python virtual environment.
2. Install the dependencies listed in `requirements.txt` (review and update this file if your local environment uses additional packages).
3. Configure any required API keys as environment variables; never commit real secrets.
4. Run the application with `streamlit run app.py` if the app uses Streamlit.

## Included folders

- `backend/` — resume parsing, job-description analysis, matching and scoring logic
- `services/` — AI and report services
- `frontend/` — UI components and styles
- `database/` — database helpers and schema (runtime database files are excluded)
- `Customer-Segmentation/` — customer segmentation example
- `Sales-Analytics-Dashboard/` — sales analytics dashboard project

## Security and repository hygiene

Environment files containing secrets, Python cache files, and local database files are excluded from this commit. Review any sample data and logs before publishing further changes.
