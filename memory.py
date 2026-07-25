"""
memory.py — Remembers which emails the agent already handled,
so it never drafts the same one twice.

We just store handled email IDs in a small JSON file on disk.
"""
import json
import os

SEEN_FILE = os.getenv("SEEN_FILE", "./seen.json")


def load_seen():
    """Return the set of email IDs we've already processed."""
    if os.path.exists(SEEN_FILE):
        with open(SEEN_FILE, "r") as f:
            return set(json.load(f))
    return set()


def mark_seen(email_id):
    """Record that we've handled this email."""
    seen = load_seen()
    seen.add(email_id)
    with open(SEEN_FILE, "w") as f:
        json.dump(list(seen), f)