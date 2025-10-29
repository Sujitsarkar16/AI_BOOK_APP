"""
Book management API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.core.database import get_db
from app.models.book import Book
from app.models.chapter import Chapter
from app.schemas.book_schema import BookConfig, BookCreate, BookResponse
from app.schemas.generation_schema import GenerationStatus, AgentStatus, AgentStatusEnum, ChapterStatusEnum
from app.services.research_service import research_service
from app.services.rag_service import rag_service
from app.core.llm_config import get_llm_config
import google.generativeai as genai
import logging

logger = logging.getLogger(__name__)

router = APIRouter()


def convert_book_config(config: BookConfig) -> dict:
    """Convert frontend book config to database format"""
    return {
        "book_idea": config.bookIdea,
        "description": config.description,
        "genre": config.genre,
        "target_audience": config.targetAudience,
        "chapters_count": config.chapters,
        "words_per_chapter": config.wordsPerChapter,
        "tone": config.tone,
        "include_images": config.includeImages,
        "include_citations": config.includeCitations,
    }


@router.post("/api/books", response_model=BookResponse)
async def create_book(book_config: BookConfig, db: Session = Depends(get_db)):
    """Create a new book from configuration"""
    
    # Convert config
    book_data = convert_book_config(book_config)
    
    # Create book
    book = Book(**book_data)
    db.add(book)
    db.commit()
    db.refresh(book)
    
    logger.info(f"Created book {book.id}: {book.book_idea}")
    
    # Run ideation phase with AI agent
    refined_concept = ""
    introduction = ""
    
    try:
        from app.core.config import settings
        
        # Check if Gemini API key is configured
        if not settings.gemini_api_key or settings.gemini_api_key == "":
            logger.error("GEMINI_API_KEY not configured in environment variables")
            refined_concept = f"Book concept: {book.book_idea}. This book will explore {book.description or 'the main topic'} for {book.target_audience or 'readers'} in a {book.tone} tone."
            introduction = f"Welcome to {book.book_idea}! This book will guide you through {book.description or 'an exploration of the topic'}."
        else:
            model = genai.GenerativeModel('gemini-2.0-flash')
            
            # Step 1: Refine the book concept
            concept_prompt = f"""
            You are an expert book ideation specialist. Refine and enhance this book concept:
            
            Title/Idea: {book.book_idea}
            Description: {book.description or 'No description provided'}
            Genre: {book.genre}
            Target Audience: {book.target_audience or 'General audience'}
            Tone: {book.tone}
            
            Provide 3-4 paragraphs that:
            1. Expand on the core concept with unique angles
            2. Explain why this book would be valuable
            3. Highlight what makes it different from other books
            4. Connect with the target audience's needs
            
            Be compelling and specific.
            """
            
            response = model.generate_content(concept_prompt)
            refined_concept = response.text if response and response.text else f"Book concept: {book.book_idea}"
            
            # Step 2: Create an engaging introduction
            intro_prompt = f"""
            Write a compelling introduction (2-3 paragraphs) for this book:
            
            Title: {book.book_idea}
            Refined Concept: {refined_concept[:500]}
            Genre: {book.genre}
            Target Audience: {book.target_audience}
            
            The introduction should:
            1. Hook the reader immediately
            2. Explain what they'll learn and gain
            3. Set the tone and style
            4. Create anticipation for the content
            
            Write in a {book.tone} tone.
            """
            
            intro_response = model.generate_content(intro_prompt)
            introduction = intro_response.text if intro_response and intro_response.text else f"Welcome to {book.book_idea}!"
            
            logger.info("Ideation phase completed successfully")
        
    except Exception as e:
        logger.error(f"Error in ideation: {e}", exc_info=True)
        refined_concept = f"Book concept: {book.book_idea}"
        introduction = f"Welcome to {book.book_idea}!"
    
    # Run research phase
    try:
        research_results = research_service.search_web(book.book_idea, max_results=10)
        
        # Store in RAG
        documents = [r.get('snippet', '') for r in research_results if r.get('snippet')]
        metadata = [
            {'url': r.get('url', ''), 'title': r.get('title', ''), 'source': 'web_search'}
            for r in research_results
        ]
        
        if documents:
            rag_service.add_documents(book.id, documents, metadata)
            
    except Exception as e:
        logger.error(f"Error in research: {e}")
    
    # Create chapters with outlines
    chapters = []
    for i in range(1, book.chapters_count + 1):
        chapter = Chapter(
            book_id=book.id,
            chapter_number=i,
            title=f"Chapter {i}: To Be Determined",
            status="pending"
        )
        chapters.append(chapter)
        db.add(chapter)
    
    # Generate detailed outline with AI agent
    try:
        outline_prompt = f"""
        You are an expert at structuring non-fiction books. Create a compelling chapter outline for this book:
        
        Title: {book.book_idea}
        Refined Concept: {refined_concept[:300]}
        Genre: {book.genre}
        Target Audience: {book.target_audience}
        Tone: {book.tone}
        Number of Chapters: {book.chapters_count}
        
        For each chapter, provide:
        1. A compelling, specific chapter title (not generic)
        2. A brief 2-3 sentence description of what the chapter will cover
        3. Ensure logical flow from chapter to chapter
        4. Make each chapter actionable and valuable
        
        Format each chapter as:
        CHAPTER_NUMBER: TITLE
        Description: Your description here
        
        Example:
        1: Getting Started with the Basics
        Description: This chapter introduces fundamental concepts that readers need to understand before diving deeper. We'll cover essential terminology, key principles, and why these fundamentals matter.
        
        Continue for all {book.chapters_count} chapters.
        """
        
        outline_response = model.generate_content(outline_prompt)
        
        if outline_response and outline_response.text:
            # Parse outline and update chapters
            lines = outline_response.text.strip().split('\n')
            current_chapter_idx = -1
            current_title = ""
            current_desc = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Check if it's a chapter number line
                if ':' in line and (line.startswith(('1', '2', '3', '4', '5', '6', '7', '8', '9', '10', '11', '12', '13', '14', '15'))):
                    # Save previous chapter if exists
                    if current_chapter_idx >= 0 and current_chapter_idx < len(chapters):
                        chapters[current_chapter_idx].title = current_title
                        chapters[current_chapter_idx].outline = ' '.join(current_desc)
                    
                    # Start new chapter
                    parts = line.split(':', 1)
                    current_chapter_idx = int(parts[0].strip()) - 1
                    current_title = parts[1].strip() if len(parts) > 1 else ""
                    current_desc = []
                    
                elif line.lower().startswith('description:'):
                    desc_text = line.replace('Description:', '').strip()
                    if desc_text:
                        current_desc.append(desc_text)
                elif current_desc or (current_chapter_idx >= 0 and line):
                    # Add to current description
                    current_desc.append(line)
            
            # Save last chapter
            if current_chapter_idx >= 0 and current_chapter_idx < len(chapters):
                chapters[current_chapter_idx].title = current_title
                chapters[current_chapter_idx].outline = ' '.join(current_desc)
            
            logger.info("Outline generated successfully")
            
    except Exception as e:
        logger.error(f"Error creating outline: {e}")
    
    # Update book description with refined concept and introduction
    if refined_concept or introduction:
        enhanced_description = f"{book.description or ''}\n\n"
        if refined_concept:
            enhanced_description += f"## Refined Concept\n{refined_concept}\n\n"
        if introduction:
            enhanced_description += f"## Introduction\n{introduction}\n\n"
        book.description = enhanced_description.strip()
    
    db.commit()
    db.refresh(book)
    
    # Update book status
    book.status = "initialized"
    db.commit()
    db.refresh(book)
    
    logger.info(f"Book {book.id} initialized with outline and AI-generated content")
    
    return BookResponse.from_orm(book)


@router.get("/api/books/{book_id}", response_model=BookResponse)
async def get_book(book_id: int, db: Session = Depends(get_db)):
    """Get book details with chapters"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    return BookResponse.from_orm(book)


