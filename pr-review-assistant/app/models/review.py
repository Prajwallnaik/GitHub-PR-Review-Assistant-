"""Data models for code review results."""

from dataclasses import dataclass, field
from typing import List


@dataclass
class Bug:
    """A bug found during code review."""
    file: str
    line: str
    issue: str
    fix: str


@dataclass
class EdgeCase:
    """An edge case identified during review."""
    description: str
    suggestion: str


@dataclass
class Optimization:
    """A performance optimization suggestion."""
    description: str
    impact: str  # "low", "medium", or "high"


@dataclass
class SecurityIssue:
    """A security vulnerability or concern."""
    issue: str
    recommendation: str


@dataclass
class ReviewResult:
    """The complete result of an AI code review."""
    summary: str
    severity: str  # "low", "medium", or "high"
    bugs: List[Bug] = field(default_factory=list)
    edge_cases: List[EdgeCase] = field(default_factory=list)
    optimizations: List[Optimization] = field(default_factory=list)
    security: List[SecurityIssue] = field(default_factory=list)
    positives: List[str] = field(default_factory=list)
