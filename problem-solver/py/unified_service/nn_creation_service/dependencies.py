from .nn_creation_services import RAGService, GenService
from fastapi import Depends
from typing import Annotated
from database.db_utils import get_db_connection
import sqlite3
from typing import Generator

rag_service = RAGService()
gen_service = GenService()

rag_service.seed_database_if_empty()

def get_db() -> Generator:
    """Database dependency for FastAPI"""
    db = get_db_connection()
    try:
        yield db
    finally:
        db.close()

def get_rag():
    return rag_service

def get_gen():
    return gen_service

RAGDep = Annotated[RAGService | None, Depends(get_rag)]

GenerationDep =  Annotated[GenService | None, Depends(get_gen)]

DbDep = Annotated[sqlite3.Connection, Depends(get_db)]