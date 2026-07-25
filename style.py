"""
style.py — Your writing VOICE (style guide + real sent emails).

Unlike facts, we don't search these — we feed all of them into every
draft so the reply consistently sounds like you.
"""

def load_style():
    """Load your style guide and example emails as one text block."""
    parts = []
    for path in ["./my_data/style_guide.md", "./my_data/sent_examples.md"]:
        try:
            with open(path, "r", encoding="utf-8") as f:
                parts.append(f.read())
        except FileNotFoundError:
            pass
    return "\n\n".join(parts)