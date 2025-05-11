from langchain_community.chat_models import ChatOllama
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.chains import create_history_aware_retriever, create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from chroma_utils import vectorstore
from langchain_core.callbacks import BaseCallbackHandler
from typing import Any, Dict, List
import json
from datetime import datetime

from langchain_core.callbacks import CallbackManager


class DetailedCallbackHandler(BaseCallbackHandler):
    """Подробный обработчик событий для отслеживания работы LangChain."""

    def __init__(self, color_output: bool = True):
        """
        Инициализация обработчика.
        
        Args:
            color_output: Использовать ли цветной вывод в консоль
        """
        super().__init__()
        self.color_output = color_output
        # ANSI коды цветов
        self.colors = {
            'blue': '\033[94m',
            'green': '\033[92m',
            'yellow': '\033[93m',
            'red': '\033[91m',
            'end': '\033[0m'
        } if color_output else dict.fromkeys(['blue', 'green', 'yellow', 'red', 'end'], '')

    def _format_time(self) -> str:
        """Форматирование текущего времени."""
        return datetime.now().strftime("%H:%M:%S")

    def _print_colored(self, text: str, color: str) -> None:
        """Вывод текста с цветом."""
        print(f"{self.colors[color]}{text}{self.colors['end']}")

    def _format_json(self, data: Any) -> str:
        """Форматирование данных в читаемый JSON."""
        return json.dumps(data, ensure_ascii=False, indent=2)

    def on_llm_start(
            self, serialized: Dict[str, Any], prompts: List[str], **kwargs: Any
    ) -> None:
        """Вызывается при старте LLM."""
        self._print_colored(
            f"\n🤖 [{self._format_time()}] Запуск LLM модели {serialized.get('name', 'Unknown')}",
            "blue"
        )
        for i, prompt in enumerate(prompts, 1):
            self._print_colored(f"\nЗапрос {i}:\n{prompt}", "yellow")

    def on_llm_end(self, response: Any, **kwargs: Any) -> None:
        """Вызывается при завершении работы LLM."""
        self._print_colored(
            f"\n✅ [{self._format_time()}] LLM завершила работу\nОтвет: {response}",
            "green"
        )

    def on_llm_error(self, error: BaseException, **kwargs: Any) -> None:
        """Вызывается при ошибке LLM."""
        self._print_colored(
            f"\n❌ [{self._format_time()}] Ошибка LLM: {str(error)}",
            "red"
        )

    def on_chain_start(
            self, serialized: Dict[str, Any], inputs: Dict[str, Any], **kwargs: Any
    ) -> None:
        """Вызывается при старте цепочки."""
        chain_type = serialized.get("name", "Unknown")
        self._print_colored(
            f"\n⛓️ [{self._format_time()}] Запуск цепочки: {chain_type}",
            "blue"
        )
        self._print_colored(
            f"Входные данные:\n{self._format_json(inputs)}",
            "yellow"
        )

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Вызывается при завершении работы цепочки."""
        self._print_colored(
            f"\n🏁 [{self._format_time()}] Цепочка завершила работу",
            "green"
        )
        self._print_colored(
            f"Выходные данные:\n{self._format_json(outputs)}",
            "green"
        )

    def on_chain_error(self, error: BaseException, **kwargs: Any) -> None:
        """Вызывается при ошибке в цепочке."""
        self._print_colored(
            f"\n❌ [{self._format_time()}] Ошибка в цепочке: {str(error)}",
            "red"
        )

    def on_tool_start(
            self, serialized: Dict[str, Any], input_str: str, **kwargs: Any
    ) -> None:
        """Вызывается при старте инструмента."""
        self._print_colored(
            f"\n🔧 [{self._format_time()}] Запуск инструмента: {serialized.get('name', 'Unknown')}",
            "blue"
        )
        self._print_colored(f"Входные данные: {input_str}", "yellow")

    def on_tool_end(self, output: str, **kwargs: Any) -> None:
        """Вызывается при завершении работы инструмента."""
        self._print_colored(
            f"\n✅ [{self._format_time()}] Инструмент завершил работу",
            "green"
        )
        self._print_colored(f"Результат: {output}", "green")

    def on_tool_error(self, error: BaseException, **kwargs: Any) -> None:
        """Вызывается при ошибке инструмента."""
        self._print_colored(
            f"\n❌ [{self._format_time()}] Ошибка инструмента: {str(error)}",
            "red"
        )

    def on_retriever_start(
            self, serialized: Dict[str, Any], query: str, **kwargs: Any
    ) -> None:
        """Вызывается при старте поиска."""
        self._print_colored(
            f"\n🔍 [{self._format_time()}] Начало поиска",
            "blue"
        )
        self._print_colored(f"Запрос: {query}", "yellow")

    def on_retriever_end(self, documents: List[Any], **kwargs: Any) -> None:
        """Вызывается при завершении поиска."""
        self._print_colored(
            f"\n📄 [{self._format_time()}] Найдено документов: {len(documents)}",
            "green"
        )
        for idx, doc in enumerate(documents, 1):
            self._print_colored(
                f"\nДокумент {idx}:",
                "green"
            )
            if hasattr(doc, 'page_content'):
                self._print_colored(
                    f"Содержание: {doc.page_content[:200]}...",
                    "yellow"
                )
            if hasattr(doc, 'metadata'):
                self._print_colored(
                    f"Метаданные:\n{self._format_json(doc.metadata)}",
                    "yellow"
                )

    def on_retriever_error(self, error: BaseException, **kwargs: Any) -> None:
        """Вызывается при ошибке поиска."""
        self._print_colored(
            f"\n❌ [{self._format_time()}] Ошибка поиска: {str(error)}",
            "red"
        )


retriever = vectorstore.as_retriever(search_kwargs={"k": 4})

contextualize_q_system_prompt = (
    "Given a chat history and the latest user question "
    "which might reference context in the chat history, "
    "formulate a standalone question which can be understood "
    "without the chat history. Do NOT answer the question, "
    "just reformulate it if needed and otherwise return it as is."
)

contextualize_q_prompt = ChatPromptTemplate.from_messages([
    ("system", contextualize_q_system_prompt),
    MessagesPlaceholder("chat_history"),
    ("human", "{input}"),
])

qa_prompt = ChatPromptTemplate.from_messages([
    ("system", "You are a helpful AI assistant. Use the following context to answer the user's question."),
    ("system", "Context: {context}"),
    MessagesPlaceholder(variable_name="chat_history"),
    ("human", "{input}")
])


def get_rag_chain(model="gemma3"):
    callbacks = [DetailedCallbackHandler()]
    callback_manager = CallbackManager(callbacks)

    llm = ChatOllama(model=model, callback_manager=callback_manager)
    history_aware_retriever = create_history_aware_retriever(
        llm,
        retriever,
        contextualize_q_prompt
    )
    question_answer_chain = create_stuff_documents_chain(
        llm,
        qa_prompt
    )

    rag_chain = create_retrieval_chain(
        history_aware_retriever,
        question_answer_chain
    )
    return rag_chain
