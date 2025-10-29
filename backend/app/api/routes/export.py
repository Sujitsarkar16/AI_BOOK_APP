"""
Export API routes
"""
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse, Response
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.book import Book
from app.models.chapter import Chapter
import tempfile
import os

router = APIRouter()


@router.get("/api/books/{book_id}/export/markdown")
async def export_markdown(book_id: int, db: Session = Depends(get_db)):
    """Export book as markdown file"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapters = db.query(Chapter).filter(
        Chapter.book_id == book_id,
        Chapter.status == "complete"
    ).order_by(Chapter.chapter_number).all()
    
    if not chapters:
        raise HTTPException(status_code=400, detail="No completed chapters to export")
    
    # Build markdown content
    markdown = f"# {book.title or book.book_idea}\n\n"
    markdown += f"**Genre:** {book.genre}\n\n"
    markdown += f"**Description:** {book.description or ''}\n\n"
    markdown += "---\n\n"
    
    for chapter in chapters:
        markdown += f"## {chapter.title}\n\n"
        if chapter.content_markdown:
            markdown += f"{chapter.content_markdown}\n\n"
        markdown += "---\n\n"
    
    # Return as file response
    return Response(
        content=markdown,
        media_type="text/markdown",
        headers={
            "Content-Disposition": f'attachment; filename="{book.book_idea.replace(" ", "_")}.md"'
        }
    )


@router.get("/api/books/{book_id}/export/html")
async def export_html(book_id: int, db: Session = Depends(get_db)):
    """Export book as HTML file"""
    
    book = db.query(Book).filter(Book.id == book_id).first()
    if not book:
        raise HTTPException(status_code=404, detail="Book not found")
    
    chapters = db.query(Chapter).filter(
        Chapter.book_id == book_id,
        Chapter.status == "complete"
    ).order_by(Chapter.chapter_number).all()
    
    if not chapters:
        raise HTTPException(status_code=400, detail="No completed chapters to export")
    
    # Build HTML content
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <title>{book.book_idea}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                line-height: 1.6;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #34495e;
                margin-top: 30px;
            }}
        </style>
    </head>
    <body>
        <h1>{book.book_idea}</h1>
        <p><strong>Genre:</strong> {book.genre}</p>
        <p>{book.description or ''}</p>
        <hr>
    """
    
    for chapter in chapters:
        html += f"<h2>{chapter.title}</h2>\n"
        if chapter.content_markdown:
            # Simple markdown to HTML conversion
            content = chapter.content_markdown.replace('\n', '<br>\n')
            html += f"<div>{content}</div>\n"
        html += "<hr>\n"
    
    html += "</body></html>"
    
    return Response(
        content=html,
        media_type="text/html",
        headers={
            "Content-Disposition": f'attachment; filename="{book.book_idea.replace(" ", "_")}.html"'
        }
    )

