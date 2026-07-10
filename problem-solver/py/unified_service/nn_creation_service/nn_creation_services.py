from langchain_ollama import ChatOllama
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_chroma import Chroma
from langchain_core.prompts import PromptTemplate
from .prompts import GENERATION_PROMPT_TEMPLATE, INITIAL_EXAMPLES
import logging
import os

logger = logging.getLogger(__name__)

class RAGService:
    def __init__(self, db_path: str = './chroma_db'):
        self.db_path = db_path
        self.embeddings = HuggingFaceEmbeddings(model_name = 'all-MiniLM-L6-v2')
        self.vector_db = Chroma(embedding_function= self.embeddings, persist_directory=self.db_path)
    
    def seed_database_if_empty(self):
        if self.vector_db._collection.count() > 0:
            logger.info("База данных уже содержит примеры.")
            return
        
        logger.info('База данных пуста загрузка текстов в базу данных.')
        self.vector_db.add_texts(INITIAL_EXAMPLES)
        logger.info(f'В базу данных добавлено {len(INITIAL_EXAMPLES)} примеров архитектур.')

    def search_similar_code(self, query: str, k: int=1)->str:
        simular_docs = self.vector_db.similarity_search(query, k=k)
        return '\n\n'.join([doc.page_content for doc in simular_docs])

class GenService:
    def __init__(self, model_name: str = 'gemma4:e2b'):
        self.llm = ChatOllama(model=model_name, base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"), timeout = 300)
        self.prompt_template = PromptTemplate(
            input_variables=["context", "target_architecture"],
            template=GENERATION_PROMPT_TEMPLATE
        )
    
    def generate(self, architecture_json: str, context: str)->str:
        final_prompt = self.prompt_template.format(
            context=context, 
            target_architecture = architecture_json
        )
        response = self.llm.invoke(final_prompt)
        return response.content
    