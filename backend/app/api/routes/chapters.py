"""
Chapter API routes
"""
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.book import Book
from app.models.chapter import Chapter
from app.schemas.chapter_schema import ChapterResponse, ChapterUpdate, TOCItem
from app.services.rag_service import rag_service
from app.core.llm_config import get_llm_config
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/api/books/{book_id}/chapters", response_model=List[TOCItem])
async def get_chapters(book_id: int, db: Session = Depends(get_db)):
    """Get all chapters for a book"""
    
    chapters = db.query(Chapter).filter(Chapter.book_id == book_id).order_by(Chapter.chapter_number).all()
    
    if not chapters:
        raise HTTPException(status_code=404, detail="Book not found or no chapters")
    
    toc = [
        TOCItem(
            chapter=ch.chapter_number,
            title=ch.title or f"Chapter {ch.chapter_number}: Untitled",
            status=ch.status,
            outline=ch.outline
        )
        for ch in chapters
    ]
    
    return toc


@router.get("/api/books/{book_id}/chapters/{chapter_number}", response_model=ChapterResponse)
async def get_chapter(book_id: int, chapter_number: int, db: Session = Depends(get_db)):
    """Get a single chapter by chapter number"""
    
    chapter = db.query(Chapter).filter(
        Chapter.chapter_number == chapter_number,
        Chapter.book_id == book_id
    ).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    return ChapterResponse.from_orm(chapter)


async def generate_chapter_content(book_id: int, chapter_id: int, db: Session):
    """Background task to generate chapter content"""
    
    # Import here to avoid circular dependency
    from app.api.routes.websocket import broadcast_to_book
    
    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id,
        Chapter.book_id == book_id
    ).first()
    
    if not chapter:
        return
    
    # Update status to generating
    chapter.status = "generating"
    db.commit()
    
    # Broadcast agent status update
    await broadcast_to_book(book_id, 'agent_status', {
        'agent_name': 'writing_agent',
        'status': 'active',
        'current_task': f'Generating {chapter.title}'
    })
    
    try:
        book = db.query(Book).filter(Book.id == book_id).first()
        
        # Get RAG context
        context_chunks = rag_service.search_relevant_context(book_id, chapter.outline or chapter.title or "", top_k=5)
        context = "\n\n".join([chunk.get('text', '') for chunk in context_chunks])
        
        # Generate content with Gemini
        llm_config = get_llm_config()
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        prompt = f"""
        Write a comprehensive chapter for this book.
        
        Chapter Title: {chapter.title}
        Chapter Description/Outline: {chapter.outline}
        Target Word Count: {book.words_per_chapter}
        Tone: {book.tone}
        Genre: {book.genre}
        Target Audience: {book.target_audience}
        
        Context from research:
        {context[:1000] if context else "No additional context available"}
        
        Write the chapter in markdown format with proper headings, lists, and emphasis.
        Make it engaging, informative, and suitable for {book.target_audience or 'general readers'}.
        """
        
        response = model.generate_content(prompt)
        content = response.text if response else ""
        
        # Update chapter
        chapter.content_markdown = content
        chapter.word_count = len(content.split()) if content else 0
        chapter.status = "complete"
        db.commit()
        
        # Broadcast agent idle status
        await broadcast_to_book(book_id, 'agent_status', {
            'agent_name': 'writing_agent',
            'status': 'idle',
            'current_task': None
        })
        
        # Broadcast chapter completion
        await broadcast_to_book(book_id, 'chapter_update', {
            'chapter_number': chapter.chapter_number,
            'status': 'complete',
            'book_id': book_id
        })
        
        logger.info(f"Generated chapter {chapter.chapter_number} for book {book_id}")
        
    except Exception as e:
        logger.error(f"Error generating chapter: {e}", exc_info=True)
        chapter.status = "failed"  # Set to failed instead of pending to indicate error
        db.commit()
        
        # Broadcast error status
        await broadcast_to_book(book_id, 'agent_status', {
            'agent_name': 'writing_agent',
            'status': 'error',
            'current_task': f'Error generating {chapter.title}'
        })


@router.post("/api/books/{book_id}/chapters/{chapter_number}/generate")
async def generate_chapter_endpoint(
    book_id: int, 
    chapter_number: int, 
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate a single chapter"""
    
    chapter = db.query(Chapter).filter(
        Chapter.chapter_number == chapter_number,
        Chapter.book_id == book_id
    ).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if chapter.status == "complete":
        raise HTTPException(status_code=400, detail="Chapter already generated")
    
    # Start background task
    background_tasks.add_task(generate_chapter_content, book_id, chapter.id, db)
    
    return {"message": "Chapter generation started", "chapter_number": chapter_number}


@router.post("/api/books/{book_id}/chapters/generate-all")
async def generate_all_chapters(
    book_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    """Generate all pending chapters"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapters = db.query(Chapter).filter(
        Chapter.book_id == book_id,
        Chapter.status == "pending"
    ).order_by(Chapter.chapter_number).all()
    
    # Start generation for each chapter
    for chapter in chapters:
        background_tasks.add_task(generate_chapter_content, book_id, chapter.id, db)
    
    return {"message": f"Generation started for {len(chapters)} chapters", "chapters": len(chapters)}


@router.put("/api/books/{book_id}/chapters/{chapter_id}")
async def update_chapter(
    book_id: int,
    chapter_id: int,
    chapter_update: ChapterUpdate,
    db: Session = Depends(get_db)
):
    """Update chapter content manually"""
    
    chapter = db.query(Chapter).filter(
        Chapter.id == chapter_id,
        Chapter.book_id == book_id
    ).first()
    
    if not chapter:
        raise HTTPException(status_code=404, detail="Chapter not found")
    
    if chapter_update.title:
        chapter.title = chapter_update.title
    if chapter_update.content_markdown:
        chapter.content_markdown = chapter_update.content_markdown
        chapter.word_count = len(chapter_update.content_markdown.split())
    if chapter_update.outline:
        chapter.outline = chapter_update.outline
    
    db.commit()
    
    return {"message": "Chapter updated"}

