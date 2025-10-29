"""
Book idea generation API routes
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from app.core.config import settings
import google.generativeai as genai
import logging
import json
import uuid

logger = logging.getLogger(__name__)

router = APIRouter()

class IdeaGenerationRequest(BaseModel):
    topics: str
    keywords: str

class BookIdea(BaseModel):
    id: str
    title: str
    description: str
    genre: str
    targetAudience: str
    uniqueAngle: str
    marketPotential: str

class IdeaGenerationResponse(BaseModel):
    success: bool
    ideas: List[BookIdea]
    message: Optional[str] = None

@router.post("/api/generate-ideas", response_model=IdeaGenerationResponse)
async def generate_book_ideas(request: IdeaGenerationRequest):
    """Generate book ideas based on topics and keywords using AI ideation agent"""
    
    try:
        # Check if Gemini API key is configured
        if not settings.gemini_api_key or settings.gemini_api_key == "your-actual-api-key-here":
            logger.error("GEMINI_API_KEY not configured")
            raise HTTPException(
                status_code=500, 
                detail="AI service not configured. Please set up your API key."
            )
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # Create comprehensive prompt for book idea generation
        prompt = f"""
You are an expert book ideation specialist and publishing consultant with deep knowledge of market trends, reader preferences, and successful book concepts. Your task is to generate 6 compelling, unique book ideas based on the user's interests.

User Input:
- Topics/Themes: {request.topics}
- Keywords/Interests: {request.keywords}

Generate 6 diverse book ideas that:
1. Are commercially viable and have market potential
2. Offer unique angles or fresh perspectives
3. Have clear target audiences
4. Are actionable and valuable to readers
5. Cover different genres/styles to give variety
6. Are specific enough to be compelling but broad enough to be developed

For each idea, provide:
- A compelling, marketable title (not generic)
- A 2-3 sentence description that hooks the reader
- The most appropriate genre/category
- Specific target audience description
- What makes this angle unique/different
- Market potential and why it would succeed

Format your response as a JSON array with this exact structure:
[
  {{
    "title": "Compelling Book Title",
    "description": "2-3 sentence description that explains what the book is about and why it's valuable",
    "genre": "Genre/Category",
    "targetAudience": "Specific description of who would read this book",
    "uniqueAngle": "What makes this book different from others in the market",
    "marketPotential": "Why this book would succeed and what market gap it fills"
  }},
  // ... repeat for all 6 ideas
]

Make sure each idea is distinct and covers different aspects of the user's interests. Vary the genres, audiences, and approaches to give maximum choice.
"""

        # Generate ideas using AI
        response = model.generate_content(prompt)
        
        if not response or not response.text:
            raise HTTPException(status_code=500, detail="Failed to generate ideas")
        
        # Parse the JSON response
        try:
            # Extract JSON from response (in case there's extra text)
            response_text = response.text.strip()
            if response_text.startswith('```json'):
                response_text = response_text[7:]
            if response_text.endswith('```'):
                response_text = response_text[:-3]
            
            ideas_data = json.loads(response_text)
            
            # Convert to our BookIdea format with unique IDs
            ideas = []
            for idea_data in ideas_data:
                idea = BookIdea(
                    id=str(uuid.uuid4()),
                    title=idea_data.get('title', 'Untitled Book'),
                    description=idea_data.get('description', 'No description provided'),
                    genre=idea_data.get('genre', 'General'),
                    targetAudience=idea_data.get('targetAudience', 'General audience'),
                    uniqueAngle=idea_data.get('uniqueAngle', 'Unique perspective'),
                    marketPotential=idea_data.get('marketPotential', 'Good market potential')
                )
                ideas.append(idea)
            
            logger.info(f"Generated {len(ideas)} book ideas successfully")
            
            return IdeaGenerationResponse(
                success=True,
                ideas=ideas,
                message=f"Successfully generated {len(ideas)} unique book ideas"
            )
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse AI response as JSON: {e}")
            logger.error(f"Raw response: {response.text}")
            
            # Fallback: create ideas manually if JSON parsing fails
            fallback_ideas = create_fallback_ideas(request.topics, request.keywords)
            return IdeaGenerationResponse(
                success=True,
                ideas=fallback_ideas,
                message="Generated ideas using fallback method"
            )
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating book ideas: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, 
            detail=f"An error occurred while generating book ideas: {str(e)}"
        )

def create_fallback_ideas(topics: str, keywords: str) -> List[BookIdea]:
    """Create fallback ideas when AI generation fails"""
    
    # Combine topics and keywords for idea generation
    combined_input = f"{topics} {keywords}".strip().lower()
    
    # Simple keyword-based idea generation
    ideas = []
    
    # Idea 1: Based on main topic
    main_topic = topics.split(',')[0].strip() if topics else "your interests"
    ideas.append(BookIdea(
        id=str(uuid.uuid4()),
        title=f"The Complete Guide to {main_topic.title()}",
        description=f"A comprehensive resource covering all aspects of {main_topic}, from basics to advanced concepts. Perfect for beginners and experts alike.",
        genre="How-To/Guide",
        targetAudience=f"People interested in {main_topic}",
        uniqueAngle=f"Comprehensive coverage with practical examples",
        marketPotential=f"Strong demand for {main_topic} content"
    ))
    
    # Idea 2: Personal experience angle
    ideas.append(BookIdea(
        id=str(uuid.uuid4()),
        title=f"My Journey with {main_topic.title()}",
        description=f"A personal memoir sharing lessons learned, challenges overcome, and insights gained through experience with {main_topic}.",
        genre="Memoir/Self-Help",
        targetAudience=f"People starting their {main_topic} journey",
        uniqueAngle="Personal experience and authentic storytelling",
        marketPotential="Growing interest in personal development stories"
    ))
    
    # Idea 3: Business/Professional angle
    ideas.append(BookIdea(
        id=str(uuid.uuid4()),
        title=f"{main_topic.title()} for Professionals",
        description=f"A practical guide for professionals looking to leverage {main_topic} in their career. Includes case studies and actionable strategies.",
        genre="Business/Professional",
        targetAudience="Working professionals and entrepreneurs",
        uniqueAngle="Professional application and career focus",
        marketPotential="High demand for professional development content"
    ))
    
    return ideas
