# MLflow Implementation Plan

This document defines how FinanceBuddy should adopt MLflow in a pragmatic, production-oriented way.

## Goal

Use MLflow as the primary system for:

- RAG experiment tracking
- evaluation run comparison
- prompt and configuration versioning
- artifact storage for evaluation outputs
- technical traceability of retrieval and generation decisions

We will not use MLflow as a replacement for normal application logging.

## Design Principle

Split observability into two layers.

### 1. Runtime Observability

This answers questions such as:

- Why did a user request fail?
- How long did retrieval take?
- Did generation fallback trigger?
- Which conversation or request produced the issue?

This belongs in:

- structured application logs
- request and conversation identifiers
- latency metrics
- error monitoring

### 2. RAG Experiment Tracking

This answers questions such as:

- Did `top_k=5` beat `top_k=3`?
- Did prompt v4 improve groundedness?
- Did query normalization improve multilingual retrieval?
- Which embedding model or chunking strategy performs best?

This belongs in:

- MLflow experiments
- MLflow runs
- MLflow metrics
- MLflow artifacts
- evaluation datasets and reports

FinanceBuddy should adopt both layers, but in that order.

## Recommended Scope For MLflow

MLflow should be introduced for offline and controlled evaluation before it is wired into live request paths.

### Phase 1

Use MLflow only from dedicated evaluation scripts.

This is the right first milestone because it gives us:

- low implementation risk
- clean comparisons between RAG configurations
- no contamination of the request-time chat flow
- a professional evaluation workflow for portfolio and interview discussions

### Phase 2

Add lightweight MLflow logging for curated backend workflows such as:

- ingestion jobs
- batch retrieval evaluation
- prompt comparison runs

### Phase 3

Optionally add MLflow tracing around selected chat workflows if and only if the app-level logging and request tracing are already stable.

## What A FinanceBuddy MLflow Run Should Record

Every meaningful evaluation run should log enough metadata to explain the result later.

### Required Parameters

- `experiment_name`
- `run_type`
  - `retrieval_eval`
  - `generation_eval`
  - `end_to_end_rag_eval`
  - `ingestion_benchmark`
- `language`
- `evaluation_dataset_name`
- `evaluation_dataset_version`
- `embedding_model`
- `chunk_strategy`
- `chunk_size`
- `chunk_overlap`
- `retriever_top_k`
- `query_normalization_enabled`
- `prompt_version`
- `generation_model`
- `corpus_version`

### Required Metrics

- `retrieval_hit_rate`
- `retrieval_mrr` or another ranking metric
- `groundedness_score`
- `answer_relevance_score`
- `answer_completeness_score`
- `citation_correctness_score`
- `no_evidence_rate`
- `generation_failure_rate`
- `average_latency_ms`
- `average_retrieval_latency_ms`
- `average_generation_latency_ms`

### Useful Extra Metrics

- `token_input_estimate`
- `token_output_estimate`
- `cost_estimate`
- `documents_retrieved_avg`
- `sources_per_answer_avg`

### Required Artifacts

- evaluation dataset manifest
- per-question evaluation results as JSON or CSV
- sample prompts used in the run
- sample answers produced in the run
- aggregate report in Markdown

## Dataset And Corpus Versioning Strategy

Do not overengineer this on day one.

### Start With

- versioned local dataset folders
- stable dataset manifest files in Git
- corpus version derived from content hashes or ingestion batch identifiers
- MLflow artifacts storing the exact evaluation inputs and outputs used by a run

### Example Dataset Layout

```text
backend/
  evals/
    datasets/
      tax_qa_es_v1.json
      tax_qa_mixed_lang_v1.json
    manifests/
      tax_qa_es_v1_manifest.json
      corpus_public_finance_v1.json
    reports/
      .gitkeep
```

### Each Evaluation Dataset Entry Should Contain

- `question_id`
- `question`
- `language`
- `expected_topics`
- `expected_source_titles` or source identifiers when possible
- `expected_answer_points`
- optional difficulty tag

This keeps the project explainable and auditable.

## Proposed Implementation Architecture

Add MLflow as a separate evaluation subsystem, not directly inside `ChatService`.

### New Areas To Add

```text
backend/
  evals/
    datasets/
    manifests/
    reports/
    run_rag_eval.py

backend/src/finance_buddy_backend/
  observability/
    logging.py
    mlflow_tracking.py
    run_context.py
  evaluation/
    rag_evaluator.py
    metrics.py
    report_builder.py
```

### Responsibilities

- `observability/logging.py`
  - configure structured logging for the app
