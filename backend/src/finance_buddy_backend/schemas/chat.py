from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str
    explanation_level: str
    conversation_id: int | None = None


class ChatSource(BaseModel):
    title: str
    url: str | None = None
    publisher: str | None = None


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    conversation_id: int


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
