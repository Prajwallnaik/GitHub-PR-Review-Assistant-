"""Diff viewer component showing file-by-file patch display."""

import streamlit as st
from typing import List
import html

from app.models.pr import PRFile
from config.settings import MAX_FILES_IN_DIFF_VIEWER


def render_diff_viewer(files: List[PRFile]):
    """Render an expandable section per file with color-coded diff lines."""
    st.markdown("### Diff Viewer")

    if not files:
        st.info("No files to display.")
        return

    display_files = files[:MAX_FILES_IN_DIFF_VIEWER]
    remaining = len(files) - MAX_FILES_IN_DIFF_VIEWER

    for pr_file in display_files:
        status_label = pr_file.status.upper() if pr_file.status else "MODIFIED"
        label = (
            f"[{status_label}] {pr_file.filename} "
            f"(+{pr_file.additions}/-{pr_file.deletions})"
        )

        with st.expander(label, expanded=False):
            if not pr_file.patch:
                st.caption("No patch content available for this file.")
                continue

            lines = pr_file.patch.split("\n")
            html_lines = []

            for line in lines:
                escaped = html.escape(line)
                if line.startswith("+") and not line.startswith("+++"):
                    html_lines.append(
                        f'<div style="background:rgba(46,204,113,0.12);color:#2ECC71;'
                        f'padding:1px 8px;font-family:monospace;font-size:0.82rem;'
                        f'white-space:pre-wrap;word-break:break-all;">{escaped}</div>'
                    )
                elif line.startswith("-") and not line.startswith("---"):
                    html_lines.append(
                        f'<div style="background:rgba(231,76,60,0.12);color:#E74C3C;'
                        f'padding:1px 8px;font-family:monospace;font-size:0.82rem;'
                        f'white-space:pre-wrap;word-break:break-all;">{escaped}</div>'
                    )
                elif line.startswith("@@"):
                    html_lines.append(
                        f'<div style="background:rgba(108,99,255,0.12);color:#6C63FF;'
                        f'padding:1px 8px;font-family:monospace;font-size:0.82rem;'
                        f'white-space:pre-wrap;font-weight:600;">{escaped}</div>'
                    )
                else:
                    html_lines.append(
                        f'<div style="color:#888;padding:1px 8px;font-family:monospace;'
                        f'font-size:0.82rem;white-space:pre-wrap;">{escaped}</div>'
                    )

            st.markdown(
                f"""<div style="
                    background:#0d0f14;
                    border:1px solid #2a2d35;
                    border-radius:8px;
                    padding:0.5rem 0;
                    max-height:500px;
                    overflow-y:auto;
                ">{''.join(html_lines)}</div>""",
                unsafe_allow_html=True,
            )

    if remaining > 0:
        st.caption(f"...and {remaining} more file(s) not shown.")
