# FAILURES.md

## Known limitations

### 1. Tiny sample corpus

This starter has only 8 papers. It proves the mechanics, not production retrieval quality.

### 2. No hybrid lexical retrieval yet

Exact paper IDs and rough titles can be better served by lexical search. The starter currently uses vector retrieval only.

### 3. No reranker

The first-stage vector search is passed directly to the LLM. A reranker should be evaluated later.

### 4. No full-text pipeline

The starter embeds title + abstract only. Full text can be added for a subset as allowed by the assessment.

### 5. Version handling is metadata-only

Version fields are stored but not yet used to implement a complete current-version policy.

### 6. Multi-hop questions are not fully implemented

A question such as "Has anyone reproduced this?" may require multiple searches and synthesis. The starter demonstrates the concept only through the architecture/documentation.

### 7. Evaluation is small

The manual evaluation set is intentionally tiny. A serious held-out set should be created before making quality claims.

## One thing that can make the system worse

A larger retrieval `top_k` is not automatically better. The sample deliberately includes evidence that one study found larger retrieval sets could hurt because of distractors, while another found benefits on its benchmark.

This is a useful demonstration that "retrieve more documents" is a hypothesis to measure, not a guaranteed improvement.

## Failure-handling policy

When evidence is insufficient:

```text
INSUFFICIENT EVIDENCE
```

When evidence conflicts:

```text
CONFLICTING EVIDENCE
```

The assistant should explain the limitation rather than produce confident unsupported claims.
