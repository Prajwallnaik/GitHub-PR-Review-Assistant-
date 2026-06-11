"""Sidebar component — API keys, review mode, and history."""

import streamlit as st
from config.providers import DEFAULT_MODEL


def render_sidebar() -> dict:
    """
    Render the sidebar with configuration inputs and return a config dict.

    Returns:
        dict with keys: github_token, openrouter_api_key, focus_mode, model
    """
    with st.sidebar:
        st.markdown(
            """
            <div style="text-align:center;margin-bottom:1.5rem;">
                <h2 style="
                    background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 100%);
                    -webkit-background-clip: text;
                    -webkit-text-fill-color: transparent;
                    font-size: 1.4rem;
                    font-weight: 800;
                    letter-spacing: -0.5px;
                ">Configuration</h2>
            </div>
            """,
            unsafe_allow_html=True,
        )

        st.markdown("##### API Keys")

        github_token = st.text_input(
            "GitHub Token",
            type="password",
            placeholder="ghp_...",
            help="Personal access token with repo scope",
        )

        openrouter_api_key = st.text_input(
            "OpenRouter API Key",
            type="password",
            placeholder="sk-or-...",
            help="Get yours at openrouter.ai",
        )

        st.markdown("---")
        st.markdown("##### Review Focus")

        focus_mode = st.selectbox(
            "Review Mode",
            options=[
                "Full Review",
                "Security Audit",
                "Performance",
                "Readability",
                "Test Coverage",
            ],
            index=0,
        )

        st.markdown("---")
        st.markdown("##### Advanced Settings")

        per_file_analysis = st.selectbox(
            "Per-file Analysis",
            options=["Auto", "Enabled", "Disabled"],
            index=0,
            help="Review each file individually to avoid token limits and get more precise feedback.",
        )

        block_merge = st.checkbox(
            "Block merge on high severity",
            value=False,
            help="Require all findings to be medium/low severity to pass the review check.",
        )

        st.markdown("---")
        st.markdown("##### Model")
        st.code(DEFAULT_MODEL, language=None)

        st.markdown("---")
        st.markdown("##### Quick Links")
        st.markdown(
            """
            <div style="font-size:0.85rem;">
                <a href="https://github.com/settings/tokens" target="_blank" 
                   style="color:#6C63FF;text-decoration:none;">
                   Get GitHub Token
                </a><br/>
                <a href="https://openrouter.ai/keys" target="_blank" 
                   style="color:#6C63FF;text-decoration:none;">
                   Get OpenRouter Key
                </a>
            </div>
            """,
            unsafe_allow_html=True,
        )

    return {
        "github_token": github_token,
        "openrouter_api_key": openrouter_api_key,
        "focus_mode": focus_mode,
        "per_file_analysis": per_file_analysis,
        "block_merge": block_merge,
        "model": DEFAULT_MODEL,
    }


