"""Supported AI provider configurations."""

PROVIDERS = {
    "openrouter": {
        "display_name": "OpenRouter",
        "base_url": "https://openrouter.ai/api/v1",
        "models": [
            {
                "id": "qwen/qwen3-235b-a22b",
                "display_name": "Qwen 3 235B A22B",
            }
        ],
        "free_tier": "Paid model",
    }
}

DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL = "qwen/qwen3-235b-a22b"

