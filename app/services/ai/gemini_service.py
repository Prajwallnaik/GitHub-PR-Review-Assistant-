"""Gemini AI service implementation using the OpenAI-compatible API."""

import json
import re
import time
from openai import OpenAI

from app.services.ai.base import BaseAIService
from app.models.pr import PRMetadata
from app.models.review import ReviewResult, Bug, EdgeCase, Optimization, SecurityIssue
from config.settings import MAX_DIFF_CHARS
from config.providers import PROVIDERS


class GeminiService(BaseAIService):
    """AI review service using Google Gemini (via OpenAI-compatible endpoint)."""

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        from config.settings import PER_FILE_ANALYSIS_ENABLED, PER_FILE_ANALYSIS_MODE
        
        base_url = PROVIDERS.get("gemini", {}).get(
            "base_url", "https://generativelanguage.googleapis.com/v1beta/openai/"
        )
        self.client = OpenAI(
            base_url=base_url,
            api_key=api_key,
        )
        self.model = model
        self.per_file_analysis_enabled = PER_FILE_ANALYSIS_ENABLED
        self.per_file_analysis_mode = PER_FILE_ANALYSIS_MODE

    def review(self, pr_metadata: PRMetadata, prompt: str) -> ReviewResult:
        """Send the PR diff to Gemini and parse the structured JSON response."""
        user_message = self._build_user_message(pr_metadata)
        analysis_prompt = self._enhance_prompt_with_per_file_analysis(prompt, pr_metadata)

        last_error = None
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": analysis_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                )

                raw_content = response.choices[0].message.content
                return self.parse_raw_response(raw_content)

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Handle rate limits
                if "rate" in error_str or "429" in error_str or "limit" in error_str:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                raise

        raise last_error

    def review_stream(self, pr_metadata: PRMetadata, prompt: str):
        """Stream the review response chunk-by-chunk."""
        user_message = self._build_user_message(pr_metadata)
        analysis_prompt = self._enhance_prompt_with_per_file_analysis(prompt, pr_metadata)

        last_error = None
        for attempt in range(3):
            try:
                response_stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": analysis_prompt},
                        {"role": "user", "content": user_message},
                    ],
                    temperature=0.3,
                    max_tokens=4096,
                    stream=True,
                )
                for chunk in response_stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                return

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Handle rate limits
                if "rate" in error_str or "429" in error_str or "limit" in error_str:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                raise

        raise last_error

    def _enhance_prompt_with_per_file_analysis(self, base_prompt: str, pr_metadata: PRMetadata) -> str:
        from config.settings import PER_FILE_ANALYSIS_AUTO_THRESHOLD
        
        should_enable = self.per_file_analysis_enabled
        
        if self.per_file_analysis_mode == "disabled":
            should_enable = False
        elif self.per_file_analysis_mode == "auto":
            diff_size = len(pr_metadata.diff)
            is_large_pr = diff_size > PER_FILE_ANALYSIS_AUTO_THRESHOLD
            should_enable = is_large_pr or pr_metadata.files_changed > 3
        
        if should_enable:
            per_file_directive = (
                "\n\n### Per-File Analysis Mode (ENABLED)\n"
                "Analyze each modified file individually. For each file:\n"
                "1. Identify the file's purpose and context\n"
                "2. Review changes specific to that file\n"
                "3. Check for file-specific issues (imports, dependencies, style)\n"
                "4. Consider how changes affect file functionality\n"
                "Then provide holistic review across all files."
            )
            return base_prompt + per_file_directive
        else:
            per_file_directive = "\n\n### Per-File Analysis Mode (DISABLED)\nProvide a general holistic review of all changes."
            return base_prompt + per_file_directive

    def _build_user_message(self, pr_metadata: PRMetadata) -> str:
        parts = [
            f"## Pull Request: {pr_metadata.title}",
            f"**Author:** {pr_metadata.author}",
            f"**Branch:** {pr_metadata.head_branch} → {pr_metadata.base_branch}",
            f"**Description:** {pr_metadata.description or 'No description provided.'}",
            f"**Files changed:** {pr_metadata.files_changed}",
            f"**Additions:** +{pr_metadata.total_additions}  |  **Deletions:** -{pr_metadata.total_deletions}",
            "",
            "## Diff",
            "```",
            pr_metadata.diff[:MAX_DIFF_CHARS],
            "```",
        ]
        return "\n".join(parts)

    def parse_raw_response(self, raw_content: str) -> ReviewResult:
        content = raw_content.strip()

        # Remove markdown code fences if present
        content = re.sub(r"^```(?:json)?\s*\n?", "", content)
        content = re.sub(r"\n?```\s*$", "", content)
        content = content.strip()

        # Remove <think>...</think> blocks if present
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL)
        content = content.strip()

        data = json.loads(content)

        bugs = [
            Bug(
                file=b.get("file", ""),
                line=str(b.get("line", "")),
                issue=b.get("issue", ""),
                fix=b.get("fix", ""),
            )
            for b in data.get("bugs", [])
        ]

        edge_cases = [
            EdgeCase(
                description=ec.get("description", ""),
                suggestion=ec.get("suggestion", ""),
            )
            for ec in data.get("edge_cases", [])
        ]

        optimizations = [
            Optimization(
                description=o.get("description", ""),
                impact=o.get("impact", "low"),
            )
            for o in data.get("optimizations", [])
        ]

        security = [
            SecurityIssue(
                issue=s.get("issue", ""),
                recommendation=s.get("recommendation", ""),
            )
            for s in data.get("security", [])
        ]

        return ReviewResult(
            summary=data.get("summary", "No summary provided."),
            severity=data.get("severity", "medium"),
            bugs=bugs,
            edge_cases=edge_cases,
            optimizations=optimizations,
            security=security,
            positives=data.get("positives", []),
        )
