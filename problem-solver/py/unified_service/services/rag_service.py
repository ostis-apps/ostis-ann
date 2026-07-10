"""
RAG service for informational queries using ChromaDB
"""
import logging
from typing import List, Dict
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_classic.chains import create_history_aware_retriever, create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
from database.vector_store import get_retriever
from utils.llm import get_llm
from utils.exceptions import RAGException

logger = logging.getLogger(__name__)


class RAGService:
    """Service for RAG-based question answering"""
    
    def __init__(self):
        self.retriever = get_retriever()
        self._setup_prompts()
        logger.info("RAGService initialized")
    
    def _setup_prompts(self):
        """Setup prompt templates for RAG"""
        
        # Context reformulation prompt
        self.contextualize_q_system_prompt = (
            "Учитывая историю чата и последний вопрос пользователя, "
            "который может ссылаться на контекст в истории чата, "
            "сформулируй самостоятельный вопрос, который можно понять "
            "без истории чата. НЕ отвечай на вопрос, "
            "просто переформулируй его при необходимости или верни как есть."
        )
        
        self.contextualize_q_prompt = ChatPromptTemplate.from_messages([
            ("system", self.contextualize_q_system_prompt),
            MessagesPlaceholder("chat_history"),
            ("human", "{input}"),
        ])
        
        # QA prompt with explicit language instruction
        self.qa_system_prompt = (
            "Ты - эксперт по машинному обучению и искусственному интеллекту. "
            "Используй следующий контекст для ответа на вопрос пользователя. "
            "ВАЖНО: Отвечай на том же языке, на котором задан вопрос. "
            "Если вопрос на русском - отвечай на русском. "
            "Если вопрос на английском - отвечай на английском. "
            "Если ты не знаешь ответа на основе контекста, так и скажи. "
            "Не придумывай информацию. "
            "Используй информацию только из предоставленного контекста."
        )
        
        self.qa_prompt = ChatPromptTemplate.from_messages([
            ("system", self.qa_system_prompt),
            ("system", "Контекст: {context}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}")
        ])
    
    async def answer_query(
        self,
        query: str,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Answer query using RAG
        
        Args:
            query: User query
            chat_history: Chat history for context
            
        Returns:
            Answer string
        """
        logger.info(f"Answering query with RAG: {query[:100]}...")
        
        try:
            # Get LLM
            llm = get_llm(temperature=0.7)
            
            # First, retrieve relevant documents
            from database.vector_store import search_documents
            retrieved_docs = search_documents(query, k=3)
            logger.info(f"Retrieved {len(retrieved_docs)} documents from vector store")
            
            if retrieved_docs:
                # Log detailed information about retrieved documents
                for idx, doc in enumerate(retrieved_docs, 1):
                    source = doc.metadata.get('source', 'unknown')
                    file_id = doc.metadata.get('file_id', 'N/A')
                    chunk_preview = doc.page_content[:150].replace('\n', ' ')
                    logger.info(
                        f"  Document {idx}: source={source}, file_id={file_id}, "
                        f"preview='{chunk_preview}...'"
                    )
                # Log first chunk full content for debugging
                first_chunk = retrieved_docs[0].page_content[:300]
                logger.debug(f"First retrieved chunk full preview: {first_chunk}...")
            
            # Create history-aware retriever
            history_aware_retriever = create_history_aware_retriever(
                llm,
                self.retriever,
                self.contextualize_q_prompt
            )
            
            # Create QA chain
            question_answer_chain = create_stuff_documents_chain(llm, self.qa_prompt)
            
            # Create retrieval chain
            rag_chain = create_retrieval_chain(
                history_aware_retriever,
                question_answer_chain
            )
            
            # Format chat history
            formatted_history = []
            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "human")
                    content = msg.get("content", "")
                    formatted_history.append((role, content))
            
            # Invoke chain
            result = await rag_chain.ainvoke({
                "input": query,
                "chat_history": formatted_history
            })
            
            answer = result.get('answer', '')
            logger.info(f"RAG answer generated (length: {len(answer)} chars)")
            
            # Log retrieved context for debugging
            if 'context' in result:
                context = result['context']
                if isinstance(context, str):
                    context_preview = context[:500]
                    logger.info(f"Context used in answer (first 500 chars): {context_preview}...")
                elif isinstance(context, list):
                    logger.info(f"Context used: {len(context)} document chunks")
                    for idx, ctx_item in enumerate(context[:3], 1):
                        if hasattr(ctx_item, 'page_content'):
                            preview = ctx_item.page_content[:150].replace('\n', ' ')
                            logger.info(f"  Context chunk {idx}: '{preview}...'")
                else:
                    context_str = str(context)[:500]
                    logger.info(f"Context used: {context_str}...")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in RAG service: {e}", exc_info=True)
            raise RAGException(f"Failed to answer query with RAG: {str(e)}")
    
    def answer_query_sync(
        self,
        query: str,
        chat_history: List[Dict[str, str]] = None
    ) -> str:
        """
        Synchronous version of answer_query
        
        Args:
            query: User query
            chat_history: Chat history for context
            
        Returns:
            Answer string
        """
        logger.info(f"Answering query with RAG (sync): {query[:100]}...")
        
        try:
            # Get LLM
            llm = get_llm(temperature=0.7)
            
            # Create history-aware retriever
            history_aware_retriever = create_history_aware_retriever(
                llm,
                self.retriever,
                self.contextualize_q_prompt
            )
            
            # Create QA chain
            question_answer_chain = create_stuff_documents_chain(llm, self.qa_prompt)
            
            # Create retrieval chain
            rag_chain = create_retrieval_chain(
                history_aware_retriever,
                question_answer_chain
            )
            
            # Format chat history
            formatted_history = []
            if chat_history:
                for msg in chat_history:
                    role = msg.get("role", "human")
                    content = msg.get("content", "")
                    formatted_history.append((role, content))
            
            # Invoke chain
            result = rag_chain.invoke({
                "input": query,
                "chat_history": formatted_history
            })
            
            answer = result.get('answer', '')
            logger.info(f"RAG answer generated (length: {len(answer)} chars)")
            
            return answer
            
        except Exception as e:
            logger.error(f"Error in RAG service: {e}", exc_info=True)
            raise RAGException(f"Failed to answer query with RAG: {str(e)}")
