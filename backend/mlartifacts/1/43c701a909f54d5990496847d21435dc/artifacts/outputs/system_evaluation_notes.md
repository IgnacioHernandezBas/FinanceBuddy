# System Evaluation Notes

- This run evaluates end-to-end system behavior rather than retrieval alone.
- answer_success_rate: share of answers with status answered_internal, answered_mixed_sources or generated. A success can still be an answer that says the evidence is insufficient.
- fact_recall: deterministic whole-word, accent-insensitive match of each example's expected_facts in the answer.
- judge_point_coverage (only when judge_enabled): share of expected_answer_points an LLM judge marks as covered. The judge uses the same Gemini model that generates the answers, so treat it as indicative.
- needs_review marks examples where fact_recall and judge coverage differ by 0.5 or more; check those by hand.
- Compare these runs side by side in MLflow using the same dataset and manifest.
