"""OpenRouter AI service implementation using the OpenAI-compatible API."""

import json
import re
import time
from openai import OpenAI

from app.services.ai.base import BaseAIService
from app.models.pr import PRMetadata
from app.models.review import ReviewResult, Bug, EdgeCase, Optimization, SecurityIssue
from config.settings import MAX_DIFF_CHARS
from config.providers import DEFAULT_MODEL


class OpenRouterService(BaseAIService):
    """AI review service using OpenRouter (OpenAI-compatible)."""

    def __init__(self, api_key: str, model: str = DEFAULT_MODEL):
        from config.settings import PER_FILE_ANALYSIS_ENABLED, PER_FILE_ANALYSIS_MODE
        
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model
        self.per_file_analysis_enabled = PER_FILE_ANALYSIS_ENABLED
        self.per_file_analysis_mode = PER_FILE_ANALYSIS_MODE

    def review(self, pr_metadata: PRMetadata, prompt: str) -> ReviewResult:
        """
        Send the PR diff to the AI model and parse the structured JSON response.

        Includes retry logic: up to 3 attempts with 2-second delay for rate limits.
        Per-file analysis is enabled dynamically based on PR size and configuration.
        """
        # Build user message with PR context
        user_message = self._build_user_message(pr_metadata)
        
        # Dynamically enable per-file analysis based on PR size
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
                    extra_headers={"HTTP-Referer": "pr-review-assistant", "X-Title": "PR Review Assistant"},
                )

                raw_content = response.choices[0].message.content
                return self.parse_raw_response(raw_content)

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Handle insufficient credits (402)
                if "402" in error_str or "credits" in error_str:
                    raise Exception(
                        "❌ OpenRouter Account Out of Credits\n\n"
                        "Your OpenRouter account doesn't have enough credits to run this review.\n\n"
                        "**Solutions:**\n"
                        "1. **Get Free Credits** (Recommended for Testing)\n"
                        "   - Visit: https://openrouter.ai/settings/credits\n"
                        "   - Check if you have any free credits or promotions\n\n"
                        "2. **Upgrade to Paid** (For Production)\n"
                        "   - Visit: https://openrouter.ai/settings/billing\n"
                        "   - Add a payment method\n"
                        "   - Set a monthly credit limit\n\n"
                        "3. **Use a Different API Key**\n"
                        "   - If you have another OpenRouter account with credits, use that key instead\n"
                        "   - Update the OPENROUTER_API_KEY in your .env file"
                    )
                
                # Handle rate limits
                if "rate" in error_str or "429" in error_str or "limit" in error_str:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                raise

        raise last_error

    def review_stream(self, pr_metadata: PRMetadata, prompt: str):
        """Stream the review response chunk-by-chunk with dynamic per-file analysis."""
        user_message = self._build_user_message(pr_metadata)
        
        # Dynamically enable per-file analysis based on PR size
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
                    extra_headers={"HTTP-Referer": "pr-review-assistant", "X-Title": "PR Review Assistant"},
                )
                for chunk in response_stream:
                    content = chunk.choices[0].delta.content
                    if content:
                        yield content
                return

            except Exception as e:
                last_error = e
                error_str = str(e).lower()
                
                # Handle insufficient credits (402)
                if "402" in error_str or "credits" in error_str:
                    raise Exception(
                        "❌ OpenRouter Account Out of Credits\n\n"
                        "Your OpenRouter account doesn't have enough credits to run this review.\n\n"
                        "**Solutions:**\n"
                        "1. **Get Free Credits** (Recommended for Testing)\n"
                        "   - Visit: https://openrouter.ai/settings/credits\n"
                        "   - Check if you have any free credits or promotions\n\n"
                        "2. **Upgrade to Paid** (For Production)\n"
                        "   - Visit: https://openrouter.ai/settings/billing\n"
                        "   - Add a payment method\n"
                        "   - Set a monthly credit limit\n\n"
                        "3. **Use a Different API Key**\n"
                        "   - If you have another OpenRouter account with credits, use that key instead\n"
                        "   - Update the OPENROUTER_API_KEY in your .env file\n\n"
                        "4. **Reduce Token Usage** (Temporary Workaround)\n"
                        "   - Edit max_tokens from 4096 to 2048 to use fewer credits per request"
                    )
                
                # Handle rate limits
                if "rate" in error_str or "429" in error_str or "limit" in error_str:
                    if attempt < 2:
                        time.sleep(2)
                        continue
                raise

        raise last_error

    def _enhance_prompt_with_per_file_analysis(self, base_prompt: str, pr_metadata: PRMetadata) -> str:
        """
        Dynamically enhance the prompt with per-file analysis directives.
        
        Determines if per-file analysis should be enabled based on:
        - Configuration mode (always, auto, disabled)
        - PR size (number of changed files)
        - Diff size (characters in diff)
        """
        from config.settings import PER_FILE_ANALYSIS_AUTO_THRESHOLD
        
        # Determine if per-file analysis should be active
        should_enable = self.per_file_analysis_enabled
        
        if self.per_file_analysis_mode == "disabled":
            should_enable = False
        elif self.per_file_analysis_mode == "auto":
            # Automatically enable for larger PRs
            diff_size = len(pr_metadata.diff)
            is_large_pr = diff_size > PER_FILE_ANALYSIS_AUTO_THRESHOLD
            should_enable = is_large_pr or pr_metadata.files_changed > 3
        
        # Add per-file analysis directives to the prompt
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
        """Assemble the user message from PR metadata fields."""
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
        """Strip markdown fences and parse JSON into a ReviewResult."""
        content = raw_content.strip()

        # Remove markdown code fences if present
        content = re.sub(r"^```(?:json)?\s*\n?", "", content)
        content = re.sub(r"\n?```\s*$", "", content)
        content = content.strip()

        # Remove <think>...</think> blocks that Qwen sometimes adds
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

