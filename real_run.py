"""
real_run.py — One-time test: read real unread mail, draft replies,
leave them in your Gmail Drafts folder for you to review.
"""
from gmail import get_service, get_unread, create_draft
from tools import decide_action, draft_reply

service = get_service()          # opens browser to log in the first time
emails = get_unread(service, max_results=50)

print(f"Found {len(emails)} unread emails.\n")

for email in emails:
    print("=" * 60)
    print(f"From:    {email['from']}")
    print(f"Subject: {email['subject']}")

    decision = decide_action(email)
    print(f"Agent decided: {decision.get('action')}  ({decision.get('reason')})")

    if decision.get("action") == "draft":
        reply = draft_reply(email)
        draft_id = create_draft(service, email, reply)
        print(f"✓ Draft created in your Gmail (id: {draft_id[:10]}...). Review before sending.")
    else:
        print("Skipped.")
    print()