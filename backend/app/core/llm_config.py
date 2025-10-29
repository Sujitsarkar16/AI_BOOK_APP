"""
LLM configuration for AutoGen agents
"""
import google.generativeai as genai
from app.core.config import settings
import logging

logger = logging.getLogger(__name__)

# Configure Gemini API
genai.configure(api_key=settings.gemini_api_key)

# Create LLM configuration for AutoGen
def get_llm_config(model_name: str = "gemini-2.0-flash"):
    """
    Get LLM configuration dictionary for AutoGen
    
    Args:
        model_name: Name of the Gemini model to use
        
    Returns:
        Config dict for AutoGen
    """
    return {
        "model": model_name,
        "api_key": settings.gemini_api_key,
        "api_type": "google",
        "temperature": 0.7,
        "max_tokens": 2000,
    }


def test_gemini_connection() -> bool:
    """
    Test Gemini API connection
    
    Returns:
        True if connection successful, False otherwise
    """
    try:
        model = genai.GenerativeModel('gemini-2.0-flash')
        response = model.generate_content("test")
        return True
    except Exception as e:
        logger.error(f"Gemini connection test failed: {e}")
        return False