- `observability/mlflow_tracking.py`
  - central MLflow helper functions
  - start runs
  - log params, metrics, and artifacts
- `observability/run_context.py`
  - standard run metadata objects for experiments
- `evaluation/rag_evaluator.py`
  - orchestrate evaluation over a dataset
- `evaluation/metrics.py`
  - compute retrieval and answer quality metrics
- `evaluation/report_builder.py`
  - write human-readable summaries for MLflow artifacts
- `evals/run_rag_eval.py`
  - CLI entrypoint for controlled experiment runs

## Why This Architecture Is Correct

This keeps production request orchestration separate from experimentation logic.

That matters because:

- `ChatService` should stay focused on user-facing application flow
- evaluation code changes more often than core request handling
- MLflow belongs to experimentation and controlled measurement, not core business logic

## Minimal First Implementation

The first implementation should be intentionally small.

### Step 1. Add Dependency And Configuration

Add MLflow to `backend/pyproject.toml` and add config values for:

- `mlflow_tracking_uri`
- `mlflow_experiment_name`
- `mlflow_enabled`

Default behavior should be safe locally.

### Step 2. Create Evaluation Dataset Format

Define one initial evaluation dataset focused on the current strongest domain:

- Spanish tax education
- mixed Spanish-English tax queries

This avoids premature expansion into invoices before the current RAG layer is measurable.

### Step 3. Create A Simple Evaluation Runner

The runner should:

1. load a dataset
2. call retrieval or end-to-end RAG pipeline
3. collect outputs per question
4. compute metrics
5. start an MLflow run
6. log params, metrics, and artifacts

### Step 4. Add Structured Runtime Logging

Before MLflow touches live request flows, the app should emit structured logs for:

- request start and end
- conversation ID
- retrieval count
- retrieval latency
- generation latency
- answer status
- exceptions

### Step 5. Add Curated Comparison Workflows

Run comparisons such as:

- query normalization on vs off
- `top_k=3` vs `top_k=5`
- prompt v1 vs prompt v2

This is where MLflow begins paying off.

## Effective MLflow Usage For This Project

This is the professional workflow you should follow.

### Use Experiments By Decision Area

Create experiments like:

- `financebuddy-retrieval`
- `financebuddy-generation`
- `financebuddy-end-to-end-rag`
- `financebuddy-ingestion-benchmarks`

Do not dump everything into one giant experiment.

### Name Runs By The Question You Are Testing

Use descriptive run names such as:

- `rag_eval_tax_es_top5_prompt_v2`
- `retrieval_eval_mixed_lang_norm_on`
- `generation_eval_grounding_prompt_v3`

If run names are vague, comparison becomes useless.

### Log Inputs As Parameters, Results As Metrics, Evidence As Artifacts

Use this rule consistently:

- configuration choices are params
- numeric outcomes are metrics
- detailed tables and examples are artifacts

That discipline is what makes MLflow valuable.

### Keep The Evaluation Dataset Stable During Comparisons

When comparing prompt or retriever changes:

- keep the evaluation dataset fixed
- change one variable at a time
- record the exact corpus version

Otherwise the run comparison is not trustworthy.

### Promote Baselines Explicitly

For each experiment family, define a baseline run and compare new runs against it.

Examples:

- baseline retrieval config
- baseline prompt template
- baseline corpus version

Without a baseline, you are just generating runs, not learning from them.

## Anti-Patterns To Avoid

- Do not log every local ad hoc test as a serious run.
- Do not put MLflow calls everywhere in service methods.
- Do not compare runs where multiple major variables changed at once.
- Do not track metrics without storing the dataset and config version that produced them.
- Do not use MLflow as a substitute for FastAPI logs.

## Suggested Order Of Execution

### Milestone A

- structured backend logging
- request and conversation correlation IDs
- latency and failure instrumentation

### Milestone B

- MLflow dependency and config
- evaluation dataset format
- offline evaluation runner
- first experiment runs

### Milestone C

- retrieval and prompt comparison workflows
- improved metrics and artifacts
- optional ingestion benchmarking runs

### Milestone D

- optional MLflow tracing for selected live workflows
- optional dashboards for portfolio storytelling

## What Success Looks Like

After the first MLflow milestone, you should be able to answer questions like:

- Which retriever configuration performs best on mixed-language tax questions?
- Did query normalization improve retrieval hit rate?
- Which prompt version improved groundedness without hurting completeness?
- Did latency regress after changing retrieval depth?
- Which corpus version produced the best citation correctness?

If you cannot answer those questions with recorded evidence, the MLflow setup is not doing its job.

