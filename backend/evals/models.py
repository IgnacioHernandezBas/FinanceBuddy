from pydantic import BaseModel, Field

class EvaluationExample(BaseModel):
    question_id: str
    question: str
    language: str
    difficulty: str
    expected_topics: list[str] = Field(default_factory=list)
    expected_source_titles: list[str] = Field(default_factory=list)
    expected_source_ids: list[int] = Field(default_factory=list)
    expected_answer_points: list[str] = Field(default_factory=list)
    must_refuse_without_evidence: bool = False
    notes: str | None = None


class EvaluationManifest(BaseModel):
    dataset_name: str
    dataset_version: str
    description: str
    language: str
    domain: str
    record_count: int
    created_on: str
    authoring_status: str
    source_family: str
    source_documents: list[str] = Field(default_factory=list)
    stored_source_titles: list[str] = Field(default_factory=list)
    intended_use: list[str] = Field(default_factory=list)
    scoring_targets: list[str] = Field(default_factory=list)
    required_record_fields: list[str] = Field(default_factory=list)
    corpus_assumptions: dict = Field(default_factory=dict)
    comparison_policy: dict = Field(default_factory=dict)
    baseline_configuration_expectations: dict = Field(default_factory=dict)
    known_limitations: list[str] = Field(default_factory=list)


class RetrievedSourceResult(BaseModel):
    source_id: int | None = None
    title: str
    similarity_score: float | None = None
    rank: int | None = None


class PerExampleResult(BaseModel):
    question_id: str
    question: str
    language: str
    retrieval_query: str
    retrieved_sources: list[RetrievedSourceResult] = Field(default_factory=list)
    answer: str | None = None
    answer_status: str | None = None
    retrieval_metrics: dict[str, float | bool] = Field(default_factory=dict)
    judge_scores: dict[str, float | int] = Field(default_factory=dict)
    latency_ms: float | None = None
    retrieval_latency_ms: float | None = None
    generation_latency_ms: float | None = None
    expected_source_titles: list[str] = Field(default_factory=list)
    expected_answer_points: list[str] = Field(default_factory=list)


class AggregateEvaluationResult(BaseModel):
    dataset_name: str
    dataset_version: str
    total_examples: int
    aggregate_metrics: dict[str, float] = Field(default_factory=dict)
    per_example_results: list[PerExampleResult] = Field(default_factory=list)


class SystemSourceResult(BaseModel):
    title: str
    url: str | None = None
    publisher: str | None = None


class SystemPerExampleResult(BaseModel):
    question_id: str
    question: str
    system_name: str
    answer: str
    answer_status: str | None = None
    latency_ms: float
    source_count: int = 0
    sources: list[SystemSourceResult] = Field(default_factory=list)
    matched_expected_source_count: int = 0
    used_web_search: bool = False
    trace_event_count: int = 0
    expected_source_titles: list[str] = Field(default_factory=list)
    expected_answer_points: list[str] = Field(default_factory=list)


class SystemAggregateEvaluationResult(BaseModel):
    dataset_name: str
    dataset_version: str
    system_name: str
    total_examples: int
    aggregate_metrics: dict[str, float] = Field(default_factory=dict)
    per_example_results: list[SystemPerExampleResult] = Field(default_factory=list)
