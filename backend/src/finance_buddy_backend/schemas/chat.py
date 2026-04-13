from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    explanation_level: str
    conversation_id: int | None = None
    allow_web_search: bool = False


class ChatSource(BaseModel):
    title: str
    url: str | None = None
    publisher: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    conversation_id: int
    message_id: int


class AgentTraceEvent(BaseModel):
    node_name: str
    status: str
    summary: str | None = None
    retrieval_status: str | None = None
    retrieval_query: str | None = None
    scores: list[float] = Field(default_factory=list)
    decision: str | None = None
    chunk_count: int | None = None
    source_count: int | None = None
    answer_status: str | None = None
    request_type: str | None = None
    internal_evidence_status: str | None = None


class AgentRetrievedChunk(BaseModel):
    source_id: int | None = None
    source_title: str | None = None
    source_url: str | None = None
    source_publisher: str | None = None
    score: float | None = None
    text: str | None = None


class AgentWebResult(BaseModel):
    title: str | None = None
    url: str | None = None
    publisher: str | None = None
    snippet: str | None = None


class AgentChatResponse(ChatResponse):
    trace_events: list[AgentTraceEvent] = Field(default_factory=list)
    retrieved_chunks: list[AgentRetrievedChunk] = Field(default_factory=list)
    web_results: list[AgentWebResult] = Field(default_factory=list)


class ConversationMessage(BaseModel):
    id: int
    role: str
    content: str
    explanation_level: str | None
    answer_status: str | None
    created_at: datetime
    sources: list[ChatSource] = Field(default_factory=list)


class ConversationHistoryResponse(BaseModel):
    conversation_id: int
    messages: list[ConversationMessage]
