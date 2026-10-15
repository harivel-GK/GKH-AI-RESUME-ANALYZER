# frontend/components.py
"""
Reusable Streamlit UI components for the AI Resume Analyzer.
Encapsulates common visual patterns with HTML/CSS injection.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
from typing import List, Dict, Optional


def render_header():
    """Render the main application header banner."""
    st.markdown("""
    <div class="main-header">
        <h1>🎯 AI Resume Analyzer</h1>
        <p>Intelligent Resume Screening & Job Match Evaluation Platform</p>
    </div>
    """, unsafe_allow_html=True)


def render_score_gauge(score: float, title: str = "Match Score") -> go.Figure:
    """
    Render an animated Plotly gauge chart for the match score.
    Score: 0-100
    """
    if score >= 80:
        color = "#10b981"
        bar_color = "rgba(16,185,129,0.3)"
    elif score >= 60:
        color = "#f59e0b"
        bar_color = "rgba(245,158,11,0.3)"
    else:
        color = "#ef4444"
        bar_color = "rgba(239,68,68,0.3)"

    fig = go.Figure(go.Indicator(
        mode="gauge+number+delta",
        value=score,
        title={
            "text": title,
            "font": {"size": 18, "color": "#f1f5f9", "family": "Inter"}
        },
        number={
            "suffix": "%",
            "font": {"size": 40, "color": color, "family": "Inter"},
        },
        gauge={
            "axis": {
                "range": [0, 100],
                "tickwidth": 1,
                "tickcolor": "#475569",
                "tickfont": {"color": "#94a3b8", "size": 10},
            },
            "bar": {"color": color, "thickness": 0.25},
            "bgcolor": "#1e293b",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 60], "color": "rgba(239,68,68,0.08)"},
                {"range": [60, 80], "color": "rgba(245,158,11,0.08)"},
                {"range": [80, 100], "color": "rgba(16,185,129,0.08)"},
            ],
            "threshold": {
                "line": {"color": color, "width": 3},
                "thickness": 0.8,
                "value": score,
            },
        },
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=20, r=20, t=40, b=10),
        font={"family": "Inter"},
    )
    return fig


def render_skills_bar_chart(matched: List[str], missing: List[str]) -> go.Figure:
    """Render a horizontal bar chart comparing matched vs missing skills."""
    categories = ["Matched Skills", "Missing Skills"]
    values = [len(matched), len(missing)]
    colors = ["#10b981", "#ef4444"]

    fig = go.Figure(go.Bar(
        x=values,
        y=categories,
        orientation="h",
        marker=dict(
            color=colors,
            line=dict(width=0),
        ),
        text=values,
        textposition="inside",
        textfont=dict(color="white", size=14, family="Inter"),
        hovertemplate="%{y}: %{x} skills<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=180,
        margin=dict(l=10, r=20, t=20, b=10),
        xaxis=dict(
            showgrid=True,
            gridcolor="rgba(51,65,85,0.5)",
            tickfont=dict(color="#94a3b8"),
            zeroline=False,
        ),
        yaxis=dict(
            tickfont=dict(color="#f1f5f9", size=13, family="Inter"),
            gridcolor="rgba(0,0,0,0)",
        ),
        font=dict(family="Inter"),
    )
    return fig


def render_score_breakdown_chart(
    skills_score: float,
    experience_score: float,
    education_score: float,
) -> go.Figure:
    """Render a radar/spider chart for score breakdown."""
    categories = ["Skills", "Experience", "Education"]
    values = [skills_score, experience_score, education_score]

    fig = go.Figure()

    fig.add_trace(go.Bar(
        x=categories,
        y=values,
        marker=dict(
            color=["#6366f1", "#06b6d4", "#10b981"],
            line=dict(width=0),
        ),
        text=[f"{v:.1f}%" for v in values],
        textposition="outside",
        textfont=dict(color="#f1f5f9", size=13, family="Inter"),
        hovertemplate="%{x}: %{y:.1f}%<extra></extra>",
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=280,
        margin=dict(l=10, r=10, t=20, b=10),
        xaxis=dict(
            tickfont=dict(color="#f1f5f9", size=13, family="Inter"),
            gridcolor="rgba(0,0,0,0)",
        ),
        yaxis=dict(
            range=[0, 110],
            showgrid=True,
            gridcolor="rgba(51,65,85,0.5)",
            tickfont=dict(color="#94a3b8"),
            ticksuffix="%",
        ),
        font=dict(family="Inter"),
    )
    return fig


def render_skill_tags(skills: List[str], tag_type: str = "matched") -> str:
    """Render HTML skill tags."""
    css_class = {
        "matched": "skill-matched",
        "missing": "skill-missing",
        "extra": "skill-extra",
    }.get(tag_type, "skill-extra")

    if not skills:
        return "<p style='color: #64748b; font-style: italic;'>None detected</p>"

    tags = "".join(
        f'<span class="skill-tag {css_class}">{skill}</span>'
        for skill in skills
    )
    return f'<div style="line-height: 2.2;">{tags}</div>'


def render_recommendation_banner(recommendation: str, score: float) -> str:
    """Render a recommendation status banner."""
    icon_map = {
        "Strong Match": ("🟢", "rec-strong"),
        "Moderate Match": ("🟡", "rec-moderate"),
        "Weak Match": ("🔴", "rec-weak"),
    }
    icon, css_class = icon_map.get(recommendation, ("⚪", "rec-moderate"))
    return f"""
    <div class="recommendation-banner {css_class}">
        {icon} &nbsp; {recommendation} &nbsp; | &nbsp; ATS Score: {score:.1f}/100
    </div>
    """


def render_feedback_list(items: List[str], feedback_type: str = "suggestion") -> str:
    """Render AI feedback items as styled list."""
    css_class = {
        "strength": "feedback-strength",
        "gap": "feedback-gap",
        "suggestion": "feedback-suggestion",
        "ats": "feedback-ats",
    }.get(feedback_type, "feedback-suggestion")

    icon_map = {
        "strength": "✅",
        "gap": "⚠️",
        "suggestion": "💡",
        "ats": "🤖",
    }
    icon = icon_map.get(feedback_type, "•")

    if not items:
        return "<p style='color: #64748b; font-style: italic;'>No items available.</p>"

    html = ""
    for item in items:
        html += f'<div class="feedback-item {css_class}">{icon} {item}</div>'
    return html


def render_analysis_history_table(history: List[Dict]) -> None:
    """Render analysis history as a styled dataframe."""
    if not history:
        st.info("No analysis history yet. Upload a resume and analyze to get started!")
        return

    df = pd.DataFrame(history)

    # Format columns
    display_cols = {
        "filename": "Resume",
        "job_title": "Position",
        "overall_score": "Score",
        "ats_score": "ATS",
        "recommendation": "Recommendation",
        "analyzed_at": "Date",
    }

    available = [c for c in display_cols.keys() if c in df.columns]
    df = df[available].rename(columns=display_cols)

    if "Score" in df.columns:
        df["Score"] = df["Score"].apply(lambda x: f"{x:.1f}%" if x else "N/A")
    if "ATS" in df.columns:
        df["ATS"] = df["ATS"].apply(lambda x: f"{x:.1f}" if x else "N/A")
    if "Date" in df.columns:
        df["Date"] = pd.to_datetime(df["Date"]).dt.strftime("%b %d, %Y")

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
    )


def render_metric_card(label: str, value: str, delta: str = None, color: str = "#6366f1") -> str:
    """Render a metric display card."""
    delta_html = ""
    if delta:
        delta_html = f'<div style="color: #94a3b8; font-size: 0.78rem; margin-top: 2px;">{delta}</div>'

    return f"""
    <div class="metric-card" style="text-align: center; border-top: 3px solid {color};">
        <div class="stat-value" style="background: linear-gradient(135deg, {color}, #06b6d4);
             -webkit-background-clip: text; -webkit-text-fill-color: transparent; background-clip: text;">
            {value}
        </div>
        <div class="stat-label">{label}</div>
        {delta_html}
    </div>
    """


def render_progress_steps(steps: List[Dict]) -> None:
    """Render animated progress steps."""
    for step in steps:
        icon = step.get("icon", "⏳")
        label = step.get("label", "")
        done = step.get("done", False)
        color = "#10b981" if done else "#6366f1"
        icon = "✅" if done else icon
        st.markdown(
            f'<div class="step-container">'
            f'<span class="step-icon">{icon}</span>'
            f'<span style="color: {"#f1f5f9" if done else "#94a3b8"};">{label}</span>'
            f'</div>',
            unsafe_allow_html=True,
        )


def render_sidebar_info():
    """Render sidebar info section."""
    st.sidebar.markdown("""
    <div style="background: rgba(99,102,241,0.1); border: 1px solid rgba(99,102,241,0.3);
         border-radius: 10px; padding: 1rem; margin-bottom: 1rem;">
        <div style="color: #818cf8; font-weight: 700; font-size: 0.85rem; margin-bottom: 0.5rem;">
            ℹ️ HOW IT WORKS
        </div>
        <ol style="color: #94a3b8; font-size: 0.82rem; padding-left: 1.2rem; margin: 0; line-height: 1.8;">
            <li>Upload your PDF resume</li>
            <li>Paste the job description</li>
            <li>Click <strong style="color: #f1f5f9;">Analyze</strong></li>
            <li>Review your ATS score & feedback</li>
            <li>Download the PDF report</li>
        </ol>
    </div>
    """, unsafe_allow_html=True)


def render_ats_score_donut(matched: int, missing: int) -> go.Figure:
    """Render a donut chart for skill coverage."""
    labels = ["Matched", "Missing"]
    values = [matched, missing]
    colors = ["#10b981", "#ef4444"]

    if matched == 0 and missing == 0:
        values = [1, 0]
        colors = ["#334155", "#334155"]

    fig = go.Figure(go.Pie(
        labels=labels,
        values=values,
        hole=0.65,
        marker=dict(
            colors=colors,
            line=dict(color="#0f172a", width=2)
        ),
        textinfo="label+percent",
        textfont=dict(color="#f1f5f9", size=12, family="Inter"),
        hovertemplate="%{label}: %{value} skills (%{percent})<extra></extra>",
        showlegend=False,
    ))

    total = matched + missing
    pct = int((matched / total * 100) if total > 0 else 0)

    fig.add_annotation(
        text=f"<b>{pct}%</b>",
        x=0.5, y=0.55,
        font_size=28,
        font_color="#10b981" if pct >= 60 else "#ef4444",
        font_family="Inter",
        showarrow=False,
    )
    fig.add_annotation(
        text="Coverage",
        x=0.5, y=0.38,
        font_size=11,
        font_color="#94a3b8",
        font_family="Inter",
        showarrow=False,
    )

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        height=240,
        margin=dict(l=10, r=10, t=10, b=10),
        font=dict(family="Inter"),
    )
    return fig
