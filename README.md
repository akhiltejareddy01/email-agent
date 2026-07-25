# Email Agent

A personal AI agent that reads your Gmail inbox, decides what each email actually needs, and — for the ones that deserve a reply — drafts one **in your own voice**, using real facts about you. It never sends anything on its own; every reply lands in Gmail's Drafts folder for you to review first.

This started as a step-by-step learning project (see [How this was built](#how-this-was-built)) and grew into a working agent that connects to a real inbox.

## What it actually does

1. Pulls your unread Gmail messages.
2. Asks an LLM to **decide** what to do with each one: draft a reply, or skip it (newsletters, spam, notifications).
3. For anything worth a reply, it:
   - retrieves the handful of facts about you that are relevant to *this specific email* (not your whole life story — just what's relevant), and
   - writes the reply in your established tone, greeting, and sign-off style.
4. Saves the reply as a **Gmail draft** — nothing is ever sent automatically.
5. Remembers which emails it already handled, so re-runs never duplicate a draft.

## How it works

```
                 ┌─────────────┐
   Gmail inbox → │  gmail.py   │  read unread mail, create drafts
                 └──────┬──────┘   (read + compose scopes only — no send)
                        │
                        ▼
                 ┌─────────────┐
                 │  tools.py   │  decide_action() → "draft" or "skip"
                 └──────┬──────┘
                        │ if "draft"
           ┌────────────┼────────────┐
           ▼                         ▼
   ┌───────────────┐        ┌───────────────┐
   │ knowledge.py  │        │   style.py    │
   │ (Chroma RAG)  │        │ (voice/tone)  │
   │ relevant facts│        │ always loaded │
   │ about you     │        │ in full       │
   └───────┬───────┘        └───────┬───────┘
           └───────────┬────────────┘
                        ▼
                 ┌─────────────┐
                 │   llm.py    │  one shared call to the LLM (OpenAI API)
                 └──────┬──────┘
                        ▼
                draft_reply() text
                        │
                        ▼
                 ┌─────────────┐
                 │  gmail.py   │  create_draft() → saved to Gmail Drafts
                 └─────────────┘
                        │
                 ┌─────────────┐
                 │  memory.py  │  marks the email "seen" so it's never
                 └─────────────┘  redrafted on the next run
```

**Two different kinds of "context about you," used differently:**
- **Facts** ([my_data/about_me.md](my_data/about_me.md)) are chunked and embedded into a local **ChromaDB** vector store ([knowledge.py](knowledge.py)). For each email, only the top-k most relevant facts are retrieved — the agent doesn't dump your whole background into every reply.
- **Style** ([my_data/style_guide.md](my_data/style_guide.md), [my_data/sent_examples.md](my_data/sent_examples.md)) isn't searched — it's small enough that the full text is fed into every drafting prompt ([style.py](style.py)), so tone stays consistent.

## Project layout

| File | Role |
|---|---|
| [llm.py](llm.py) | One shared function, `ask()`, that talks to the LLM (OpenAI API). Every other module calls through this — swapping models means editing one file. |
| [gmail.py](gmail.py) | Talks to the real Gmail API: OAuth login, fetch unread mail with full body text, create draft replies. Requests **read + compose** scopes only — the app is structurally incapable of sending mail. |
| [inbox.py](inbox.py) | A small hardcoded mock inbox, used for safe local testing without touching real Gmail. |
| [tools.py](tools.py) | The agent's actions: `classify()`, `summarize()`, `decide_action()`, `draft_reply()`. |
| [knowledge.py](knowledge.py) | Chunks `about_me.md` and stores it in a local ChromaDB collection; retrieves the facts most relevant to a given email. |
| [style.py](style.py) | Loads your style guide + example sent emails as one text block for the drafting prompt. |
| [memory.py](memory.py) | Tracks which email IDs have already been handled (`seen.json`), so nothing is drafted twice. |
| [agent.py](agent.py) | Runs the **agentic** loop over the mock inbox — the LLM itself decides draft-vs-skip per email. |
| [run.py](run.py) | An earlier, simpler pipeline over the mock inbox — classify → summarize → draft, driven by fixed Python logic rather than an LLM decision. |
| [real_run.py](real_run.py) | One-shot run against your **real** Gmail: fetch unread mail, decide, draft, leave results in Drafts. |
| [schedular.py](schedular.py) | The always-on version: polls real Gmail every few minutes, drafts replies for anything new, sleeps, repeats. |

## Setup

**1. Install dependencies**
```bash
pip install -r requirements.txt
```

**2. Set your OpenAI API key**
```bash
setx OPENAI_API_KEY "sk-..."      # Windows (restart terminal after)
# or: export OPENAI_API_KEY="sk-..."   (macOS/Linux)
```

**3. Get Gmail API credentials**
- In [Google Cloud Console](https://console.cloud.google.com/), create a project and enable the **Gmail API**.
- Create an OAuth client ID (Desktop app) and download it as `credentials.json` in the project root.
- This file — and the `token.json` it generates after your first login — are already excluded via `.gitignore` and must never be committed.

**4. Fill in your personal context**

Edit the files in [my_data/](my_data/):
- `about_me.md` — facts about you (role, experience, standard answers) — feeds the RAG store.
- `style_guide.md` — your tone, greeting, sign-off, length preferences.
- `sent_examples.md` — a few real emails you've written, so the agent learns your actual voice.

**5. Build the fact database**
```bash
python knowledge.py
```
Re-run this any time you update `about_me.md`.

## Running it

| Command | What happens |
|---|---|
| `python run.py` | Safe dry run over the **mock** inbox — no real Gmail involved. |
| `python agent.py` | Same mock inbox, but the LLM decides draft-vs-skip itself. |
| `python real_run.py` | One-time pass over your **real** unread Gmail. Opens a browser to log in the first time. Creates drafts you can review in Gmail. |
| `python schedular.py` | Runs forever, checking your inbox every 5 minutes and drafting replies for anything new. |

Every real-mail path only ever **creates drafts** — you always approve and send manually from Gmail.

## Security notes

- Gmail OAuth scopes are limited to `gmail.readonly` and `gmail.compose` — send access is never requested.
- `credentials.json`, `token.json`, `seen.json`, and the local `my_db/` vector store are all git-ignored; they contain your OAuth secrets and local run state and should never be pushed.
- `my_data/` (your facts, style, and sent examples) **is** version-controlled here since it's part of the demo — remove or replace it with your own before relying on this for a real inbox, and double-check it for anything you don't want public before committing.

## How this was built

This project was built incrementally, one concept at a time:

1. **llm.py** — a single shared connection to the model.
2. **inbox.py** — a fake inbox to develop safely against.
3. **tools.py** — the agent's first tool, `classify()`.
4. **run.py** — a fixed pipeline (classify → summarize → draft) to prove the tools worked.
5. **knowledge.py + style.py** — turned "personalization" into two concrete pieces: searchable facts (RAG via ChromaDB) and always-on tone/voice.
6. **agent.py** — the actual agentic leap: instead of Python code deciding "classify then maybe draft," `decide_action()` lets the LLM choose the action itself.
7. **gmail.py + real_run.py** — swapped the mock inbox for real Gmail, restricted to read + draft-creation permissions.
8. **memory.py + schedular.py** — added persistence (don't redraft the same email) and a polling loop, turning a one-off script into an always-on agent.

### Possible next steps
- Wrap it in a small API (e.g. FastAPI) so it can be triggered on demand instead of only via polling or CLI.
- Containerize it (Docker) for easier deployment.
- Add a lightweight UI for reviewing/approving drafts outside of Gmail itself.
