from typing_extensions import Literal, TypedDict


ExplanationLevel = Literal["basic", "technical"]
RequestType = Literal["knowledge_qa", "document_analysis", "unsupported"]
WebAccessMode = Literal["disabled", "fallback_only", "allowed"]
InternalRetrievalStatus = Literal["ok", "empty", "failed"]
InternalEvidenceStatus = Literal["sufficient", "insufficient", "none"]
WebSearchDecision = Literal["not_needed", "not_allowed", "allowed"]
AnswerStatus = Literal[
    "answered_internal",
    "answered_mixed_sources",
    "insufficient_internal_only",
    "generation_failed",
    "agent_failed",
]

ChunkRecord = dict[str, object]
SourceRecord = dict[str, object]
WebResultRecord = dict[str, object]
TraceEventRecord = dict[str, object]


class AgentState(TypedDict, total=False):
    conversation_id: int | None
    user_message_id: int | None
    question: str
    explanation_level: ExplanationLevel
    user_allows_web_search: bool

    # Routing
    request_type: RequestType | None
    request_type_confidence: float | None

    # Policies
    web_access_mode: WebAccessMode
    allowed_web_domains: list[str]
    web_search_policy_reason: str | None

    # Retrieval
    retrieval_query: str | None
    internal_retrieval_status: InternalRetrievalStatus | None
    internal_chunks: list[ChunkRecord]
    internal_sources: list[SourceRecord]

    # Decision fields
    internal_evidence_status: InternalEvidenceStatus | None
    web_search_decision: WebSearchDecision | None

    web_search_query: str | None
    web_results: list[WebResultRecord]
    web_sources: list[SourceRecord]

    final_sources: list[SourceRecord]
    answer: str | None
    answer_status: AnswerStatus | None
    answer_policy_flags: list[str]
    requires_disclaimer: bool

    trace_events: list[TraceEventRecord]
    errors: list[str]
