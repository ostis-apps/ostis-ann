"""
Configuration for the unified AI service
"""
import os
from typing import Optional, List
from pydantic import Field
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings"""
    
    # API Settings
    app_name: str = "OSTIS ANN Unified Service"
    app_version: str = "1.0.0"
    debug: bool = False
    
    # Server Settings
    host: str = "0.0.0.0"
    port: int = 8000
    
    # LLM Settings - Migration to TinyLlama
    ollama_base_url: str = "http://host.docker.internal:11434"
    llm_model: str = "tinyllama"
    llm_temperature: float = 0.7
    llm_timeout: int = 300
    
    # Database Settings
    sqlite_db_name: str = "unified_rag_app.db"
    
    # ChromaDB Settings
    chroma_persist_directory: str = "./chroma_db"
    embedding_model: str = "all-MiniLM-L6-v2"
    chroma_search_k: int = 2
    
    # Document Processing Settings
    chunk_size: int = 500  # Reduced for better granularity (was 1000)
    chunk_overlap: int = 100  # Reduced proportionally (was 200)
    allowed_file_extensions: list[str] = [".pdf", ".docx", ".html"]
    temp_upload_dir: str = "./temp_uploads"
    bootstrap_documents: List[str] = Field(
        default_factory=lambda: ["./NejronGafGal.pdf"],
        description="Static documents that should be indexed on startup"
    )
    
    # External API Settings
    github_token: Optional[str] = None
    github_pat: Optional[str] = None
    hf_token: Optional[str] = None
    
    # Session Settings
    session_timeout: int = 3600  # 1 hour
    
    # Logging Settings
    log_level: str = "INFO"
    log_file: str = "unified_service.log"
    log_format: str = "%(asctime)s | %(name)s | %(levelname)s | %(message)s"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False


# Global settings instance
settings = Settings()


# Ensure required directories exist
os.makedirs(settings.temp_upload_dir, exist_ok=True)
os.makedirs(settings.chroma_persist_directory, exist_ok=True)

