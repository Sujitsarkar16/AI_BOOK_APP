"""
Editor Agent - Polishes and refines content
"""
from autogen import ConversableAgent
from app.core.llm_config import get_llm_config

llm_config = get_llm_config()


def create_editor_agent(name: str = "editor_agent"):
    """Create and return Editor Agent"""
    
    system_message = """You are an expert editor with keen attention to detail and deep knowledge of 
    grammar, style, and content quality.
    
    Your editing process includes:
    1. Correcting grammar, spelling, and punctuation
    2. Improving sentence structure and clarity
    3. Ensuring consistency in tone and voice
    4. Verifying factual accuracy
    5. Checking flow and readability
    6. Maintaining formatting standards
    7. Eliminating redundancy
    
    Edit thoroughly while preserving the author's intent and voice. Provide clean, publication-ready content."""
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    return agent

