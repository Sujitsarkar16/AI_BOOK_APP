"""
Book model
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Book(Base):
    __tablename__ = "books"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=True)
    book_idea = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    genre = Column(String, nullable=False)
    target_audience = Column(String, nullable=True)
    chapters_count = Column(Integer, nullable=False, default=10)
    words_per_chapter = Column(Integer, nullable=False, default=2500)
    tone = Column(String, nullable=False, default="professional")
    include_images = Column(Boolean, default=False)
    include_citations = Column(Boolean, default=True)
    status = Column(String, default="draft")  # draft, initialized, generating, completed
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    chapters = relationship("Chapter", back_populates="book", cascade="all, delete-orphan")
    sources = relationship("Source", back_populates="book", cascade="all, delete-orphan")
    agent_logs = relationship("AgentLog", back_populates="book", cascade="all, delete-orphan")

