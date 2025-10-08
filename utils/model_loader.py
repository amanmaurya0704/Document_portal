import os
import sys
from pathlib import Path

# Add the src and utils directory to the Python path
utils_path = Path(__file__).parent
src_path = utils_path.parent / "src"
sys.path.insert(0, str(src_path))
sys.path.insert(0, str(utils_path))

import json
from dotenv import load_dotenv
from config_loader import load_config
from langchain_google_genai import GoogleGenerativeAIEmbeddings, ChatGoogleGenerativeAI
from langchain_groq import ChatGroq
from logger.custom_logging import CustomLogger
from exception.custom_exception import Document_Portal_Exception

log = CustomLogger().get_logger(__name__)

class ApiKeyManager:
    REQUIRED_KEYS = ["GROQ_API_KEY", "GOOGLE_API_KEY"]

    def __init__(self):
        self.api_keys = {}
        raw = os.getenv("API_KEYS")

        if raw:
            try:
                parsed = json.loads(raw)
                if not isinstance(parsed, dict):
                    raise ValueError("API_KEYS is not a valid JSON object")
                self.api_keys = parsed
                log.info("Loaded API_KEYS from ECS secret")
            except Exception as e:
                log.warning("Failed to parse API_KEYS as JSON", error=str(e))

        # Fallback to individual env vars
        for key in self.REQUIRED_KEYS:
            if not self.api_keys.get(key):
                env_val = os.getenv(key)
                if env_val:
                    self.api_keys[key] = env_val
                    log.info(f"Loaded {key} from individual env var")

        # Final check
        missing = [k for k in self.REQUIRED_KEYS if not self.api_keys.get(k)]
        if missing:
            log.error("Missing required API keys", missing_keys=missing)
            raise Document_Portal_Exception("Missing API keys", sys)

        log.info("API keys loaded", keys={k: v[:6] + "..." for k, v in self.api_keys.items()})


    def get(self, key: str) -> str:
        val = self.api_keys.get(key)
        if not val:
            raise KeyError(f"API key for {key} is missing")
        return val


class ModelLoader:
    def __init__(self):
        if os.getenv("ENV", "local").lower() != "production":
            load_dotenv()
            log.info("Running in LOCAL mode: .env loaded")
        else:
            log.info("Running in PRODUCTION mode")

        self.api_key_mgr = ApiKeyManager()
        self.config = load_config()
        log.info("YAML config loaded", config_keys=list(self.config.keys()))

        
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

        provider_key = os.getenv("LLM_Provider","google")

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
            llm = ChatGoogleGenerativeAI(model = model_name, temperature = temperature, max_output_tokens = max_tokens)
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