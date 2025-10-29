"""
Pydantic schemas for generation and agent status
"""
from pydantic import BaseModel
from typing import Optional, List
from enum import Enum


class AgentStatusEnum(str, Enum):
    """Agent status values"""
    IDLE = "idle"
    ACTIVE = "active"
    ERROR = "error"


class ChapterStatusEnum(str, Enum):
    """Chapter status values"""
    PENDING = "pending"
    GENERATING = "generating"
    COMPLETE = "complete"


class AgentStatus(BaseModel):
    """Current status of an agent"""
    agent_name: str
    status: AgentStatusEnum
    current_task: Optional[str] = None


class GenerationStatus(BaseModel):
    """Overall generation status"""
    book_id: int
    book_status: str
    chapters_total: int
    chapters_complete: int
    current_chapter: Optional[int] = None
    agents: List[AgentStatus]


class WebSocketMessage(BaseModel):
    """WebSocket message structure"""
    type: str
    data: dict

