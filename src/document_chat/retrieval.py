import sys
import os
from operator import itemgetter
from langchain_core.messages import BaseMessage
from langchain_core.output_parsers import StrOutputParser
from langchain_community.vectorstores import FAISS
from langchain_core.runnables import RunnablePassthrough
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate
from utils.model_loader import ModelLoader
from logger.custom_logging import CustomLogger
from exception.custom_exception import Document_Portal_Exception
from prompt.prompt_library import PROMPT_REGISTRY
from model.models import PromptType
from typing import List, Optional, Dict,Any


class ConversationalRAG:
    def __init__(self,session_id:str, retriever=None):
        try:
            self.log = CustomLogger().get_logger(__name__)
            self.session_id = session_id
            self.llm = self._load_llm()
            self.contextualize_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXTUALIZE_QUESTION.value]
            self.qa_prompt : ChatPromptTemplate = PROMPT_REGISTRY[PromptType.CONTEXT_QA.value]
            self.retriever = retriever
            self.chain = None
            if self.retriever is not None:
                self._build_lcel_chain()
            self.log.info("Intialised Conversational RAG",session_id = session_id)

        except Exception as e:
            self.log.error("Failed to initalise Converational RAG",error = str(e))
            raise Document_Portal_Exception("Initialisation error in coverationRAG", sys)

        

    def load_retriever_from_faiss(self,
        index_path: str,
        k: int = 5,
        index_name: str = "index",
        search_type: str = "similarity",
        search_kwargs: Optional[Dict[str, Any]] = None,):
        """
        Load a FAISS
        """
        try:
            if not os.path.isdir(index_path):
                raise FileNotFoundError(f"FAISS index directory not found: {index_path}")

            embeddings = ModelLoader().load_embedding()
            vectorstore = FAISS.load_local(
                index_path,
                embeddings,
                index_name=index_name,
                allow_dangerous_deserialization=True,  # ok if you trust the index
            )

            if search_kwargs is None:
                search_kwargs = {"k": k}

            self.retriever = vectorstore.as_retriever(
                search_type=search_type, search_kwargs=search_kwargs
            )
            self._build_lcel_chain()

            self.log.info(
                "FAISS retriever loaded successfully",
                index_path=index_path,
                index_name=index_name,
                k=k,
                session_id=self.session_id,
            )
            return self.retriever

        except Exception as e:
            self.log.error("Failed to invoke ConversationalRAG", error=str(e))
            raise Document_Portal_Exception("Invocation error in ConversationalRAG", sys)


    def invoke(self, user_input:str, chat_history:Optional[List[BaseMessage]] =None )->str:
        try:
            chat_history = chat_history or []
            payload = {"input": user_input, "chat_history": chat_history}
            response = self.chain.invoke(payload)
            if not response:
                self.log.warning("No answer received",session_id = self.session_id)
                return "No answer received"
            self.log.info("Answer generated succesfully successfully", user_iput = user_input, session_id = self.session_id, anser_preview = response[:150])
            return response
        except Exception as e:
            self.log.error("Failed to invoke RAG",error = str(e))
            raise Document_Portal_Exception("Failed to invoke RAG",sys)
        except Exception as e:
            self.log.error("Failed to invoke RAG",error = str(e))
            raise Document_Portal_Exception("Failed to invoke RAG",sys)

    def _load_llm(self):
        try:
            llm = ModelLoader().load_llm()
            if not llm:
                raise ValueError("LLM cannot be None")
            self.log.info("Loaded LLM",class_name = llm.__class__.__name__)
            return llm
        except Exception as e:
            self.log.error("Failed to load LLM",error = str(e))
            raise Document_Portal_Exception("Failed to load LLM",sys)

    @staticmethod
    def _format_docs(docs):
        return "\n\n".join(d.page_content for d in docs)


    def _build_lcel_chain(self):
        try:
            question_rewritter = ({"input":itemgetter("input"),
            "chat_history": itemgetter("chat_history")}
            | self.contextualize_prompt 
            | self.llm 
            | StrOutputParser()
            )

            retrieve_docs = question_rewritter | self.retriever |self._format_docs
            self.chain = (
                {
                    "context" : retrieve_docs,
                    "input": itemgetter("input"),
                    "chat_history": itemgetter("chat_history")

                }
            | self.qa_prompt 
            | self.llm 
            | StrOutputParser()
            )
            self.log.info("Built LELC chain",session_id = self.session_id)
        except Exception as e:
            self.log.error("Failed to build LELC chain",error = str(e))
            raise Document_Portal_Exception("Failed to build LELC chain",sys)