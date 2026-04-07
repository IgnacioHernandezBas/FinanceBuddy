from typing import Literal
from pydantic import BaseModel

class MessageFeedbackRequest(BaseModel):
    rating: Literal["positive", "negative"]
    comment: str | None = None

class MessageFeedbackResponse(BaseModel):
    message_id: int
    rating: Literal["positive", "negative"]
    comment: str | None = None
