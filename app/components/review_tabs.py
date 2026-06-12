"""Review tabs component showing categorized review findings."""

import json
import streamlit as st
from dataclasses import asdict

from app.models.review import ReviewResult
from app.utils.formatter import format_impact_badge


def render_review_tabs(review: ReviewResult):
    """Render six tabs: Bugs, Edge Cases, Optimizations, Security, Positives, Raw JSON."""

    tabs = st.tabs([
        f"Bugs ({len(review.bugs)})",
        f"Edge Cases ({len(review.edge_cases)})",
        f"Optimizations ({len(review.optimizations)})",
        f"Security ({len(review.security)})",
        f"Positives ({len(review.positives)})",
        "Raw JSON",
    ])

    # --- Bugs Tab ---
    with tabs[0]:
        if not review.bugs:
            st.success("No bugs found.")
        else:
            for i, bug in enumerate(review.bugs):
                with st.container():
                    st.markdown(
                        f"""
                        <div style="
                            background:#1e2028;
                            border-left:4px solid #E74C3C;
                            border-radius:8px;
                            padding:1rem 1.25rem;
                            margin-bottom:0.75rem;
                        ">
                            <div style="margin-bottom:0.5rem;">
                                <code style="
                                    background:#2a2d35;
                                    color:#3B82F6;
                                    padding:2px 8px;
                                    border-radius:4px;
                                    font-size:0.85rem;
                                ">{bug.file}</code>
                                <span style="color:#888;font-size:0.85rem;margin-left:8px;">
                                    Line {bug.line}
                                </span>
                            </div>
                            <p style="color:#FAFAFA;margin:0.25rem 0;font-size:0.95rem;">
                                {bug.issue}
                            </p>
                            <p style="color:#2ECC71;font-size:0.85rem;margin:0.25rem 0;">
                                <strong>Fix:</strong> {bug.fix}
                            </p>
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

    # --- Edge Cases Tab ---
    with tabs[1]:
        if not review.edge_cases:
            st.success("No edge cases identified.")
        else:
            for ec in review.edge_cases:
                st.markdown(
                    f"""
                    <div style="
                        background:#1e2028;
                        border-left:4px solid #F39C12;
                        border-radius:8px;
                        padding:1rem 1.25rem;
                        margin-bottom:0.75rem;
                    ">
                        <p style="color:#FAFAFA;margin:0 0 0.25rem 0;font-size:0.95rem;">
                            {ec.description}
                        </p>
                        <p style="color:#3B82F6;font-size:0.85rem;margin:0;">
                            Suggestion: {ec.suggestion}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- Optimizations Tab ---
    with tabs[2]:
        if not review.optimizations:
            st.success("No optimizations suggested.")
        else:
            for opt in review.optimizations:
                impact_color = {
                    "high": "#E74C3C",
                    "medium": "#F39C12",
                    "low": "#2ECC71",
                }.get(opt.impact.lower(), "#95A5A6")

                st.markdown(
                    f"""
                    <div style="
                        background:#1e2028;
                        border-left:4px solid {impact_color};
                        border-radius:8px;
                        padding:1rem 1.25rem;
                        margin-bottom:0.75rem;
                    ">
                        <div style="margin-bottom:0.4rem;">
                            {format_impact_badge(opt.impact)}
                        </div>
                        <p style="color:#FAFAFA;margin:0;font-size:0.95rem;">
                            {opt.description}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- Security Tab ---
    with tabs[3]:
        if not review.security:
            st.success("No security issues found.")
        else:
            for sec in review.security:
                st.markdown(
                    f"""
                    <div style="
                        background:#1e2028;
                        border-left:4px solid #9B59B6;
                        border-radius:8px;
                        padding:1rem 1.25rem;
                        margin-bottom:0.75rem;
                    ">
                        <p style="color:#FAFAFA;margin:0 0 0.25rem 0;font-size:0.95rem;">
                            {sec.issue}
                        </p>
                        <p style="color:#F39C12;font-size:0.85rem;margin:0;">
                            Recommendation: {sec.recommendation}
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

    # --- Positives Tab ---
    with tabs[4]:
        if not review.positives:
            st.info("No specific positives highlighted.")
        else:
            for pos in review.positives:
                st.markdown(
                    f"""
                    <div style="
                        background:#1e2028;
                        border-left:4px solid #2ECC71;
                        border-radius:8px;
                        padding:0.75rem 1.25rem;
                        margin-bottom:0.5rem;
                    ">
                        <p style="color:#FAFAFA;margin:0;font-size:0.95rem;">{pos}</p>
                    </div>
                    """,
                    unsafe_allow_html=True,
                )


    # --- Raw JSON Tab ---
    with tabs[5]:
        st.json(asdict(review))
