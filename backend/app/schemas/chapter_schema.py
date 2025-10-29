"""
Pydantic schemas for Chapter model
"""
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime


class TOCItem(BaseModel):
    """Table of contents item"""
    chapter: int
    title: str
    status: str
    outline: Optional[str] = None


class ChapterResponse(BaseModel):
    """Schema for chapter response"""
    id: int
    book_id: int
    chapter_number: int
    title: Optional[str]
    outline: Optional[str]
    content_markdown: Optional[str]
    status: str
    word_count: int
    created_at: datetime
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True


class ChapterUpdate(BaseModel):
    """Schema for updating a chapter"""
    title: Optional[str] = None
    content_markdown: Optional[str] = None
    outline: Optional[str] = None

