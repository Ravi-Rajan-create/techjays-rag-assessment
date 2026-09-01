from common import OLLAMA_URL, EMBED_MODEL, CHAT_MODEL
import requests

def main():
    r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=10)
    r.raise_for_status()
    names = {m["name"] for m in r.json().get("models", [])}

    # Ollama may report a model with the :latest tag.
    normalized_names = {name.split(":")[0] for name in names}
    print("Ollama: OK")
    print(
    "Required embedding model:",
    EMBED_MODEL,
    "->",
    "FOUND" if EMBED_MODEL in names or EMBED_MODEL in normalized_names else "MISSING"
)

    print(
        "Required chat model:",
        CHAT_MODEL,
        "->",
        "FOUND" if CHAT_MODEL in names or CHAT_MODEL in normalized_names else "MISSING"
    )

    if not (EMBED_MODEL in names or EMBED_MODEL in normalized_names) or not (
        CHAT_MODEL in names or CHAT_MODEL in normalized_names
    ):
        print("\nRun:")
        print(f"  ollama pull {EMBED_MODEL}")
        print(f"  ollama pull {CHAT_MODEL}")
        raise SystemExit(1)

if __name__ == "__main__":
    main()
