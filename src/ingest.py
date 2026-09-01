import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

from common import DATA_FILE, COLLECTION, embed, get_client
from qdrant_client.models import Distance, VectorParams, PointStruct

def main():
    client = get_client()
    papers = []
    with DATA_FILE.open(encoding="utf-8") as f:
        for line in f:
            if line.strip():
                papers.append(__import__("json").loads(line))

    first_text = papers[0]["title"] + "\n" + papers[0]["abstract"]
    dim = len(embed(first_text))

    existing = [c.name for c in client.get_collections().collections]
    if COLLECTION in existing:
        client.delete_collection(COLLECTION)

    client.create_collection(
        collection_name=COLLECTION,
        vectors_config=VectorParams(size=dim, distance=Distance.COSINE),
    )

    points = []
    for i, p in enumerate(papers):
        text = p["title"] + "\n" + p["abstract"]
        vector = embed(text)
        payload = {
            "id": p["id"],
            "title": p["title"],
            "abstract": p["abstract"],
            "authors": p.get("authors", []),
            "categories": p.get("categories", []),
            "doi": p.get("doi"),
            "versions": p.get("versions", []),
        }
        points.append(PointStruct(id=i+1, vector=vector, payload=payload))
        print(f"Embedded {i+1}/{len(papers)}: {p['id']}")

    client.upsert(collection_name=COLLECTION, points=points)
    print(f"\nStored {len(points)} papers in local Qdrant collection '{COLLECTION}'.")

if __name__ == "__main__":
    main()
