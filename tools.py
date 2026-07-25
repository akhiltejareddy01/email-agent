"""
tools.py — The agent's tools. Each tool is just a Python function.

Right now we have one: classify(). We'll add summarize() and
draft_reply() in the next steps.
"""
from llm import ask

# The buckets the agent can sort emails into.
CATEGORIES = ["urgent", "question", "meeting", "newsletter", "spam"]


def classify(email):
    """Use the LLM to decide which category an email belongs to."""
    prompt = f"""Classify this email into exactly ONE of these categories:
{", ".join(CATEGORIES)}

Email:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Reply with only the single category word, nothing else."""

    result = ask(prompt).lower()

    # The model might add extra words; keep only a known category.
    for c in CATEGORIES:
        if c in result:
            return c
    return "unknown"

def summarize(email):
    """One-line summary of what the email is about."""
    prompt = f"""Summarize this email in ONE short sentence.

From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Summary:"""
    return ask(prompt)


from knowledge import retrieve_facts
from style import load_style

# Set these once to your real identity.
MY_NAME = "Akhil"
MY_EMAIL = "yvakhilteja1104@gmail.com"


def draft_reply(email):
    """Write a reply AS you, TO the sender, in your voice."""
    query = f"{email['subject']} {email['body']}"
    facts = retrieve_facts(query, k=3)
    facts_block = "\n".join(facts) if facts else "(none)"
    style_block = load_style()

    prompt = f"""You are {MY_NAME}. You are writing an email reply FROM yourself
TO the person who sent the email below.

IMPORTANT RULES:
- You ARE {MY_NAME} ({MY_EMAIL}). Do NOT greet {MY_NAME}. Greet the SENDER.
- Reply to what the sender actually asked. Stay on their topic.
- The facts below are background about you. Use them ONLY if the sender's
  email actually calls for them. Do NOT volunteer unrelated facts
  (e.g. do not offer your resume unless they asked about a job).
- Do not invent facts, actions, or commitments you have not made.
- If you lack information to answer, keep it short and ask a clarifying question.

Background facts about you (use only if relevant):
{facts_block}

Write in this style:
{style_block}

The email you are replying to:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Write ONLY the reply body, addressed to the sender, in your voice."""

    return ask(prompt)

import json

def decide_action(email):
    """Ask the LLM what to do with this email. Returns a dict."""
    prompt = f"""You are an email assistant. Decide what to do with this email.

Choose ONE action:
- "draft"  : it needs a personal reply, so draft one
- "skip"   : no reply needed (newsletter, spam, notifications)

Also give a one-sentence reason.

Email:
From: {email['from']}
Subject: {email['subject']}
Body: {email['body']}

Respond ONLY with JSON, nothing else, in this exact format:
{{"action": "draft" or "skip", "reason": "..."}}"""

    raw = ask(prompt)

    # The model sometimes wraps JSON in ```; strip that, then parse.
    cleaned = raw.replace("```json", "").replace("```", "").strip()
    try:
        return json.loads(cleaned)
    except Exception:
        # If parsing fails, fall back to a safe default.
        return {"action": "skip", "reason": "could not parse decision"}