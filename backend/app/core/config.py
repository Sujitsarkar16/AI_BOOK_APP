"""
Application configuration settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # API Keys
    gemini_api_key: str
    
    # Database
    database_url: str = "sqlite:///./bookforge.db"
    
    # Server
    backend_url: str = "http://localhost:8000"
    frontend_url: str = "http://localhost:8080"
    
    # ChromaDB
    chroma_db_path: str = "./chroma_db"
    
    # Agent Configuration
    max_iterations: int = 5
    agent_timeout: int = 300  # seconds
    
    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()

