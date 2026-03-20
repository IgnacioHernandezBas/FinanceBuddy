from pydantic import BaseModel

# Define the schemas for the chat request and response (mocked for now, to be expanded later with actual logic and data structures)
class ChatRequest(BaseModel):
    message: str
    explanation_level: str


class ChatSource(BaseModel):
    title: str
    url: str


class ChatResponse(BaseModel):
    answer: str
    sources: list[ChatSource]
