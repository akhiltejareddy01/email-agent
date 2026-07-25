"""
gmail.py — Talks to your real Gmail using the official API.

Permission requested: read messages + create drafts. NOT send.
First run opens a browser to log in; after that it remembers you
via a saved token.json file.
"""
import os
import base64
from email.mime.text import MIMEText

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

# These scopes are deliberately limited: read, and create drafts. No send.
SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly",
    "https://www.googleapis.com/auth/gmail.compose",
]


def get_service():
    """Log in (once) and return a Gmail API client."""
    creds = None
    # token.json stores your login so you don't sign in every time.
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    # If there's no valid login, do the browser sign-in flow.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)
        # Save the login for next time.
        with open("token.json", "w") as f:
            f.write(creds.to_json())

    return build("gmail", "v1", credentials=creds)


def _extract_body(payload):
    """Dig the plain-text body out of Gmail's nested message structure."""
    # Simple case: body is right here.
    if payload.get("body", {}).get("data"):
        data = payload["body"]["data"]
        return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")

    # Multipart case: search the parts for the plain-text version.
    for part in payload.get("parts", []):
        if part.get("mimeType") == "text/plain" and part.get("body", {}).get("data"):
            data = part["body"]["data"]
            return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
        # Nested parts (emails can be deeply nested) — recurse.
        nested = _extract_body(part)
        if nested:
            return nested

    return ""  # nothing found


def get_unread(service, max_results=5):
    """Fetch unread emails with their FULL body text."""
    results = service.users().messages().list(
        userId="me", q="is:unread", maxResults=max_results
    ).execute()
    messages = results.get("messages", [])

    emails = []
    for m in messages:
        full = service.users().messages().get(
            userId="me", id=m["id"], format="full"
        ).execute()

        headers = full["payload"]["headers"]
        subject = next((h["value"] for h in headers if h["name"] == "Subject"), "")
        sender = next((h["value"] for h in headers if h["name"] == "From"), "")

        body = _extract_body(full["payload"]).strip()
        if not body:
            body = full.get("snippet", "")  # fallback if extraction fails

        emails.append({
            "id": m["id"],
            "thread_id": full["threadId"],
            "from": sender,
            "subject": subject,
            "body": body[:2000],  # cap length so prompts stay reasonable
        })
    return emails

def create_draft(service, email, reply_text):
    """Create a Gmail DRAFT reply (does NOT send)."""
    message = MIMEText(reply_text)
    message["to"] = email["from"]
    message["subject"] = "Re: " + email["subject"]

    raw = base64.urlsafe_b64encode(message.as_bytes()).decode()

    draft = service.users().drafts().create(
        userId="me",
        body={"message": {"raw": raw, "threadId": email.get("thread_id")}},
    ).execute()
    return draft["id"]