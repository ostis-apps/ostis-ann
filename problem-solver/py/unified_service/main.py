"""
Main FastAPI application for the unified OSTIS ANN service

This service unifies:
- Task classification (informational vs build_model)
- RAG service for informational queries (using ChromaDB)
- Model designer service (determines ML model type)
- Code search service (HuggingFace/GitHub)
- Data collection for model building

All models migrated to TinyLlama for consistency
"""
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from config import settings
from utils import setup_logging
from routers import health_router, documents_router, chat_router, dialogs_router
from nn_creation_service.nn_creation_router import router as nn_router
# Setup logging
setup_logging()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    logger.info("=" * 60)
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"LLM Model: {settings.llm_model}")
    logger.info(f"Ollama Base URL: {settings.ollama_base_url}")
    logger.info(f"Database: {settings.sqlite_db_name}")
    logger.info(f"ChromaDB: {settings.chroma_persist_directory}")
    logger.info("=" * 60)
    
    # Initialize services on startup
    try:
        from database import init_database
        init_database()
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
    
    try:
        from database.vector_store import get_vectorstore
        get_vectorstore()
        logger.info("Vector store initialized successfully")
    except Exception as e:
        logger.error(f"Error initializing vector store: {e}")

    try:
        from utils.bootstrap import bootstrap_documents
        await bootstrap_documents()
    except Exception as e:
        logger.error(f"Error during bootstrap documents: {e}")
    
    logger.info(f"{settings.app_name} is ready!")
    
    yield
    
    logger.info(f"Shutting down {settings.app_name}...")


# Create FastAPI app
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Unified AI service for OSTIS ANN project.
    
    Features:
    - Task classification (informational vs build_model)
    - RAG-based Q&A using ChromaDB
    - ML model recommendation (RF, LR, GRB, NN, etc.)
    - Code search on HuggingFace and GitHub
    - Document management and indexing
    
    All LLM operations use TinyLlama for consistency and efficiency.
    """,
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(health_router)
app.include_router(documents_router)
app.include_router(chat_router)
app.include_router(dialogs_router)
app.include_router(nn_router)

logger.info("Routers registered successfully")


if __name__ == "__main__":
    import uvicorn
    
    logger.info(f"Starting server on {settings.host}:{settings.port}")
    
    uvicorn.run(
        "main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower()
    )

