# Evaluation Layer

This folder contains the first evaluation workflow for FinanceBuddy.

Current scope:

- retrieval-only evaluation
- dataset and manifest loading
- deterministic retrieval metrics
- MLflow tracking for baseline and comparison runs

Generation quality evaluation is not implemented yet.

## Current Goal

The current evaluation stack answers questions such as:

- Does the retriever return the expected source?
- How high is the expected source ranked?
- How much source noise appears in the retrieved set?
- Does a retriever configuration improve or hurt recall and precision?

This is intentionally separated from answer generation so retrieval quality can be measured without prompt or model noise.

## Folder Overview

- `datasets/`
  Versioned evaluation datasets. The current baseline is grounded in the Agencia Tributaria corpus.

- `manifests/`
  Metadata for each dataset: scope, assumptions, source titles, intended use, and scoring targets.

- `[models.py](/d:/FinanceBuddy/backend/evals/models.py)`
  Pydantic contracts for dataset examples, manifests, per-example results, and aggregate run results.

- `[loaders.py](/d:/FinanceBuddy/backend/evals/loaders.py)`
  Loads JSON files from disk and validates dataset-manifest consistency.

- `[rag_evaluator.py](/d:/FinanceBuddy/backend/evals/rag_evaluator.py)`
  Runs retrieval-only evaluation using the real retrieval path from the backend codebase.

- `[mlflow_tracking.py](/d:/FinanceBuddy/backend/evals/mlflow_tracking.py)`
  Logs retrieval evaluation runs to MLflow, including params, aggregate metrics, datasets, artifacts, and failure summaries.

- `[run_rag_eval.py](/d:/FinanceBuddy/backend/evals/run_rag_eval.py)`
  CLI entrypoint for evaluation runs.

- `metrics.py`
  Reserved for shared metric helpers. It is not the main scoring entrypoint yet because the first retrieval metrics are currently implemented directly in the evaluator.

## Model Reference

### `EvaluationExample`

Represents one benchmark question.

Key fields:

- `question_id`
  Stable identifier for regression tracking.

- `question`
  The query that will be sent through the retrieval pipeline.

- `expected_source_titles`
  The expected document titles for retrieval matching in `v1`.

- `expected_answer_points`
  Used later for generation and judge-based evaluation.

- `must_refuse_without_evidence`
  Reserved for later end-to-end RAG evaluation.

### `EvaluationManifest`

Describes the dataset itself.

Key fields:

- `dataset_name`, `dataset_version`
- `stored_source_titles`
  The titles currently stored in the database and used for title-based matching.

- `scoring_targets`
  The metrics this dataset is intended to support.

- `corpus_assumptions`
  Documents the ingestion and source-title rules behind the dataset.

### `RetrievedSourceResult`

Represents one retrieved source in a per-example result.

Key fields:

- `source_id`
  Logged for debugging and local inspection.

- `title`
  Used as the primary retrieval matching key in `v1`.

- `similarity_score`
- `rank`

### `PerExampleResult`

Represents the evaluation output for one benchmark question.

Key fields:

- `retrieval_query`
  The query form used for evaluation traceability, including normalization effects.

- `retrieved_sources`
  The unique source list derived from chunk-level retrieval results.

- `retrieval_metrics`
  Per-question retrieval metrics such as hit, MRR, and precision.

### `AggregateEvaluationResult`

Represents the full outcome of one retrieval evaluation run.

Key fields:

- `aggregate_metrics`
  Dataset-level metrics logged to MLflow.

- `per_example_results`
  Full evidence used for analysis and failure inspection.

## Current Matching Rule

The current benchmark uses title-based matching.

That means:

- `expected_source_titles` is the authoritative ground truth in `v1`
- `source_id` is logged for debugging and local DB inspection

This is intentional because titles are more stable across database rebuilds than auto-increment IDs.

## Current Metrics

The retrieval evaluator currently computes:

- `retrieval_hit_rate`
- `retrieval_mrr`
- `retrieval_source_precision_at_k`

Per example, it records:

- `hit`
- `mrr`
- `precision_at_k`

## Current Workflow

1. Load dataset JSON.
2. Load manifest JSON.
3. Validate that the dataset matches the manifest.
4. Run retrieval-only evaluation against the current PostgreSQL corpus.
5. Log the run to MLflow.

Current MLflow outputs include:

- params
- aggregate metrics
- tracked dataset input
- raw dataset artifact
- raw manifest artifact
- aggregate evaluation result JSON
- per-example results JSON
- failure summary Markdown
- evaluation notes Markdown

## Example Command

From `[backend](/d:/FinanceBuddy/backend)`:

```powershell
uv run python -m evals.run_rag_eval --dataset-path evals/datasets/tax_qa_es_v1.json --manifest-path evals/manifests/tax_qa_es_v1_manifest.json --top-k 5 --log-to-mlflow --run-name baseline_tax_es_top5
```

## Current Baseline Findings

The first retrieval experiments already showed:

- `top_k=5` gives stronger recall
- `top_k=3` gives cleaner source precision
- retrieval issues currently come more from ranking and source noise than from total recall failure

That means the next retrieval work should focus on retriever comparisons, not on generation yet.

## Next Planned Evaluation Steps

- compare query normalization on vs off
- improve retrieval artifacts and failure analysis
- add generation evaluation later
- add LLM-as-a-judge metrics only after retrieval evaluation is stable
