"""Export review results as JSON or Markdown."""

import json
from dataclasses import asdict
from app.models.review import ReviewResult
from app.models.pr import PRMetadata


def export_as_json(review: ReviewResult, pr_meta: PRMetadata) -> str:
    """Serialize a ReviewResult and PRMetadata to a formatted JSON string."""
    data = {
        "pr_metadata": {
            "title": pr_meta.title,
            "author": pr_meta.author,
            "created_at": pr_meta.created_at,
            "base_branch": pr_meta.base_branch,
            "head_branch": pr_meta.head_branch,
            "files_changed": pr_meta.files_changed,
            "total_additions": pr_meta.total_additions,
            "total_deletions": pr_meta.total_deletions,
        },
        "review": asdict(review),
    }
    return json.dumps(data, indent=2, ensure_ascii=False)


def export_as_markdown(review: ReviewResult, pr_meta: PRMetadata) -> str:
    """Format the review as a readable Markdown report."""
    lines = []
    lines.append(f"# Code Review Report")
    lines.append(f"## PR: {pr_meta.title}")
    lines.append(f"**Author:** {pr_meta.author}  ")
    lines.append(f"**Date:** {pr_meta.created_at}  ")
    lines.append(f"**Branch:** `{pr_meta.head_branch}` → `{pr_meta.base_branch}`  ")
    lines.append(f"**Files Changed:** {pr_meta.files_changed} | "
                  f"**+{pr_meta.total_additions}** / **-{pr_meta.total_deletions}**")
    lines.append("")

    lines.append(f"## Summary")
    lines.append(f"**Severity:** {review.severity.upper()}")
    lines.append("")
    lines.append(review.summary)
    lines.append("")

    if review.bugs:
        lines.append("## Bugs Found")
        lines.append("| File | Line | Issue | Fix |")
        lines.append("|------|------|-------|-----|")
        for bug in review.bugs:
            lines.append(f"| `{bug.file}` | {bug.line} | {bug.issue} | {bug.fix} |")
        lines.append("")

    if review.edge_cases:
        lines.append("## Edge Cases")
        for ec in review.edge_cases:
            lines.append(f"- **{ec.description}**  ")
            lines.append(f"  _Suggestion:_ {ec.suggestion}")
        lines.append("")

    if review.optimizations:
        lines.append("## Optimizations")
        for opt in review.optimizations:
            lines.append(f"- [{opt.impact.upper()}] **{opt.description}**")
        lines.append("")

    if review.security:
        lines.append("## Security Issues")
        for sec in review.security:
            lines.append(f"- **{sec.issue}**  ")
            lines.append(f"  _Recommendation:_ {sec.recommendation}")
        lines.append("")

    if review.positives:
        lines.append("## Positives")
        for pos in review.positives:
            lines.append(f"- {pos}")
        lines.append("")


    return "\n".join(lines)
