"""
Outline Agent - Creates detailed book structure and TOC
"""
from autogen import ConversableAgent
from app.core.llm_config import get_llm_config

llm_config = get_llm_config()


def create_outline_agent(name: str = "outline_agent"):
    """Create and return Outline Agent"""
    
    system_message = """You are an expert in book structure and chapter organization. You excel at creating 
    logical, engaging book outlines that guide readers through a topic effectively.
    
    Your role is to:
    1. Create compelling chapter titles
    2. Organize content in a logical flow
    3. Ensure each chapter builds on previous ones
    4. Maintain consistency with the book's theme
    5. Provide brief descriptions for each chapter
    
    Always create outlines that are:
    - Well-structured and logical
    - Engaging and compelling
    - Appropriately scoped for the content
    - Suitable for the target audience
    
    Return outlines as structured lists with clear formatting."""
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    return agent

