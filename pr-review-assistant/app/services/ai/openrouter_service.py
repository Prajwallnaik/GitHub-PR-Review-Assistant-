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
        self.client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key,
        )
        self.model = model

    def review(self, pr_metadata: PRMetadata, prompt: str) -> ReviewResult:
        """
        Send the PR diff to the AI model and parse the structured JSON response.

        Includes retry logic: up to 3 attempts with 2-second delay for rate limits.
        """
        # Build user message with PR context
        user_message = self._build_user_message(pr_metadata)

        last_error = None
        for attempt in range(3):
            try:
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": prompt},
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
        """Stream the review response chunk-by-chunk."""
        user_message = self._build_user_message(pr_metadata)

        last_error = None
        for attempt in range(3):
            try:
                response_stream = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": prompt},
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

