"""Sidebar component — API keys, review mode, and history."""

import streamlit as st
from config.providers import PROVIDERS


def render_sidebar() -> dict:
    """
    Render the sidebar with configuration inputs and return a config dict.

    Returns:
        dict with keys: ai_provider, focus_mode, per_file_analysis, block_merge, model
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

        st.markdown("##### AI Settings")

        provider_options = list(PROVIDERS.keys())
        provider_display_names = {k: v["display_name"] for k, v in PROVIDERS.items()}
        selected_provider = st.selectbox(
            "AI Provider",
            options=provider_options,
            format_func=lambda x: provider_display_names[x],
            index=0,
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
        st.markdown("##### Model")

        models = PROVIDERS[selected_provider]["models"]
        model_options = [m["id"] for m in models]
        model_display_names = {m["id"]: m["display_name"] for m in models}

        selected_model = st.selectbox(
            "Model",
            options=model_options,
            format_func=lambda x: model_display_names[x],
            index=0,
        )

    return {
        "ai_provider": selected_provider,
        "focus_mode": focus_mode,
        "per_file_analysis": "Auto",
        "block_merge": False,
        "model": selected_model,
    }



