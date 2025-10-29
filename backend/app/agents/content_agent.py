"""
Content Agent - Enhances content with depth and examples
"""
from autogen import ConversableAgent
from app.core.llm_config import get_llm_config

llm_config = get_llm_config()


def create_content_agent(name: str = "content_agent"):
    """Create and return Content Agent"""
    
    system_message = """You are a content enhancement specialist focused on adding depth, examples, and 
    clarity to written content.
    
    Your role is to:
    1. Add concrete examples and case studies
    2. Include relevant statistics and data
    3. Improve transitions between sections
    4. Add depth to complex topics
    5. Ensure content is comprehensive
    6. Add visual aids descriptions (if needed)
    7. Include actionable takeaways
    
    Enhance content while maintaining the original voice and ensuring everything adds value."""
    
    agent = ConversableAgent(
        name=name,
        system_message=system_message,
        llm_config=llm_config,
        human_input_mode="NEVER",
    )
    
    return agent

