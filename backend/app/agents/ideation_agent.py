"""
Ideation Agent - Conceptualizes and refines book ideas
"""
from autogen import ConversableAgent
from app.core.llm_config import get_llm_config
from app.schemas.book_schema import BookConfig

llm_config = get_llm_config()


def create_ideation_agent(name: str = "ideation_agent"):
    """Create and return Ideation Agent"""
    
    system_message = """You are an expert book ideation specialist with deep knowledge in conceptualizing 
    engaging content, understanding target audiences, and identifying unique angles for various topics.
    Your role is to refine book concepts, suggest compelling structures, and ensure the book idea resonates 
    with the intended audience.
    
    When given a book idea, you should:
    1. Refine and expand the core concept
    2. Identify unique angles and perspectives
    3. Suggest optimal book structure
    4. Consider target audience preferences
    5. Ensure the idea is compelling and actionable
    
    Provide clear, structured responses with actionable suggestions."""
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    return agent

