"""Configuration constants and settings."""

import os

# AI settings
MAX_DIFF_CHARS = 80000

# Display settings
MAX_FILES_IN_DIFF_VIEWER = 10

# Database
SQLITE_DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "reviews.db")

# App
APP_TITLE = "AI Code Review Assistant"


# Network
REQUEST_TIMEOUT_SECONDS = 60
