"""Factory for creating AI service instances."""

from app.services.ai.base import BaseAIService
from app.services.ai.openrouter_service import OpenRouterService


def get_ai_service(provider: str, api_key: str) -> BaseAIService:
    """
    Create and return an AI service instance for the given provider.

    Args:
        provider: The provider name (e.g., "openrouter").
        api_key: The API key for the provider.

    Returns:
        An instance of BaseAIService.

    Raises:
        ValueError: If the provider is not supported.
    """
    providers = {
        "openrouter": lambda: OpenRouterService(api_key=api_key),
    }

    factory = providers.get(provider.lower())
    if factory is None:
        raise ValueError(
            f"Unsupported AI provider: '{provider}'. "
            f"Supported providers: {', '.join(providers.keys())}"
        )

    return factory()
