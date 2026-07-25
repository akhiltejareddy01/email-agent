from inbox import INBOX
from tools import classify, summarize, draft_reply

# Categories that actually deserve a reply (skip newsletters and spam).
REPLY_TO = ["urgent", "question", "meeting"]

for email in INBOX:
    category = classify(email)

    print("=" * 60)
    print(f"From:     {email['from']}")
    print(f"Subject:  {email['subject']}")
    print(f"Category: {category}")
    print(f"Summary:  {summarize(email)}")

    # Only draft a reply for emails that need one.
    if category in REPLY_TO:
        print("\n--- DRAFT REPLY (for your approval) ---")
        print(draft_reply(email))
    else:
        print("\n(No reply needed.)")
    print()