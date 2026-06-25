from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List

class ChatRequest(BaseModel):
    conversation_id: Optional[int] = None
    title: Optional[str] = None
    question: str
    thinking_enabled: bool = True

class MessageResponse(BaseModel):
    model: str
    response: str
    reasoning: Optional[str] = None
    tokens: Optional[int] = None
    latency_ms: Optional[int] = None
    cost: Optional[str] = None

class ChatResponse(BaseModel):
    message_id: int
    conversation_id: int
    user_question: str
    responses: List[MessageResponse]
    created_at: datetime
