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

# Per-file Analysis
PER_FILE_ANALYSIS_ENABLED = os.getenv("PER_FILE_ANALYSIS_ENABLED", "true").lower() == "true"
PER_FILE_ANALYSIS_MODE = os.getenv("PER_FILE_ANALYSIS_MODE", "auto")  # auto, always, disabled
PER_FILE_ANALYSIS_AUTO_THRESHOLD = int(os.getenv("PER_FILE_ANALYSIS_AUTO_THRESHOLD", "3000"))  # chars

# Network
REQUEST_TIMEOUT_SECONDS = 60
