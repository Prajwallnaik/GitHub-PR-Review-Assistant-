"""Abstract base class for AI review services."""

from abc import ABC, abstractmethod
from app.models.pr import PRMetadata
from app.models.review import ReviewResult


class BaseAIService(ABC):
    """Abstract base for AI-powered code review services."""

    @abstractmethod
    def review(self, pr_metadata: PRMetadata, prompt: str) -> ReviewResult:
        """
        Perform an AI code review on a pull request.

        Args:
            pr_metadata: The PR metadata including diff content.
            prompt: The system prompt to use for the review.

        Returns:
            A ReviewResult dataclass with the structured review.
        """
        pass

    @abstractmethod
    def review_stream(self, pr_metadata: PRMetadata, prompt: str):
        """
        Stream the review response chunk-by-chunk.

        Args:
            pr_metadata: The PR metadata.
            prompt: The system prompt.

        Yields:
            str: Token chunks from the AI response.
        """
        pass

    @abstractmethod
    def parse_raw_response(self, raw_content: str) -> ReviewResult:
        """
        Parse raw response content into a ReviewResult dataclass.

        Args:
            raw_content: Raw text content from the AI response.

        Returns:
            ReviewResult dataclass.
        """
        pass

