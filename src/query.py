import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))

from qdrant_client.models import Filter, FieldCondition, MatchValue

from common import COLLECTION, embed, get_client, ollama_chat


DEFAULT_LIMIT = 5

ARXIV_ID_PATTERN = re.compile(
    r"\b(\d{4}\.\d{4,5}(?:v\d+)?)\b",
    re.IGNORECASE,
)

DOI_PATTERN = re.compile(
    r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b",
    re.IGNORECASE,
)


def extract_arxiv_id(question):
    match = ARXIV_ID_PATTERN.search(question)

    if match:
        return match.group(1)

    return None


def extract_doi(question):
    match = DOI_PATTERN.search(question)

    if match:
        return match.group(0).rstrip(".,;)")

    return None


def exact_lookup(field_name, value):
    """
    Exact metadata lookup in Qdrant.

    This is used for paper IDs and DOIs instead of semantic
    vector similarity.
    """

    client = get_client()

    qdrant_filter = Filter(
        must=[
            FieldCondition(
                key=field_name,
                match=MatchValue(value=value),
            )
        ]
    )

    try:
        result = client.scroll(
            collection_name=COLLECTION,
            scroll_filter=qdrant_filter,
            limit=1,
            with_payload=True,
            with_vectors=False,
        )

        points = result[0]

        return points

    except Exception as exc:
        print(f"Exact {field_name} lookup failed: {exc}")
        return []


def vector_retrieve(question, limit=DEFAULT_LIMIT):
    """
    Semantic retrieval using:

        question
            ↓
        Ollama embedding
            ↓
        Qdrant vector search
    """

    client = get_client()

    vector = embed(question)

    try:
        result = client.query_points(
            collection_name=COLLECTION,
            query=vector,
            limit=limit,
            with_payload=True,
        )

        return result.points

    except Exception as exc:
        print(f"Vector search failed: {exc}")
        return []


def retrieve(question, limit=DEFAULT_LIMIT):

    # ------------------------------------------------------------
    # 1. Exact arXiv ID lookup
    # ------------------------------------------------------------

    arxiv_id = extract_arxiv_id(question)

    if arxiv_id:

        print(f"\nDetected arXiv ID: {arxiv_id}")

        hits = exact_lookup(
            field_name="id",
            value=arxiv_id,
        )

        if hits:
            return hits, "EXACT_ARXIV_ID"

        print(
            f"No exact paper found for arXiv ID {arxiv_id}."
        )

        # Do not silently pretend semantic search found the paper.
        # We can still fall back for robustness.
        print("Falling back to semantic search...\n")

    # ------------------------------------------------------------
    # 2. Exact DOI lookup
    # ------------------------------------------------------------

    doi = extract_doi(question)

    if doi:

        print(f"\nDetected DOI: {doi}")

        hits = exact_lookup(
            field_name="doi",
            value=doi,
        )

        if hits:
            return hits, "EXACT_DOI"

        print(
            f"No exact paper found for DOI {doi}."
        )

        print("Falling back to semantic search...\n")

    # ------------------------------------------------------------
    # 3. Normal semantic/vector search
    # ------------------------------------------------------------

    hits = vector_retrieve(
        question,
        limit=limit,
    )

    return hits, "VECTOR"


def build_evidence(hits):

    blocks = []

    for index, hit in enumerate(hits, start=1):

        payload = hit.payload or {}

        paper_id = payload.get("id", "UNKNOWN")
        title = payload.get(
            "title",
            "UNKNOWN TITLE",
        )
        abstract = payload.get(
            "abstract",
            "NO ABSTRACT",
        )

        blocks.append(
            f"""SOURCE {index}
Paper ID: {paper_id}
Title: {title}
Abstract:
{abstract}"""
        )

    return "\n\n".join(blocks)


