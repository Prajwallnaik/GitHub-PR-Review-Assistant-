"""AI Code Review Assistant — Main Entry Point."""

import json
import os
import sys
from dataclasses import asdict

import streamlit as st
from dotenv import load_dotenv

# Ensure the project root is on the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.components.sidebar import render_sidebar
from app.components.pr_metadata import render_pr_metadata
from app.components.metrics_bar import render_metrics_bar
from app.components.review_tabs import render_review_tabs
from app.components.diff_viewer import render_diff_viewer
from app.services.github_service import (
    fetch_pr_data,
    post_review_comment,
    post_inline_review_comments,
    post_unified_review,
)
from app.services.ai.factory import get_ai_service
from app.storage.history import init_db, save_review, get_history, get_review_by_id
from app.utils.parser import parse_pr_url
from app.utils.exporter import export_as_json, export_as_markdown
from app.utils.formatter import format_severity_badge
from app.models.review import ReviewResult, Bug, EdgeCase, Optimization, SecurityIssue
from app.models.pr import PRMetadata, PRFile
from config.settings import APP_TITLE

# Prompt modules
from app.prompts import base_review, security_focus, performance_focus, readability_focus, test_coverage

# ---------------------------------------------------------------------------
# Page Config
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="AI Code Review Assistant",
    page_icon="search",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---------------------------------------------------------------------------
