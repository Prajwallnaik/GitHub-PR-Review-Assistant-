"""URL parser for GitHub Pull Request URLs."""

import re


def parse_pr_url(url: str) -> tuple:
    """
    Parse a GitHub Pull Request URL and extract owner, repo, and PR number.

    Args:
        url: A GitHub PR URL like https://github.com/owner/repo/pull/123

    Returns:
        Tuple of (owner, repo, pr_number)

    Raises:
        ValueError: If the URL does not match the expected GitHub PR pattern.
    """
    pattern = r"https?://github\.com/([^/]+)/([^/]+)/pull/(\d+)"
    match = re.match(pattern, url.strip())

    if not match:
        raise ValueError(
            f"Invalid GitHub PR URL: '{url}'. "
            "Expected format: https://github.com/owner/repo/pull/123"
        )

    owner = match.group(1)
    repo = match.group(2)
    pr_number = int(match.group(3))

    return owner, repo, pr_number
