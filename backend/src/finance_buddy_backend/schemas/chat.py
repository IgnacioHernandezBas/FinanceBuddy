from pydantic import BaseModel
from datetime import datetime

class ChatRequest(BaseModel):
    message: str
    explanation_level: str
    conversation_id: int | None = None  # can be None for new conversations


class ChatSource(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
    conversation_id: int

class ConversationMessage(BaseModel):
    id: int
    role: str
    content: str
    explanation_level: str |None
    answer_status: str | None
    created_at: datetime

class ConversationHistoryResponse(BaseModel):
    conversation_id: int
    messages: list[ConversationMessage]