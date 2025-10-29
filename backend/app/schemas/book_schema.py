"""
Pydantic schemas for Book model
"""
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class BookConfig(BaseModel):
    """Book configuration from frontend"""
    bookIdea: str = Field(..., min_length=5, max_length=200, description="Book title or idea")
    description: Optional[str] = Field(None, max_length=2000, description="Book description")
    targetAudience: Optional[str] = Field(None, max_length=200, description="Target audience")
    genre: str = Field(..., min_length=2, max_length=50, description="Book genre")
    chapters: int = Field(ge=5, le=30, description="Number of chapters")
    wordsPerChapter: int = Field(ge=1000, le=10000, description="Words per chapter")
    tone: str = Field(default="professional", pattern="^(professional|casual|academic|conversational|humorous|formal)$", description="Writing tone")
    includeImages: bool = Field(default=False, description="Include images in book")
    includeCitations: bool = Field(default=True, description="Include citations")
    
    @classmethod
    def validate_genre(cls, v: str):
        """Validate genre against common genres"""
        common_genres = [
            "non-fiction", "technical", "business", "self-help", "biography",
            "history", "science", "education", "guide", "manual", "fiction",
            "how-to", "reference", "other"
        ]
        v_lower = v.lower()
        if v_lower not in common_genres and v_lower != "other":
            raise ValueError(f"Genre should be one of: {', '.join(common_genres)}")
        return v


class BookCreate(BaseModel):
    """Schema for creating a book"""
    title: Optional[str] = None
    book_idea: str
    description: Optional[str] = None
    genre: str
    target_audience: Optional[str] = None
    chapters_count: int
    words_per_chapter: int
    tone: str
    include_images: bool
    include_citations: bool


class ChapterPreview(BaseModel):
    """Preview of chapter data"""
    chapter_number: int
    title: Optional[str]
    status: str

    class Config:
        from_attributes = True


class BookResponse(BaseModel):
    """Schema for book response"""
    id: int
    title: Optional[str]
    book_idea: str
    description: Optional[str]
    genre: str
    target_audience: Optional[str]
    chapters_count: int
    words_per_chapter: int
    tone: str
    include_images: bool
    include_citations: bool
    status: str
    created_at: datetime
    updated_at: Optional[datetime]
    chapters: Optional[List[ChapterPreview]] = None

    class Config:
        from_attributes = True