## Immediate Next Step

Implement only the foundation needed for Milestones A and B.

That means:

1. add structured logging design
2. add MLflow configuration to backend settings
3. create the first evaluation dataset schema
4. build one offline evaluation runner
5. log one clean baseline run in MLflow

## FinanceBuddy Evaluation Schema

This section defines the first concrete evaluation contract for the project.

The goal is to make every evaluation example explicit enough that:

- retrieval quality can be measured deterministically
- answer quality can be judged with LLM-based scorers
- runs remain comparable across prompt, retriever, and corpus changes

### Evaluation Dataset Families

The first implementation should use two datasets only.

- `tax_qa_es_v1`
  - Spanish tax education questions
- `tax_qa_mixed_lang_v1`
  - mixed Spanish-English tax questions

This is the right boundary because it tests the current strongest domain and directly exercises the new query normalization feature.

### Dataset Record Schema

Each evaluation record should follow this shape.

```json
{
  "question_id": "tax-es-001",
  "question": "Que es el IRPF y quien tiene que pagarlo?",
  "language": "es",
  "difficulty": "basic",
  "expected_topics": ["irpf", "renta", "contribuyente"],
  "expected_source_titles": [
    "Guia_50_preguntas",
    "GuiaFiscalidadAcciones2026"
  ],
  "expected_source_ids": [],
  "expected_answer_points": [
    "IRPF es un impuesto sobre la renta de las personas fisicas",
    "se aplica a determinados contribuyentes o personas con rentas sujetas"
  ],
  "must_refuse_without_evidence": false,
  "notes": "baseline tax definition example"
}
```

### Field Definitions

- `question_id`
  - stable identifier for regression tracking
- `question`
  - raw user query to evaluate
- `language`
  - `es`, `mixed`, or later `en`
- `difficulty`
  - `basic`, `intermediate`, `technical`
- `expected_topics`
  - coarse semantic concepts expected in a good answer
- `expected_source_titles`
  - source titles that should ideally appear in retrieval results
- `expected_source_ids`
  - optional exact source identifiers when your corpus is stable
- `expected_answer_points`
  - short factual points a grounded answer should cover
- `must_refuse_without_evidence`
  - use `true` for examples where the system should explicitly avoid unsupported answers
- `notes`
  - optional human annotation

### Why This Schema Is Strong

It supports both deterministic and judge-based evaluation without forcing fake exact-match labels.

That is important for FinanceBuddy because a good grounded answer can vary in wording while still being correct.

## Scorer Design

FinanceBuddy should use three scorer categories.

### 1. Deterministic Retrieval Scorers

These do not require an LLM judge.

#### Required Retrieval Metrics

- `retrieval_hit_rate`
  - whether at least one expected source appears in top-k
- `retrieval_mrr`
  - reciprocal rank of the first expected source
- `retrieval_source_precision_at_k`
  - fraction of returned sources that are expected
- `retrieval_avg_similarity`
  - average similarity score of returned chunks
- `retrieval_empty_rate`
  - rate of empty retrieval results

#### Input Needed Per Example

- returned chunk list
- returned source titles or IDs
- similarity scores
- expected source titles or IDs from the dataset

### 2. Deterministic Answer Scorers

These are still code-based and should be added early.

#### Required Deterministic Answer Metrics

- `citation_presence_rate`
  - whether sources were attached to the answer
- `citation_correctness_rate`
  - whether attached sources overlap expected sources when available
- `no_evidence_behavior_rate`
  - whether the system refused appropriately on `must_refuse_without_evidence=true` examples
- `answer_non_empty_rate`
  - whether generation returned non-empty text
- `answer_status_generated_rate`
  - percentage of answers with status `generated`
- `generation_failure_rate`
  - percentage of answers with failure fallback
- `latency_ms`
  - total latency per example
- `retrieval_latency_ms`
  - retrieval stage latency
- `generation_latency_ms`
  - generation stage latency

### 3. LLM-as-a-Judge Scorers

These should be used for qualities that are too semantic for strict rules.

#### First Judge Metrics To Add

- `groundedness_score`
  - does the answer stay supported by retrieved context?
- `relevance_to_query_score`
  - does it answer the user question directly?
- `answer_completeness_score`
  - does it cover the expected answer points well enough?

#### Judge Metrics To Add Later

- `explanation_level_alignment_score`
  - does the answer match `basic` vs `technical` depth?
- `citation_explanation_quality_score`
  - are sources used in a way that is actually helpful?
