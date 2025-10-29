"""
Pydantic schemas for chat/interaction
"""
from pydantic import BaseModel
from typing import Optional, List


class ChatMessage(BaseModel):
    """Chat message structure"""
    role: str  # "user" or "assistant"
    content: str


class ChatRequest(BaseModel):
    """Request for chat/interaction"""
    message: str
    context: Optional[dict] = None


class ChatResponse(BaseModel):
    """Response from chat"""
    response: str
    agent_name: Optional[str] = None
    actions_taken: Optional[List[str]] = None

