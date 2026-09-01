from pathlib import Path
import json
import os
import requests
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

ROOT = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT / "data" / "sample_papers.jsonl"
QDRANT_PATH = ROOT / "qdrant_storage"
COLLECTION = "papers"

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
EMBED_MODEL = os.getenv("EMBED_MODEL", "nomic-embed-text:latest")
CHAT_MODEL = os.getenv("CHAT_MODEL", "llama3.2:3b")

def embed(text: str):
    r = requests.post(
        f"{OLLAMA_URL}/api/embed",
        json={"model": EMBED_MODEL, "input": text},
        timeout=120,
    )
    r.raise_for_status()
    data = r.json()
    return data["embeddings"][0]

def ollama_chat(prompt: str):
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={
            "model": CHAT_MODEL,
            "messages":[{"role":"user","content":prompt}],
            "stream": False,
            "options":{"temperature":0}
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]

def get_client():
    return QdrantClient(path=str(QDRANT_PATH))
