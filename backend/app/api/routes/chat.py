"""
Chat/Interaction API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.book import Book
from app.models.chapter import Chapter
from app.schemas.chat_schema import ChatRequest, ChatResponse
from app.core.llm_config import get_llm_config
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/api/books/{book_id}/chat", response_model=ChatResponse)
async def chat_with_book(
    book_id: int,
    chat_request: ChatRequest,
    db: Session = Depends(get_db)
):
    """Handle chat/interaction requests for a book"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        You are helping with book generation. User request: {chat_request.message}
        
        Book: {book.book_idea}
        Genre: {book.genre}
        Tone: {book.tone}
        
        Provide a helpful response about how you'll address this request or what actions you'll take.
        Be specific and actionable.
        """
        
        response = model.generate_content(prompt)
        
        return ChatResponse(
            response=response.text if response else "I understand your request.",
            agent_name="ideation_agent"
        )
        
    except Exception as e:
        logger.error(f"Chat error: {e}")
        raise HTTPException(status_code=500, detail="Error processing chat request")

