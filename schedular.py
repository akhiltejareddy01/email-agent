"""
scheduler.py — The always-on agent.

Every few minutes: read unread mail, skip anything already handled,
draft replies for the rest, remember what it did, then wait and repeat.
Creates drafts only — never sends.
"""
import time

from gmail import get_service, get_unread, create_draft
from tools import decide_action, draft_reply
from memory import load_seen, mark_seen

# How often to check the inbox, in seconds. 300 = every 5 minutes.
CHECK_EVERY = 300


def check_inbox(service):
    seen = load_seen()
    emails = get_unread(service, max_results=10)

    # Keep only emails we haven't handled before.
    new_emails = [e for e in emails if e["id"] not in seen]

    if not new_emails:
        print("No new emails to handle.")
        return

    print(f"Found {len(new_emails)} new email(s).")

    for email in new_emails:
        print(f"  - {email['subject']}")
        decision = decide_action(email)

        if decision.get("action") == "draft":
            reply = draft_reply(email)
            create_draft(service, email, reply)
            print(f"    -> draft created ({decision.get('reason')})")
        else:
            print(f"    -> skipped ({decision.get('reason')})")

        # Remember it either way, so we don't reconsider it next cycle.
        mark_seen(email["id"])


def run_forever():
    service = get_service()  # logs in once using saved token
    print("Email agent started. Watching your inbox...")

    while True:
        try:
            check_inbox(service)
        except Exception as e:
            # Never let one bad cycle kill the agent; log and keep going.
            print(f"Error this cycle (will retry): {e}")

        print(f"Sleeping {CHECK_EVERY}s...\n")
        time.sleep(CHECK_EVERY)


if __name__ == "__main__":
    run_forever()