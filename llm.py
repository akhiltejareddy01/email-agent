"""
llm.py — One shared connection to the LLM (now via the OpenAI API).

The rest of the project doesn't change: everyone still just calls ask().
The API key is read from the OPENAI_API_KEY environment variable — never
hardcode it in the file.
"""
import os
from openai import OpenAI

LLM_MODEL = os.getenv("LLM_MODEL", "gpt-5-mini")

client = OpenAI()  # automatically reads OPENAI_API_KEY from the environment


def ask(prompt, system=None):
    """Send a prompt to the LLM and return its text reply."""
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    response = client.chat.completions.create(
        model=LLM_MODEL,
        messages=messages,
    )
    return response.choices[0].message.content.strip()