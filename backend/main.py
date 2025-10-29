"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.database import init_db
from app.api.routes import books, chapters, chat, websocket, export, ideas
from app.core.config import settings
# Import models to ensure they're registered with SQLAlchemy
from app.models import book, chapter, source, agent_log
import logging

# Configure logging with structured format option
from app.utils.logger import setup_logging
import os

# Use JSON logging in production if STUCTURED_LOGS env var is set
use_json_logs = os.getenv("STRUCTURED_LOGS", "false").lower() == "true"
setup_logging(log_level="INFO", use_json=use_json_logs)

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events"""
    # Startup
    logger.info("Initializing database...")
    init_db()
    logger.info("Database initialized")
    yield
    # Shutdown
    logger.info("Shutting down...")


# Create FastAPI app
app = FastAPI(title="BookForge AI Backend", version="1.0.0", lifespan=lifespan)

# Configure CORS - Allow all localhost ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8081",
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080",
        "http://127.0.0.1:8081",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8080",
    ],
    allow_credentials=False,  # Set to False to avoid wildcard issues
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["*"],
)

# Include routers
app.include_router(books.router)
app.include_router(chapters.router)
app.include_router(chat.router)
app.include_router(websocket.router)
app.include_router(export.router)
app.include_router(ideas.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {"message": "BookForge AI Backend API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

