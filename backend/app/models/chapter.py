"""
Chapter model
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.core.database import Base


class Chapter(Base):
    __tablename__ = "chapters"
    
    id = Column(Integer, primary_key=True, index=True)
    book_id = Column(Integer, ForeignKey("books.id"), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    title = Column(String, nullable=True)
    outline = Column(Text, nullable=True)
    content_markdown = Column(Text, nullable=True)
    status = Column(String, default="pending")  # pending, generating, complete, failed
    word_count = Column(Integer, default=0)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    book = relationship("Book", back_populates="chapters")
    sources = relationship("Source", back_populates="chapter")
    agent_logs = relationship("AgentLog", back_populates="chapter")

