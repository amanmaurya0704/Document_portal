import os

import json
from dotenv import load_dotenv
from config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from logger.custom_logging import CustomLogger
from exception.custom_exception import Document_Portal_Exception

log = CustomLogger().get_logger(__name__)

class ModelLoader:
    def __init__(self):
        load_dotenv()
        self._validate_env()
        self.config = load_config()
        log.info("Configuration loaded successfully", config_keys = list(self.config.keys()))
        
    def _validate_env(self):
        required_varss = ["GOOGLE_API_KEY", "GROQ_API_KEY"]
        self.api_keys = {key: os.getenv(key) for key in required_varss}
        missing = [k for k,v in self.api_keys.items() if not v]
        if missing:
            log.error("Missing environment variables", missing_vars = missing)
        log.info("Environment variables are validated", available_keys = [k for k in self.api_keys if self.api_keys[k]])

    def load_embedding(self):
        try:
            log.info("Loading embedding model.....")
            model_name = self.config["embedding_model"]["model_name"]
            return GoogleGenerativeAIEmbeddings(model = model_name)
        except:
            log.error("Error in loading embedding model")
            raise Document_Portal_Exception("Failed to load embedding model",sys)

    def load_llm(self):
        llm_block = self.config["llm"]

        log.info("Loading LLM model .....")

        provider_key = os.getenv("LLM_Provider","groq")

        if provider_key not in llm_block:
            log.error("LLM Provider not foundin config", provider = provider_key)
            raise ValueError(f"Provider {provider_key} not found!")
        
        llm_config = llm_block[provider_key]
        provider = llm_config.get("provider")
        model_name = llm_config.get("model_name")
        temperature = llm_config.get("temperature",0.2)
        max_tokens = llm_config.get("max_output_tokens",2048)

        log.info("Loading LLM model", provider = provider, model_name = model_name, temperature = temperature, max_output_tokens = max_tokens)

        if provider == "groq":
            llm = ChatGroq(model_name = model_name, temperature = temperature)
            return llm
        elif provider == "google":
            llm = ChatGoogleGenerativeAI(model_name = model_name, temperature = temperature, max_output_tokens = max_tokens)
            return llm
        else:
            log.error("LLM Provider not found in config", provider = provider_key)
            raise ValueError(f"Provider {provider_key} not found!")
if __name__ == "__main__":
    model_loader = ModelLoader()

    embeddings = model_loader.load_embedding()
    print("Embeddings model loaded: ", embeddings)

    llm = model_loader.load_llm()
    print("LLM model loaded: ", llm)

    result = llm.invoke("Hello")
    print("Result: ", result.content)