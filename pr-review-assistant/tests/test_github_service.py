"""Tests for the GitHub service (mocked)."""

import json
import sys
import os
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app.services.github_service import fetch_pr_data


def _load_fixture(name):
    path = os.path.join(os.path.dirname(__file__), "fixtures", name)
    with open(path) as f:
        return json.load(f)


@patch("app.services.github_service.requests.get")
def test_fetch_pr_data(mock_get):
    """Test that fetch_pr_data assembles PRMetadata correctly."""
    pr_json = _load_fixture("sample_pr.json")

    files_json = [
        {
            "filename": "auth/login.py",
            "status": "modified",
            "additions": 5,
            "deletions": 2,
            "patch": "@@ -40,7 +40,10 @@\n-old\n+new",
        }
    ]

    # Mock responses
    mock_pr_resp = MagicMock()
    mock_pr_resp.json.return_value = pr_json
    mock_pr_resp.raise_for_status = MagicMock()

    mock_files_resp = MagicMock()
    mock_files_resp.json.return_value = files_json
    mock_files_resp.raise_for_status = MagicMock()

    mock_get.side_effect = [mock_pr_resp, mock_files_resp]

    result = fetch_pr_data("octocat", "hello-world", 1, "fake-token")

    assert result.title == "Fix login validation bug"
    assert result.author == "octocat"
    assert result.files_changed == 1
    assert result.total_additions == 5
    assert result.total_deletions == 2
    assert len(result.files) == 1
    assert result.files[0].filename == "auth/login.py"
