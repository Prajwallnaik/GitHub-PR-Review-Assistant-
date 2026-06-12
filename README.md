# AI PR Review Assistant

<div align="center">

**Automated Code Review Agent — powered by Gemini, OpenRouter, and GitHub REST API**

[![Python](https://img.shields.io/badge/Python-3.9%2B-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-UI-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white)](https://streamlit.io/)
[![GitHub](https://img.shields.io/badge/GitHub-API-181717?style=for-the-badge&logo=github&logoColor=white)](https://docs.github.com/en/rest)
[![Google Gemini](https://img.shields.io/badge/Google_Gemini-LLM-4285F4?style=for-the-badge&logo=google&logoColor=white)](https://ai.google.dev/)
[![OpenRouter](https://img.shields.io/badge/OpenRouter-LLM-005CED?style=for-the-badge)](https://openrouter.ai/)
[![SQLite](https://img.shields.io/badge/SQLite-Database-003B57?style=for-the-badge&logo=sqlite&logoColor=white)](https://sqlite.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-22C55E?style=for-the-badge)](./LICENSE)

</div>

---

## Overview

**AI PR Review Assistant** is an automated code review application that analyzes GitHub Pull Request diffs. By pasting a PR URL, you get an instant, structured code review covering syntax bugs, logical edge cases, performance bottlenecks, and security vulnerabilities. Reviews can be posted directly back to the pull request on GitHub in a single click, generating inline code annotations mapped to exact modified lines along with a high-level review summary comment.

### Core Features

- **Comprehensive Code Review:** Scans changes for code defects, missing bounds checks, performance optimizations, and security vulnerabilities.
- **Focus Modes:** Tailor the review criteria by choosing from Full Review, Security Audit, Performance, Readability, or Test Coverage.
- **Multi-Provider Support:** Supports both Google Gemini (direct API access) and OpenRouter models (such as Qwen 3 235B) to perform the evaluations.
- **Color-Coded Diff Viewer:** Visualizes code changes in a structured UI dashboard with tabbed findings and metrics.
- **Review History:** Stores all past reviews locally in SQLite, allowing you to reload historical PR analyses instantly from the sidebar.
- **One-Click Post to GitHub:** Automatically posts inline annotations on the exact diff lines and writes a summary evaluation directly onto the PR.

---

## Architecture & Pipeline

### Step-by-Step Process

| Step | Module | Description |
|------|--------|-------------|
| **1. PR Parsing** | [parser.py](file:///d:/GitHub/app/utils/parser.py) | Extracts the owner, repository, and pull request number from the input GitHub URL. |
| **2. GitHub Retrieval** | [github_service.py](file:///d:/GitHub/app/services/github_service.py) | Authenticates with the GitHub REST API using OAuth credentials to fetch PR metadata and files changed. |
| **3. Focus Routing** | [main.py](file:///d:/GitHub/main.py) | Maps user preferences to specific review prompts (Security, Performance, Readability, Coverage, or Full). |
| **4. Ingestion & Request** | [factory.py](file:///d:/GitHub/app/services/ai/factory.py) | Routes the prompts and file diff patches to the selected provider (OpenRouter Qwen or Google Gemini API). |
| **5. Response Parsing** | [factory.py](file:///d:/GitHub/app/services/ai/factory.py) | Cleans reasoning tokens (such as Qwen-think blocks) and parses structured JSON findings into Python models. |
| **6. Local Storage** | [history.py](file:///d:/GitHub/app/storage/history.py) | Saves the structured findings, metadata, and JSON responses into a local SQLite repository for history tracking. |
| **7. Unified Review Posting** | [github_service.py](file:///d:/GitHub/app/services/github_service.py) | Transmits position-aware inline annotations and a comprehensive summary comment to the GitHub PR in a single API review action. |

---

## Tech Stack

- **UI:** Streamlit (clean Corporate Dark-mode interface).
- **AI Integration:** Google Gemini API, OpenRouter (Qwen 3 235B).
- **Version Control Integration:** GitHub REST API.
- **Database:** SQLite (local history repository).
- **Testing:** Pytest.

---

## Getting Started

### Prerequisites
- Python **3.9+**
- A **GitHub Personal Access Token (PAT)** (classic or fine-grained with read/write access to Pull Requests and Issues)
- An **OpenRouter API Key** or **Google Gemini API Key**

### Installation
```bash
# 1. Clone the repository
git clone https://github.com/Prajwallnaik/GitHub-PR-Review-Assistant-.git
cd GitHub-PR-Review-Assistant-

# 2. Install dependencies
pip install -r requirements.txt
```

### Configuration
Create a `.env` file in the project root:
```env
GITHUB_TOKEN=your_github_token_here
OPENROUTER_API_KEY=your_openrouter_key_here
GEMINI_API_KEY=your_gemini_key_here
```

### Run the App
```bash
python -m streamlit run main.py
```
Open `http://localhost:8501` to start reviewing your pull requests.

---

## Project Structure

```text
GitHub-PR-Review-Assistant-/
│
├── main.py                 # Streamlit UI -- main entry point & dashboard
│
├── app/                    # Core application package
│   ├── components/         # Streamlit UI components (diff viewer, sidebar, tabs)
│   ├── services/           # GitHub API & AI provider service integrations
│   ├── models/             # Python data structures for PRs and reviews
│   ├── prompts/            # System prompts for different review modes
│   ├── utils/              # Data parsing, badging, and export formatting helpers
│   └── storage/            # SQLite local history schema and initialization
│
├── config/                 # App configurations and provider declarations
│
├── tests/                  # Unit test suite with mock fixtures
│
├── requirements.txt        # Python package dependencies
├── .env                    # Environment credentials (git-ignored)
└── .gitignore
```

---

## Running Tests

Verify the integration of components and API mocks by running the test suite:
```bash
python -m pytest tests/ -v
```

---

## License

This project is licensed under the **MIT License** — you are free to use, modify, and distribute it.

```
MIT License — Copyright (c) 2026 Prajwal Naik
```

See the [LICENSE](./LICENSE) file for full details.
