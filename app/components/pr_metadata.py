"""PR Metadata card component."""

import streamlit as st
from app.models.pr import PRMetadata


def render_pr_metadata(pr_meta: PRMetadata):
    """Render a styled card showing PR title, author, date, and branches."""
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1a1d23 0%, #2d2f36 100%);
            border: 1px solid rgba(108, 99, 255, 0.3);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 20px rgba(108, 99, 255, 0.1);
        ">
            <h3 style="
                margin: 0 0 0.75rem 0;
                color: #FAFAFA;
                font-size: 1.3rem;
                font-weight: 700;
            ">{pr_meta.title}</h3>
            <div style="display:flex;flex-wrap:wrap;gap:1.5rem;align-items:center;">
                <div style="color:#b0b0b0;font-size:0.9rem;">
                    <span style="color:#6C63FF;font-weight:600;">Author:</span> {pr_meta.author}
                </div>
                <div style="color:#b0b0b0;font-size:0.9rem;">
                    <span style="color:#6C63FF;font-weight:600;">Date:</span> {pr_meta.created_at[:10]}
                </div>
                <div style="color:#b0b0b0;font-size:0.9rem;">
                    <code style="background:#2a2d35;padding:2px 8px;border-radius:6px;color:#3B82F6;">
                        {pr_meta.head_branch}
                    </code>
                    <span style="color:#6C63FF;margin:0 6px;">→</span>
                    <code style="background:#2a2d35;padding:2px 8px;border-radius:6px;color:#2ECC71;">
                        {pr_meta.base_branch}
                    </code>
                </div>
            </div>
            {"<p style='color:#888;font-size:0.85rem;margin-top:0.75rem;'>" + pr_meta.description[:300] + "</p>" if pr_meta.description else ""}
        </div>
        """,
        unsafe_allow_html=True,
    )
