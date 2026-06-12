"""Tests for the Gemini AI service (mocked)."""

import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.ai.gemini_service import GeminiService
from app.models.pr import PRMetadata, PRFile


def _make_pr_metadata():
    return PRMetadata(
        title="Test PR",
        description="A test pull request.",
        author="tester",
        created_at="2024-01-01T00:00:00Z",
        base_branch="main",
        head_branch="feature/test",
        files_changed=1,
        total_additions=10,
        total_deletions=3,
        files=[
            PRFile(
                filename="test.py",
                status="modified",
                additions=10,
                deletions=3,
                patch="+new line\n-old line",
            )
        ],
        diff="+new line\n-old line",
    )


def _load_sample_review():
    path = os.path.join(os.path.dirname(__file__), "fixtures", "sample_review.json")
    with open(path) as f:
        return f.read()


@patch("app.services.ai.gemini_service.OpenAI")
def test_review_parses_json(mock_openai_class):
    """Test that the Gemini service correctly parses the AI JSON response."""
    sample_json = _load_sample_review()

    # Mock the chat completion response
    mock_message = MagicMock()
    mock_message.content = sample_json

    mock_choice = MagicMock()
    mock_choice.message = mock_message

    mock_completion = MagicMock()
    mock_completion.choices = [mock_choice]

    mock_client = MagicMock()
    mock_client.chat.completions.create.return_value = mock_completion
    mock_openai_class.return_value = mock_client

    service = GeminiService(api_key="fake-key", model="gemini-2.5-flash")
    pr_meta = _make_pr_metadata()

    result = service.review(pr_meta, "You are a reviewer.")

    assert result.summary == "Overall good PR with minor issues."
    assert result.severity == "low"
    assert len(result.bugs) == 1
    assert result.bugs[0].file == "auth/login.py"
    assert len(result.edge_cases) == 1
    assert len(result.optimizations) == 1
    assert len(result.security) == 1
    assert len(result.positives) == 2
