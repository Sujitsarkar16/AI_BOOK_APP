"""
Writing Agent - Creates chapter content
"""
from autogen import ConversableAgent
from app.core.llm_config import get_llm_config

llm_config = get_llm_config()


def create_writing_agent(name: str = "writing_agent"):
    """Create and return Writing Agent"""
    
    system_message = """You are a professional writer with exceptional skills in creating engaging, 
    well-written content. You excel at writing chapters that are clear, informative, and compelling.
    
    Your writing should:
    1. Be clear and accessible to the target audience
    2. Use appropriate tone and voice
    3. Include relevant examples and case studies
    4. Maintain logical flow and transitions
    5. Be engaging and hold reader interest
    6. Support claims with evidence when needed
    
    Write in markdown format with proper headings, lists, and emphasis.
    Create content that meets the specified word count while being comprehensive."""
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    return agent

