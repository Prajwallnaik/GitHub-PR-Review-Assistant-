# AI Code Review Assistant

A Streamlit web application that reviews GitHub Pull Requests using AI. Paste a PR URL, and get an instant senior-engineer-level code review covering bugs, edge cases, performance optimizations, and security issues.

## Features

- 🔍 **Comprehensive Code Review** — Analyzes PR diffs for bugs, edge cases, optimizations, and security issues
- 🎯 **Focus Modes** — Choose from Full Review, Security Audit, Performance, Readability, or Test Coverage
- 🤖 **Powered by Qwen** — Uses the Qwen 3 235B model via OpenRouter (free tier)
- 📊 **Rich UI** — Metrics dashboard, tabbed findings, color-coded diff viewer
- 💾 **Review History** — All reviews saved locally in SQLite
- 📥 **Export** — Download results as JSON or Markdown
- � **One-Click Post to GitHub** — Post the complete review directly to the PR with a single button click (includes inline comments + summary)
- 💬 **Granular Posting** — Post summary comments or inline reviews separately if preferred

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure credentials:**
   ```bash
   cp .env.example .env
   # Edit .env with your GitHub token and OpenRouter API key
   ```

3. **Run the app:**
   ```bash
   streamlit run main.py
   ```

4. **Paste a PR URL** and click "Review"!

## Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token with `repo` scope |
| `OPENROUTER_API_KEY` | API key from [openrouter.ai](https://openrouter.ai) |

## Project Structure

```
pr-review-assistant/
├── app/
│   ├── components/     # Streamlit UI components
│   ├── services/       # GitHub & AI service integrations
│   ├── prompts/        # System prompts for different review modes
│   ├── models/         # Python dataclasses
│   ├── utils/          # Parser, formatter, exporter
│   └── storage/        # SQLite review history
├── config/             # App settings and provider configs
├── tests/              # Unit tests with fixtures
├── main.py             # Entry point
└── requirements.txt
```

## Posting Reviews to GitHub

After generating a review, you have multiple options to share it:

### One-Click Posting (Recommended)
Click the **"🚀 Post Review to GitHub PR"** button at the top of the results to post both:
- **Inline comments** — Specific bug reports and issues linked to exact line numbers
- **Summary comment** — Comprehensive overview with all findings

### Granular Posting
Use the buttons in the "Additional Export & Options" section to:
- **Post Summary Comment** — Post only the overall review
- **Post Inline Review** — Post only the line-specific comments

The review is automatically saved to your local history regardless of posting status.

## Running Tests

```bash
pip install pytest
pytest tests/ -v
```