- `safety_or_financial_caution_score`
  - does the answer avoid overclaiming or unsupported financial guidance?

## Judge Strategy For FinanceBuddy

Do not let the judge operate blind.

Each judge should receive:

- the original question
- the generated answer
- the retrieved context
- the expected answer points
- the expected sources when available

That makes the judgment much more useful than generic "is this a good answer?" prompting.

### Example Judge Responsibilities

- `groundedness`
  - fail answers that introduce facts not supported by retrieved chunks
- `relevance`
  - fail answers that drift into unrelated tax concepts
- `completeness`
  - reward answers that cover the major expected points without requiring identical wording

## One MLflow Run: Exact Shape

A single end-to-end RAG run should represent one controlled comparison.

### Example Run Name

`rag_eval_tax_mixed_lang_top5_norm_on_prompt_v1`

### Example Run Params

```json
{
  "run_type": "end_to_end_rag_eval",
  "evaluation_dataset_name": "tax_qa_mixed_lang_v1",
  "evaluation_dataset_version": "v1",
  "language": "mixed",
  "embedding_model": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
  "chunk_strategy": "fixed_window",
  "chunk_size": 800,
  "chunk_overlap": 120,
  "retriever_top_k": 5,
  "query_normalization_enabled": true,
  "prompt_version": "grounded_v1",
  "generation_model": "gemini-3-flash-preview",
  "corpus_version": "public_finance_corpus_2026_04_05",
  "dataset_size": 40
}
```

### Example Run Aggregate Metrics

```json
{
  "retrieval_hit_rate": 0.82,
  "retrieval_mrr": 0.67,
  "citation_correctness_rate": 0.78,
  "groundedness_score": 0.86,
  "relevance_to_query_score": 0.88,
  "answer_completeness_score": 0.74,
  "no_evidence_behavior_rate": 0.95,
  "generation_failure_rate": 0.02,
  "average_latency_ms": 1430,
  "average_retrieval_latency_ms": 320,
  "average_generation_latency_ms": 980
}
```

### Required Run Artifacts

- `dataset.json`
- `dataset_manifest.json`
- `per_example_results.json`
- `aggregate_metrics.json`
- `sample_failures.md`
- `judge_prompts.md`
- `run_config.json`

## Per-Example Result Schema

Every example in a run should emit a detailed record.

```json
{
  "question_id": "tax-mixed-003",
  "question": "What is IRPF tax in Spain?",
  "language": "mixed",
  "retrieval_query": "What is IRPF tax in Spain?\nWhat is IRPF impuesto impuesto sobre la renta de las personas fisicas impuesto sobre la renta renta",
  "retrieved_sources": [
    {
      "source_id": 12,
      "title": "Guia_50_preguntas",
      "similarity_score": 0.84,
      "rank": 1
    }
  ],
  "answer": "...",
  "answer_status": "generated",
  "retrieval_metrics": {
    "hit": true,
    "mrr": 1.0,
    "precision_at_k": 0.5
  },
  "judge_scores": {
    "groundedness": 1,
    "relevance": 1,
    "completeness": 0
  },
  "latency_ms": 1320,
  "retrieval_latency_ms": 290,
  "generation_latency_ms": 910,
  "expected_source_titles": ["Guia_50_preguntas"],
  "expected_answer_points": [
    "IRPF es un impuesto sobre la renta de las personas fisicas"
  ]
}
```

## Baseline Evaluation Packs

Do not start with a giant dataset.

Start with:

- 15 Spanish tax questions
- 10 mixed-language tax questions
- 5 refusal or low-evidence cases

That first pack is enough to compare:

- normalization on vs off
- `top_k=3` vs `top_k=5`
- prompt v1 vs prompt v2

## Teaching Workflow: How You Use This Like A Pro

This is the discipline you should follow every time.

### Before Running An Experiment

- define the decision you are trying to make
- choose one baseline
- change one important variable
- keep dataset and corpus version fixed

### During The Run

- log all config as params
- log aggregate outcomes as metrics
- save all per-example evidence as artifacts

### After The Run

- inspect failures first, not averages first
- compare against the baseline, not in isolation
- convert important failures into permanent regression examples

## Immediate Build Target

The first concrete implementation should support exactly this workflow:

1. load `tax_qa_es_v1` or `tax_qa_mixed_lang_v1`
2. run retrieval-only or end-to-end evaluation
3. compute deterministic retrieval metrics
4. compute deterministic answer metrics
5. run a small set of MLflow judge scorers
6. log one clean baseline run with artifacts

That is enough to make MLflow useful immediately without overbuilding the system.