def build_prompt(
    question,
    evidence,
    retrieval_mode,
):

    return f"""
You are a cautious scientific literature research assistant.

Answer the user's question using ONLY the evidence provided below.

Retrieval mode:
{retrieval_mode}

IMPORTANT RULES:

1. Do not invent facts, papers, authors, results, dates, or numbers.

2. Every factual claim must be supported by the supplied evidence.

3. If the evidence directly answers the question, answer clearly.

4. If two or more papers make materially different or opposing
   claims, classify this as:

   CONFLICTING EVIDENCE

   This is NOT the same as insufficient evidence.

5. When there is conflicting evidence:
   - identify the relevant papers;
   - explain what each paper says;
   - explain how their claims differ;
   - give a careful conclusion.

6. Use:

   INSUFFICIENT EVIDENCE

   only when the supplied evidence does not contain enough
   information to answer the question.

7. Do not convert disagreement between papers into
   INSUFFICIENT EVIDENCE.

8. For paper identification questions, provide the paper ID and
   title when available.

9. Cite paper IDs using square brackets, for example:

   [2401.00006]

10. Do not claim that a paper says something unless it appears
    in its supplied title or abstract.

USER QUESTION:
{question}

EVIDENCE:
{evidence}

Now provide the answer.
""".strip()


def print_evidence(
    hits,
    retrieval_mode,
):

    print("\nEVIDENCE")
    print("========")

    print(
        f"Retrieval mode: {retrieval_mode}"
    )

    print()

    for hit in hits:

        payload = hit.payload or {}

        paper_id = payload.get(
            "id",
            "UNKNOWN",
        )

        title = payload.get(
            "title",
            "UNKNOWN TITLE",
        )

        score = getattr(
            hit,
            "score",
            None,
        )

        if score is not None:

            print(
                f"- {paper_id} | "
                f"{title} | "
                f"score={score:.4f}"
            )

        else:

            print(
                f"- {paper_id} | "
                f"{title}"
            )


def main():

    if len(sys.argv) < 2:

        print(
            'Usage:\n'
            '  python src/query.py "your question"\n\n'
            'Examples:\n'
            '  python src/query.py '
            '"What is retrieval augmented generation?"\n'
            '  python src/query.py '
            '"Find paper 2401.00001"\n'
        )

        raise SystemExit(2)

    question = " ".join(
        sys.argv[1:]
    ).strip()

    if not question:

        print(
            "Question cannot be empty."
        )

        raise SystemExit(2)

    # ------------------------------------------------------------
    # Retrieval
    # ------------------------------------------------------------

    try:

        hits, retrieval_mode = retrieve(
            question
        )

    except Exception as exc:

        print("\nERROR")
        print("=====")
        print(
            f"Unable to perform retrieval: {exc}"
        )

        print(
            "\nMake sure you have run:\n"
            "  python src/ingest.py"
        )

        raise SystemExit(1)

    # ------------------------------------------------------------
    # No evidence
    # ------------------------------------------------------------

    if not hits:

        print("\nANSWER")
        print("======")

        print(
            "INSUFFICIENT EVIDENCE\n\n"
            "No matching documents were found "
            "in the local corpus."
        )

        print("\nRETRIEVAL")
        print("=========")

        print(
            f"Retrieval mode: {retrieval_mode}"
        )

        return

    # ------------------------------------------------------------
    # Evidence
    # ------------------------------------------------------------

    evidence = build_evidence(
        hits
    )

    # ------------------------------------------------------------
    # LLM
    # ------------------------------------------------------------

    prompt = build_prompt(
        question=question,
        evidence=evidence,
        retrieval_mode=retrieval_mode,
    )

    try:

        answer = ollama_chat(
            prompt
        )

    except Exception as exc:

        print("\nERROR")
        print("=====")

        print(
            f"Ollama generation failed: {exc}"
        )

        print(
            "\nCheck that Ollama is running "
            "and llama3.2:3b is installed."
        )

        raise SystemExit(1)

    # ------------------------------------------------------------
    # Output
    # ------------------------------------------------------------

    print("\nANSWER")
    print("======")

    print(answer)

    print_evidence(
        hits=hits,
        retrieval_mode=retrieval_mode,
    )


if __name__ == "__main__":
    main()