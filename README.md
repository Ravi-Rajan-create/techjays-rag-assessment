# Techjays Senior AI Engineer Assessment — Simple Local RAG Starter

This is a deliberately small, end-to-end starter implementation for the uploaded Techjays Senior AI Engineer Practical Assessment.

The assessment asks for a working private system over an arXiv corpus (~2.7M JSONL records), a recording showing success and failure and `DECISIONS.md`, `EVAL.md` and `FAILURES.md`. This starter uses only a tiny sample corpus so you can understand and demo the architecture first.

## Architecture

```text
sample JSONL
    |
    v
ingest.py
    |
    v
Ollama embedding model
    |
    v
Qdrant local vector store
    |
    v
retrieve.py  <--- user question
    |
    v
Ollama LLM
    |
    v
answer + evidence
```

For the real 2.7M-record corpus, the same pipeline can be scaled by batching ingestion and replacing the sample file with the real JSONL.

## 1. Prerequisites

- Python 3.10+
- Ollama installed and running locally
- Internet is needed only to download Ollama/model packages initially. Queries and documents remain local once models are installed.

Install Ollama from the official site:
https://ollama.com/

## 2. Create a virtual environment

### Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

### Windows CMD

```cmd
python -m venv .venv
.venv\Scripts\activate.bat
```

### macOS/Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
```

## 3. Install Python dependencies

```bash
pip install -r requirements.txt
```
## Download ollama for windows
# https://ollama.com/download/windows

## 4. Download local Ollama models

This project defaults to:

```bash
ollama pull nomic-embed-text
ollama pull llama3.2:3b
```

You can substitute another local chat model later. Keep one embedding model for a clean evaluation.

Check:

```bash
ollama list
```

## 5. Verify Ollama

```bash
python src/check_ollama.py
```

Expected result is a successful connection and confirmation that the required models exist.

## 6. Create embeddings and build the vector store

```bash
python src/ingest.py
```

This reads `data/sample_papers.jsonl`, creates one embedding per paper and stores vectors plus metadata in local Qdrant storage under `qdrant_storage/`.

Run it again after changing the sample corpus.

## 7. Ask a question

```bash
python src/query.py "What does the sample corpus say about retrieval augmented generation?"
```

The program:

1. embeds the question locally;
2. retrieves the most similar papers;
3. sends only retrieved evidence to the local Ollama LLM;
4. asks the LLM to answer only from the evidence;
5. prints source IDs/titles and a confidence-style status.

## 8. Try the demo queries

### Positive: answerable

```bash
python src/query.py "What benefit does retrieval augmented generation provide according to the papers?"
```

```bash
python src/query.py "What is the relationship between vector retrieval and language models in the sample corpus?"
```

```bash
python src/query.py "Which paper discusses version-aware scientific literature?"
```

### Negative: unsupported

```bash
python src/query.py "What was the exact GDP of India in 2024 according to these papers?"
```

The expected behavior is that the system should say the evidence is insufficient rather than inventing an answer.

### Negative: conflicting evidence

```bash
python src/query.py "Do the sample papers agree about whether larger retrieval sets always improve answer quality?"
```

The sample corpus deliberately contains two documents with different claims. The expected behavior is to surface the disagreement instead of silently selecting one.

### Paper lookup

```bash
python src/query.py "Find the paper with ID 2401.00005"
```

This demonstrates the assessment's requirement for researchers who know a paper number or rough title rather than a topic.

## 9. Run automated tests

First make sure ingestion has completed:

```bash
python src/ingest.py
```

Then:

```bash
pytest -q
```

The tests cover:
- answerable query returns evidence;
- unsupported query triggers an uncertainty response;
- conflicting evidence is surfaced.

## 10. Important limitations

This is a starter, not a finished production system.

It does NOT yet fully solve:
- 2.7M-record ingestion performance;
- robust current-version resolution across all arXiv versions;
- full-text extraction;
- sophisticated multi-hop research questions;
- production authentication;
- distributed vector storage;
- comprehensive benchmark datasets;
- expert-grade claim verification.

Those limitations are intentional and should be discussed honestly in `FAILURES.md`.

## 11. Suggested next improvements

1. Add BM25/hybrid lexical search for paper IDs and exact titles.
2. Add a reranker after vector retrieval.
3. Add explicit version normalization.
4. Add full-text chunks for a selected subset.
5. Create a held-out evaluation set.
6. Measure Recall@K, MRR, answer correctness, citation correctness and abstention behavior.
7. Compare one embedding model against another and record before/after results.
8. Add multi-hop retrieval for questions such as "Has anyone reproduced this?"