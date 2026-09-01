# EVAL.md

## What this starter measures

The assessment asks for the trajectory: baseline, each change, before/after, including changes that made the system worse.

Do not claim production-scale performance from this tiny sample.

## Baseline

Baseline A is the first working retrieval pipeline:

```text
title + abstract
    -> one embedding model
    -> cosine vector retrieval
    -> one local LLM
```

Record:
- top-k retrieval results;
- whether expected evidence appears;
- whether the answer is supported;
- whether unsupported questions are rejected;
- whether conflicting evidence is surfaced.

## Manual evaluation set

| Query | Expected behavior |
|---|---|
| What benefit does retrieval augmented generation provide according to the papers? | Answer with evidence from 2401.00001 |
| What is the relationship between vector retrieval and language models? | Use 2401.00002 |
| Which paper discusses version-aware scientific literature? | Identify 2401.00003 |
| Do the papers agree about whether larger retrieval sets always improve answer quality? | Surface disagreement between 2401.00004 and 2401.00005 |
| What was the exact GDP of India in 2024 according to these papers? | Abstain: evidence is insufficient |
| Find the paper with ID 2401.00001 | Identifier/paper lookup |

## Results table

Fill this in during your experiments.

| Version | Change | Recall@K | MRR | Answer correct | Citation correct | Abstention correct | Notes |
|---|---|---:|---:|---:|---:|---:|---|
| A | Initial vector retrieval | TODO | TODO | TODO | TODO | TODO | Baseline |
| B | Add lexical/BM25 retrieval | TODO | TODO | TODO | TODO | TODO | Measure |
| C | Add reranker | TODO | TODO | TODO | TODO | TODO | Measure |
| D | Add version-aware filtering | TODO | TODO | TODO | TODO | TODO | Measure |

## Negative tests

A negative test is successful when the system does not manufacture an answer.

For the GDP query, record:
- query;
- retrieved papers;
- model response;
- whether the response clearly says evidence is insufficient.

## Conflict test

For the retrieval-set-size query, record whether both 2401.00004 and 2401.00005 are surfaced and whether the answer explicitly states that the papers disagree.

## Scaling experiment

When moving toward the real corpus, measure:

```text
10
100
1,000
10,000
100,000
2,700,000
```

At each point measure ingestion time, embedding throughput, storage size, query latency and retrieval quality.

Do not invent these numbers before running the experiment.
