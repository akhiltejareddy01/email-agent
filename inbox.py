"""
inbox.py — A pretend inbox (just data, no real email account).

Each email is a simple dictionary. Later we can swap this for a real
inbox and the rest of the code won't need to change.
"""
INBOX = [
    {
        "id": 1,
        "from": "boss@company.com",
        "subject": "Q3 report needed today",
        "body": "Can you send me the Q3 sales report before 3pm? It's urgent for the board meeting.",
    },
    {
        "id": 2,
        "from": "friend@gmail.com",
        "subject": "Lunch next week?",
        "body": "Hey! Are you free for lunch sometime next week? Would love to catch up.",
    },
    {
        "id": 3,
        "from": "news@techweekly.com",
        "subject": "This week in tech: 10 stories you missed",
        "body": "Your weekly digest of the biggest tech headlines. Read on for more.",
    },
    {
        "id": 4,
        "from": "no-reply@shop-deals.com",
        "subject": "YOU WON a $1000 gift card!!!",
        "body": "Click here now to claim your prize before it expires! Limited time offer!!!",
    },
    {
        "id": 5,
        "from": "client@bigcorp.com",
        "subject": "Question about the invoice",
        "body": "Hi, I noticed the latest invoice was for $500 but our agreement said $450. Can you clarify?",
    },
]
