# DECISIONS.md

## Goal

Build the smallest useful local retrieval-augmented research assistant that can be defended live.

## Decision 1 — Local Ollama

**Chosen:** Ollama for both the embedding model and chat model.

**Why:** The assessment says legal will not allow research queries to leave the client's infrastructure. A local model keeps inference on the user's machine/server.

**Rejected for the starter:** Hosted LLM APIs.

## Decision 2 — One LLM

**Chosen:** One local chat model (`llama3.2:3b` by default).

**Why:** The assessment values measured decisions. Multiple LLMs add complexity before we know whether retrieval works.

## Decision 3 — Separate embedding model

**Chosen:** `nomic-embed-text`.

**Why:** Embeddings solve semantic retrieval; the chat LLM should not be expected to search 2.7M records by itself.

## Decision 4 — Qdrant local mode

**Chosen:** Qdrant local persistent storage.

**Why:** It gives a real vector database abstraction without requiring a separate Docker service for the starter.

**Rejected for the starter:** A distributed vector cluster.

## Decision 5 — Title + abstract first

**Chosen:** Embed title + abstract.

**Why:** Those fields are explicitly supplied in the assessment corpus. Full text is optional for a subset.

## Decision 6 — Evidence-grounded generation

**Chosen:** Send retrieved evidence to the LLM and explicitly instruct it to abstain when evidence is insufficient and surface conflicts.

**Why:** The client specifically warns about confident nonsense and papers that disagree.

## Decision 7 — Small corpus before 2.7M

**Chosen:** Start with 8 records.

**Why:** Faster iteration and easier debugging. Scale only after retrieval and answer behavior are measured.

## Untested assumptions

- The exact hardware available for the final 2.7M-record run is unknown.
- Embedding throughput for the full corpus has not been measured here.
- The best embedding model for the held-out questions has not been established.
- A production-grade version strategy has not been tested against the full arXiv dataset.