# Global CSS
# ---------------------------------------------------------------------------
st.markdown(
    """
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

        * { font-family: 'Inter', sans-serif; }

        .stApp {
            background: linear-gradient(180deg, #0E1117 0%, #151820 100%);
        }

        /* Header */
        .main-header {
            text-align: center;
            padding: 2rem 0 1rem;
        }
        .main-header h1 {
            background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 50%, #06B6D4 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-size: 2.5rem;
            font-weight: 800;
            letter-spacing: -1px;
            margin-bottom: 0.25rem;
        }
        .main-header p {
            color: #888;
            font-size: 1rem;
            margin-top: 0;
        }

        /* Input area */
        .url-container {
            background: linear-gradient(135deg, #1a1d23 0%, #22252b 100%);
            border: 1px solid rgba(108, 99, 255, 0.25);
            border-radius: 16px;
            padding: 1.5rem 2rem;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 24px rgba(0,0,0,0.2);
        }

        /* Metric cards */
        [data-testid="stMetric"] {
            background: linear-gradient(135deg, #1a1d23 0%, #22252b 100%);
            border: 1px solid rgba(108, 99, 255, 0.2);
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 2px 12px rgba(0,0,0,0.15);
        }

        /* Tabs */
        .stTabs [data-baseweb="tab-list"] {
            border-bottom: 2px solid rgba(255, 255, 255, 0.05);
            gap: 8px;
        }
        .stTabs [data-baseweb="tab"] {
            background-color: transparent !important;
            border: none !important;
            color: #888 !important;
            font-weight: 500;
            padding: 8px 16px;
        }
        .stTabs [data-baseweb="tab"][aria-selected="true"] {
            color: #6C63FF !important;
            border-bottom: 2px solid #6C63FF !important;
        }

        /* Buttons */
        .stButton > button {
            background: linear-gradient(135deg, #6C63FF 0%, #3B82F6 100%);
            color: white;
            border: none;
            border-radius: 10px;
            padding: 0.6rem 2rem;
            font-weight: 600;
            font-size: 1rem;
            transition: all 0.3s ease;
            box-shadow: 0 4px 15px rgba(108, 99, 255, 0.3);
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(108, 99, 255, 0.45);
        }

        /* Sidebar history cards */
        .history-card {
            background: #1a1d23;
            border: 1px solid #2a2d35;
            border-radius: 10px;
            padding: 0.75rem 1rem;
            margin-bottom: 0.5rem;
            cursor: pointer;
            transition: all 0.2s ease;
        }
        .history-card:hover {
            border-color: #6C63FF;
            box-shadow: 0 2px 12px rgba(108, 99, 255, 0.15);
        }

        /* Hide Streamlit branding */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
    </style>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# Init
# ---------------------------------------------------------------------------
load_dotenv()
init_db()

# ---------------------------------------------------------------------------
# Prompt mapping
# ---------------------------------------------------------------------------
FOCUS_PROMPT_MAP = {
    "Full Review": base_review.get_prompt,
    "Security Audit": security_focus.get_prompt,
    "Performance": performance_focus.get_prompt,
    "Readability": readability_focus.get_prompt,
    "Test Coverage": test_coverage.get_prompt,
}

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
config = render_sidebar()

# Use env vars as fallback
github_token = config["github_token"] or os.getenv("GITHUB_TOKEN", "")
openrouter_key = config["openrouter_api_key"] or os.getenv("OPENROUTER_API_KEY", "")

# ---------------------------------------------------------------------------
# History sidebar section
# ---------------------------------------------------------------------------
with st.sidebar:
    st.markdown("---")
    st.markdown("##### Review History")

    history = get_history()
    if not history:
        st.caption("No reviews yet.")
    else:
        for row in history[:15]:
            severity_color = {
                "low": "#2ECC71",
                "medium": "#F39C12",
                "high": "#E74C3C",
            }.get(row["severity"], "#888")

            if st.button(
                f"{row['repo']}#{row['pr_number']} — {row['review_date'][:10]}",
                key=f"hist_{row['id']}",
                use_container_width=True,
            ):
                st.session_state["loaded_review_id"] = row["id"]

# ---------------------------------------------------------------------------
# Header
# ---------------------------------------------------------------------------
st.markdown(
    f"""
    <div class="main-header">
        <h1>{APP_TITLE}</h1>
        <p>Paste a GitHub PR URL and get an instant senior-engineer-level code review</p>
    </div>
    """,
    unsafe_allow_html=True,
)

# ---------------------------------------------------------------------------
# URL Input
# ---------------------------------------------------------------------------
col1, col2 = st.columns([4, 1])
with col1:
    pr_url = st.text_input(
        "GitHub PR URL",
        placeholder="https://github.com/owner/repo/pull/123",
        label_visibility="collapsed",
    )
with col2:
    review_clicked = st.button("Review", use_container_width=True)


# ---------------------------------------------------------------------------
# Helper: reconstruct ReviewResult from JSON
# ---------------------------------------------------------------------------
def _reconstruct_review(review_json: str) -> ReviewResult:
    """Parse a stored JSON string back into a ReviewResult dataclass."""
    data = json.loads(review_json)
    return ReviewResult(
        summary=data.get("summary", ""),
        severity=data.get("severity", "medium"),
        bugs=[Bug(**b) for b in data.get("bugs", [])],
        edge_cases=[EdgeCase(**e) for e in data.get("edge_cases", [])],
        optimizations=[Optimization(**o) for o in data.get("optimizations", [])],
        security=[SecurityIssue(**s) for s in data.get("security", [])],
        positives=data.get("positives", []),
    )


def consolidate_reviews(results: list, summaries: list) -> ReviewResult:
    """Consolidate multiple file-level ReviewResults into a single result."""
    bugs = []
    edge_cases = []
    optimizations = []
    security = []
    positives = []
    severity = "low"
    
    for r in results:
        bugs.extend(r.bugs)
        edge_cases.extend(r.edge_cases)
        optimizations.extend(r.optimizations)
        security.extend(r.security)
        positives.extend(r.positives)
        
        # severity logic: high > medium > low
        r_sev = r.severity.lower()
        if r_sev == "high":
            severity = "high"
        elif r_sev == "medium" and severity != "high":
            severity = "medium"

    summary = "### Consolidated File-by-File Review:\n\n" + "\n".join(summaries)
    return ReviewResult(
        summary=summary,
        severity=severity,
        bugs=bugs,
        edge_cases=edge_cases,
        optimizations=optimizations,
        security=security,
        positives=positives
    )


# ---------------------------------------------------------------------------
# State Initialization
# ---------------------------------------------------------------------------
if "current_review" not in st.session_state:
    st.session_state["current_review"] = None
if "current_pr_meta" not in st.session_state:
    st.session_state["current_pr_meta"] = None
if "current_owner" not in st.session_state:
    st.session_state["current_owner"] = None
if "current_repo" not in st.session_state:
    st.session_state["current_repo"] = None
if "current_pr_number" not in st.session_state:
    st.session_state["current_pr_number"] = None


# ---------------------------------------------------------------------------
# Load from history
# ---------------------------------------------------------------------------
    # Load from history
if st.session_state.get("loaded_review_id"):
    review_row = get_review_by_id(st.session_state["loaded_review_id"])
    if review_row:
        review_result = _reconstruct_review(review_row["review_json"])
        
        pr_meta = PRMetadata(
            title=f"Saved Review: {review_row['owner']}/{review_row['repo']}#{review_row['pr_number']}",
            description=f"Loaded from history. Reviewed on {review_row['review_date']}.",
            author="N/A",
            created_at=review_row["review_date"],
            base_branch="main",
            head_branch="feature",
            files_changed=0,
            total_additions=0,
            total_deletions=0,
            files=[],
            diff="",
            head_sha=""  # Cannot post inline to historical reviews
        )
        st.session_state["current_review"] = review_result
        st.session_state["current_pr_meta"] = pr_meta
        st.session_state["current_owner"] = review_row["owner"]
        st.session_state["current_repo"] = review_row["repo"]
        st.session_state["current_pr_number"] = review_row["pr_number"]
        
    st.session_state["loaded_review_id"] = None

# ---------------------------------------------------------------------------
# Run Review Pipeline
# ---------------------------------------------------------------------------
if review_clicked:
    if not pr_url.strip():
        st.error("Please enter a GitHub PR URL.")
    elif not github_token:
        st.error("GitHub token is required. Enter it in the sidebar or set GITHUB_TOKEN in .env")
    elif not openrouter_key:
        st.error("OpenRouter API key is required. Enter it in the sidebar or set OPENROUTER_API_KEY in .env")
    else:
        try:
            # 1. Parse URL
            owner, repo, pr_number = parse_pr_url(pr_url)
            st.session_state["current_owner"] = owner
            st.session_state["current_repo"] = repo
            st.session_state["current_pr_number"] = pr_number

            # 2. Fetch PR data
            with st.spinner("Fetching PR data from GitHub..."):
                pr_meta = fetch_pr_data(owner, repo, pr_number, github_token)
                st.session_state["current_pr_meta"] = pr_meta

            # 3. Select prompt
            prompt_fn = FOCUS_PROMPT_MAP.get(config["focus_mode"], base_review.get_prompt)
            system_prompt = prompt_fn()

            # 4. Get AI service
            ai_service = get_ai_service("openrouter", openrouter_key)

            # Determine if per-file is triggered
            is_per_file = False
            if config["per_file_analysis"] == "Enabled":
                is_per_file = True
            elif config["per_file_analysis"] == "Auto":
                if len(pr_meta.diff) > 20000 or pr_meta.files_changed > 3:
                    is_per_file = True

            if is_per_file:
                results = []
                summaries = []
                st.info(f"Large PR or Per-file mode triggered. Reviewing {len(pr_meta.files)} files individually...")
                
                for idx, file in enumerate(pr_meta.files):
                    if not file.patch:
                        continue
                    
                    st.markdown(f"##### Analyzing file {idx+1}/{len(pr_meta.files)}: `{file.filename}`")
                    
                    single_meta = PRMetadata(
                        title=pr_meta.title,
                        description=pr_meta.description,
                        author=pr_meta.author,
                        created_at=pr_meta.created_at,
                        base_branch=pr_meta.base_branch,
                        head_branch=pr_meta.head_branch,
                        files_changed=1,
                        total_additions=file.additions,
                        total_deletions=file.deletions,
                        files=[file],
                        diff=f"--- {file.filename} [{file.status}] (+{file.additions}/-{file.deletions})\n{file.patch}\n",
                        head_sha=pr_meta.head_sha
                    )
                    
                    # Stream raw content for this file
                    raw_chunks = []
                    placeholder = st.empty()
                    with placeholder.container():
                        st.markdown(f"_Streaming AI Response for `{file.filename}`:_")
                        def token_generator():
                            for chunk in ai_service.review_stream(single_meta, system_prompt):
                                raw_chunks.append(chunk)
                                yield chunk
                        st.write_stream(token_generator)
                    
                    raw_text = "".join(raw_chunks)
                    try:
                        res = ai_service.parse_raw_response(raw_text)
                        results.append(res)
                        summaries.append(f"- **{file.filename}**: {res.summary}")
                        st.success(f"Completed analysis for `{file.filename}`")
                    except Exception as parse_err:
                        st.warning(f"Failed to parse response for `{file.filename}`. Error: {parse_err}")
                
                if not results:
                    raise Exception("No file patches were successfully analyzed.")
                review_result = consolidate_reviews(results, summaries)
            else:
                # Stream full PR review
                st.info(f"Analyzing full PR using **{config['model']}**...")
                raw_chunks = []
                placeholder = st.empty()
                with placeholder.container():
                    st.markdown("_Streaming AI Response:_")
                    def token_generator():
                        for chunk in ai_service.review_stream(pr_meta, system_prompt):
                            raw_chunks.append(chunk)
                            yield chunk
                    st.write_stream(token_generator)
                
                raw_text = "".join(raw_chunks)
                review_result = ai_service.parse_raw_response(raw_text)

            st.success("Analysis complete!")
            st.session_state["current_review"] = review_result

            # 5. Save to history
            save_review(pr_url, owner, repo, pr_number, review_result)

        except ValueError as e:
            st.error(f"{e}")
        except Exception as e:
            error_msg = str(e)
            
            # Check if it's a credit error and display more prominently
            if "OpenRouter Account Out of Credits" in error_msg or "402" in error_msg:
                st.error(error_msg)
                st.info(
                    "**💡 Quick Fix:**\n\n"
                    "1. Visit [OpenRouter Credits](https://openrouter.ai/settings/credits)\n"
                    "2. Look for free credits or add a payment method\n"
                    "3. Generate a new API key if using a paid account\n"
                    "4. Update your `.env` file with the new key\n"
                    "5. Restart the app"
                )
            else:
                st.error(f"An error occurred: {error_msg}")
                st.exception(e)


# ---------------------------------------------------------------------------
# Unified Render Block
# ---------------------------------------------------------------------------
if st.session_state["current_review"] and st.session_state["current_pr_meta"]:
    pr_meta = st.session_state["current_pr_meta"]
    review_result = st.session_state["current_review"]
    owner = st.session_state["current_owner"]
    repo = st.session_state["current_repo"]
    pr_number = st.session_state["current_pr_number"]

    # 1. PR Metadata
    render_pr_metadata(pr_meta)

    # 1.5 One-Click Post to GitHub Button (Prominent)
    st.markdown("---")
    col_quick, col_spacer = st.columns([2, 3])
    
    with col_quick:
        if st.button(
            "🚀 Post Review to GitHub PR",
            use_container_width=True,
            help="Post both inline comments and summary review to the GitHub PR with one click",
        ):
            try:
                with st.spinner("Posting review to GitHub..."):
                    post_results = post_unified_review(
                        owner,
                        repo,
                        pr_number,
                        github_token,
                        review_result,
                        pr_meta.head_sha,
                    )
                
                # Build success/error message
                success_items = []
                error_items = []
                
                if post_results.get("inline_posted"):
                    success_items.append("✅ Inline comments posted")
                elif post_results.get("inline_posted") is False and post_results.get("inline_error"):
                    error_items.append(f"⚠️ Inline comments: {post_results.get('inline_error', 'Unknown error')}")
                
                if post_results.get("summary_posted"):
                    success_items.append("✅ Summary comment posted")
                elif post_results.get("summary_posted") is False and post_results.get("summary_error"):
                    error_items.append(f"❌ Summary: {post_results.get('summary_error', 'Unknown error')}")
                
                # Display results
                if success_items:
                    st.success("\n".join(success_items))
                    st.markdown(
                        f"[View PR on GitHub](https://github.com/{owner}/{repo}/pull/{pr_number})",
                        unsafe_allow_html=False,
                    )
                
                if error_items:
                    for error in error_items:
                        st.warning(error)
                
            except Exception as e:
                error_msg = str(e)
                st.error(f"Failed to post review:\n\n{error_msg}")
                
                # Provide helpful suggestion for 403 errors
                if "403" in error_msg or "Forbidden" in error_msg:
                    st.info(
                        "**💡 Fix this error:**\n\n"
                        "Your GitHub token needs the `repo` scope to post comments.\n\n"
                        "1. Go to [GitHub Settings → Tokens](https://github.com/settings/tokens)\n"
                        "2. Create a new token with `repo` scope\n"
                        "3. Update your `.env` file with the new token\n"
                        "4. Restart the app"
                    )

    st.markdown("---")

    if config["block_merge"]:
        if review_result.severity.lower() == "high":
            st.markdown("""
                <div style="
                    background-color: rgba(231,76,60,0.12);
                    border: 1px solid #E74C3C;
                    border-radius: 12px;
                    padding: 1.25rem 1.5rem;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 1.25rem;
                    box-shadow: 0 4px 15px rgba(231,76,60,0.05);
                ">
                    <div style="
                        background: #E74C3C;
                        color: white;
                        font-weight: 800;
                        font-size: 1.25rem;
                        padding: 6px 16px;
                        border-radius: 8px;
                        text-align: center;
                        box-shadow: 0 0 10px rgba(231,76,60,0.3);
                    ">
                        FAIL
                    </div>
                    <div>
                        <strong style="color:#E74C3C;font-size:1.1rem;margin:0;">Merge Gate Blocked</strong>
                        <p style="color:#b0b0b0;margin:3px 0 0 0;font-size:0.88rem;">
                            High severity issues were found. The merge is auto-blocked.
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)
        else:
            st.markdown("""
                <div style="
                    background-color: rgba(46,204,113,0.12);
                    border: 1px solid #2ECC71;
                    border-radius: 12px;
                    padding: 1.25rem 1.5rem;
                    margin-bottom: 1.5rem;
                    display: flex;
                    align-items: center;
                    gap: 1.25rem;
                    box-shadow: 0 4px 15px rgba(46,204,113,0.05);
                ">
                    <div style="
                        background: #2ECC71;
                        color: white;
                        font-weight: 800;
                        font-size: 1.25rem;
                        padding: 6px 16px;
                        border-radius: 8px;
                        text-align: center;
                        box-shadow: 0 0 10px rgba(46,204,113,0.3);
                    ">
                        PASS
                    </div>
                    <div>
                        <strong style="color:#2ECC71;font-size:1.1rem;margin:0;">Merge Gate Passed</strong>
                        <p style="color:#b0b0b0;margin:3px 0 0 0;font-size:0.88rem;">
                            No high severity issues found. Safe to merge.
                        </p>
                    </div>
                </div>
            """, unsafe_allow_html=True)

    # 3. Metrics
    render_metrics_bar(pr_meta, review_result)

    # 4. Review Tabs
    st.markdown("---")
    render_review_tabs(review_result)

    # 5. Diff Viewer (only if files exist)
    if pr_meta.files:
        st.markdown("---")
        render_diff_viewer(pr_meta.files)

    # 6. Action/Export Section
    st.markdown("---")
    st.markdown("### Additional Export & Options")
    st.caption("Use the 'Post Review to GitHub PR' button above to post with one click, or export/post individually below:")

    col_exp1, col_exp2, col_exp3, col_exp4 = st.columns(4)

    with col_exp1:
        json_export = export_as_json(review_result, pr_meta)
        st.download_button(
            "Download JSON",
            data=json_export,
            file_name=f"review_{repo}_{pr_number}.json",
            mime="application/json",
            use_container_width=True,
        )

    with col_exp2:
        md_export = export_as_markdown(review_result, pr_meta)
        st.download_button(
            "Download Markdown",
            data=md_export,
            file_name=f"review_{repo}_{pr_number}.md",
            mime="text/markdown",
            use_container_width=True,
        )

    with col_exp3:
        if st.button("Post Summary Comment", use_container_width=True):
            try:
                post_review_comment(owner, repo, pr_number, github_token, review_result)
                st.success("Summary comment posted to PR!")
            except Exception as e:
                st.error(f"Failed to post comment: {str(e)[:200]}")
                if "403" in str(e):
                    st.caption("💡 Your GitHub token needs `repo` scope. [Get a new token](https://github.com/settings/tokens)")


    with col_exp4:
        if pr_meta.head_sha:
            if st.button("Post Inline Review", use_container_width=True):
                try:
                    post_inline_review_comments(
                        owner, repo, pr_number, github_token, review_result, pr_meta.head_sha
                    )
                    st.success("Position-aware inline review posted to GitHub!")
                except Exception as e:
                    st.error(f"Failed to post inline review: {str(e)[:200]}")
                    if "403" in str(e):
                        st.caption("💡 Your GitHub token needs `repo` scope. [Get a new token](https://github.com/settings/tokens)")
        else:
            st.button(
                "Post Inline Review (N/A)",
                disabled=True,
                use_container_width=True,
                help="Commit SHA not available (only for live reviews, not historical)"
            )
            st.caption("💡 Available only for live PR reviews, not for historical reviews")



