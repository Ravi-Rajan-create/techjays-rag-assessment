import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from common import COLLECTION, embed, get_client

def test_collection_has_documents():
    client = get_client()
    info = client.get_collection(COLLECTION)
    assert info.points_count >= 8

def test_retrieval_returns_evidence():
    client = get_client()
    hits = client.query_points(
        collection_name=COLLECTION,
        query=embed("retrieval augmented generation evidence"),
        limit=3,
        with_payload=True,
    ).points
    ids = {h.payload["id"] for h in hits}
    assert ids & {"2401.00001", "2401.00002"}

def test_conflict_sources_can_be_retrieved():
    client = get_client()
    hits = client.query_points(
        collection_name=COLLECTION,
        query=embed("larger retrieval sets always improve answer quality"),
        limit=8,
        with_payload=True,
    ).points
    ids = {h.payload["id"] for h in hits}
    assert "2401.00004" in ids
    assert "2401.00005" in ids
