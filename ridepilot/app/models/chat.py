from datetime import datetime

from pydantic import BaseModel, Field


class ChatRequest(BaseModel):
    message: str = Field(min_length=1)
    conversation_id: str | None = None


class ChatHistoryMessage(BaseModel):
    id: str
    role: str
    content: str
    created_at: datetime


class ChatHistoryResponse(BaseModel):
    conversation_id: str
    messages: list[ChatHistoryMessage]