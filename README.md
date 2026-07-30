# Email Agent

TL;DR: Personal AI agent that drafts Gmail replies in your voice and saves them as drafts — read-only + compose scopes, never sends automatically.

## Quick facts
- Tech: Python, ChromaDB (local), Playwright (optional), OpenAI API (configurable)
- Purpose: Automate drafting replies while keeping human approval before send
- Contact: yvakhilteja1104@gmail.com
- License: MIT — see LICENSE

## Quick start
1. Install dependencies:
```bash
pip install -r requirements.txt
```
2. Configure API keys / Gmail credentials (see README details):
- Set OPENAI API key: `export OPENAI_API_KEY="sk-..."`
- Place Google OAuth `credentials.json` in the project root (desktop OAuth client)
3. Build the local RAG store:
```bash
python knowledge.py
```
4. Dry run with mock inbox:
```bash
python run.py
```
5. One-time pass over real unread Gmail (creates drafts only):
```bash
python real_run.py
```

## Security notes
- OAuth scopes: `gmail.readonly` and `gmail.compose` only — send is not requested.
- `credentials.json`, `token.json`, `seen.json`, and local `my_db/` are gitignored and should never be committed.

## Contributing
Open issues or PRs. See ISSUE_TEMPLATE.md and PULL_REQUEST_TEMPLATE.md for guidance.
