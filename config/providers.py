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
    },
    "gemini": {
        "display_name": "Google Gemini",
        "base_url": "https://generativelanguage.googleapis.com/v1beta/openai/",
        "models": [
            {
                "id": "gemini-2.5-flash",
                "display_name": "Gemini 2.5 Flash",
            },
            {
                "id": "gemini-2.5-pro",
                "display_name": "Gemini 2.5 Pro",
            },
            {
                "id": "gemini-1.5-flash",
                "display_name": "Gemini 1.5 Flash",
            }
        ],
        "free_tier": "Free tier available",
    }
}

DEFAULT_PROVIDER = "openrouter"
DEFAULT_MODEL = "qwen/qwen3-235b-a22b"


