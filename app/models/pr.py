"""Data models for Pull Request metadata."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class PRFile:
    """Represents a single file in a pull request."""
    filename: str
    status: str
    additions: int
    deletions: int
    patch: str = ""


@dataclass
class PRMetadata:
    """Represents the full metadata of a pull request."""
    title: str
    description: str
    author: str
    created_at: str
    base_branch: str
    head_branch: str
    files_changed: int
    total_additions: int
    total_deletions: int
    files: List[PRFile] = field(default_factory=list)
    diff: str = ""
    head_sha: str = ""

