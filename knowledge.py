"""
knowledge.py — Your personal FACTS, stored in a vector database.

This is the RAG part: about_me.md is chunked and stored, then we can
retrieve only the facts relevant to a given email.
"""
import os
import chromadb

DB_PATH = os.getenv("DB_PATH", "./my_db")
ABOUT_PATH = os.getenv("ABOUT_PATH", "./my_data/about_me.md")
COLLECTION_NAME = "about_me"

client = chromadb.PersistentClient(path=DB_PATH)


def chunk_text(text, size=400, overlap=80):
    """Cut the text into overlapping chunks."""
    chunks = []
    start = 0
    while start < len(text):
        chunks.append(text[start:start + size])
        start += size - overlap
    return [c.strip() for c in chunks if c.strip()]


def ingest():
    """Read about_me.md, chunk it, and store it in the vector DB."""
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(name=COLLECTION_NAME)

    with open(ABOUT_PATH, "r", encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_text(text)
    collection.add(
        documents=chunks,
        ids=[f"fact-{i}" for i in range(len(chunks))],
    )
    print(f"Stored {len(chunks)} chunks about you.")


def retrieve_facts(query, k=3):
    """Return the facts about you most relevant to this query."""
    collection = client.get_or_create_collection(name=COLLECTION_NAME)
    if collection.count() == 0:
        return []
    results = collection.query(query_texts=[query], n_results=k)
    return results["documents"][0]


# Run this file directly to (re)build the DB:  python knowledge.py
if __name__ == "__main__":
    ingest()