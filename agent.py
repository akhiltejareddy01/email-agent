"""
agent.py — The agent loop.

For each email, the LLM DECIDES what to do, then we carry it out.
The decision lives in the model now, not in our if-statements.
"""
from inbox import INBOX
from tools import decide_action, summarize, draft_reply


def process_email(email):
    print("=" * 60)
    print(f"From:    {email['from']}")
    print(f"Subject: {email['subject']}")

    # STEP 1: the agent decides
    decision = decide_action(email)
    action = decision.get("action")
    reason = decision.get("reason", "")

    print(f"Agent decided: {action}  ({reason})")

    # STEP 2: we carry out whatever it chose
    if action == "draft":
        print(f"Summary: {summarize(email)}")
        print("\n--- DRAFT REPLY (for your approval) ---")
        print(draft_reply(email))
    else:
        print("(Skipped — no reply needed.)")
    print()


def run():
    for email in INBOX:
        process_email(email)


if __name__ == "__main__":
    run()