"""Metrics bar component showing key PR and review statistics."""

import streamlit as st
from app.models.pr import PRMetadata
from app.models.review import ReviewResult
from app.utils.formatter import format_severity_badge


def render_metrics_bar(pr_meta: PRMetadata, review: ReviewResult):
    """Render five metric columns: files, additions, deletions, bugs, severity."""
    cols = st.columns(5)

    with cols[0]:
        st.metric(
            label="Files Changed",
            value=pr_meta.files_changed,
        )

    with cols[1]:
        st.metric(
            label="Additions",
            value=f"+{pr_meta.total_additions}",
        )

    with cols[2]:
        st.metric(
            label="Deletions",
            value=f"-{pr_meta.total_deletions}",
        )

    with cols[3]:
        st.metric(
            label="Bugs Found",
            value=len(review.bugs),
        )

    with cols[4]:
        st.markdown("**Severity**")
        st.markdown(format_severity_badge(review.severity), unsafe_allow_html=True)