@router.get("/api/books/{book_id}/status", response_model=GenerationStatus)
async def get_book_status(book_id: int, db: Session = Depends(get_db)):
    """Get generation status"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapters = db.query(Chapter).filter(Chapter.book_id == book_id).all()
    
    # Calculate completion status
    total = len(chapters)
    complete = sum(1 for c in chapters if c.status == "complete")
    
    # Default agent statuses (idle)
    agents = [
        AgentStatus(agent_name="ideation_agent", status=AgentStatusEnum.IDLE),
        AgentStatus(agent_name="research_agent", status=AgentStatusEnum.IDLE),
        AgentStatus(agent_name="outline_agent", status=AgentStatusEnum.IDLE),
        AgentStatus(agent_name="writing_agent", status=AgentStatusEnum.IDLE),
        AgentStatus(agent_name="content_agent", status=AgentStatusEnum.IDLE),
        AgentStatus(agent_name="editor_agent", status=AgentStatusEnum.IDLE),
        AgentStatus(agent_name="format_agent", status=AgentStatusEnum.IDLE),
    ]
    
    return GenerationStatus(
        book_id=book_id,
        book_status=book.status,
        chapters_total=total,
        chapters_complete=complete,
        current_chapter=None,
        agents=agents
    )


@router.delete("/api/books/{book_id}")
async def delete_book(book_id: int, db: Session = Depends(get_db)):
    """Delete book and cleanup resources"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    # Delete from RAG
    try:
        rag_service.delete_book_documents(book_id)
    except Exception as e:
        logger.error(f"Error deleting RAG data: {e}")
    
    # Delete book (cascades to chapters, sources, logs)
    db.delete(book)
    db.commit()
    
    return {"message": "Book deleted successfully"}

