import sys
from dotenv import load_dotenv
import pandas as pd
from logger.custom_logging import CustomLogger
from exception.custom_exception import Document_Portal_Exception
from model.models import *
from prompt.prompt_library import PROMPT_REGISTRY
from utils.model_loader import ModelLoader
from langchain_core.output_parsers import JsonOutputParser
from langchain.output_parsers import OutputFixingParser


class DocumentComparatorLLM:
    def __init__(self):
        load_dotenv()
        self.log = CustomLogger().get_logger(__name__)
        self.loader = ModelLoader()
        self.llm = self.loader.load_llm()
        self.parser = JsonOutputParser(pydantic_object=SummaryResponse)
        self.fix_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)
        self.prompt = PROMPT_REGISTRY[PromptType.DOCUMENT_COMPARISON.value]
        self.chain = self.prompt | self.llm | self.parser
        self.log.info("DocumentComparatorLLM initialized", model=self.llm)

    def compare_documents(self, combined_docs : str)-> pd.DataFrame:
        try:
            inputs = {
                "combined_docs": combined_docs,
                "format_instruction" : self.parser.get_format_instructions()
            }

            self.log.info("starting document comparison",inputs = inputs)
            response = self.chain.invoke(inputs)
            self.log.info("document comparison completed", response = response)
            return self._format_response(response)
        except Exception as e:
            self.log.error(f"Error in comparing documents: {e}")
            raise Document_Portal_Exception("Error in comparing documents",sys)

    def _format_response(self, response_parsed: list[dict]) -> pd.DataFrame:
        try:
            df = pd.DataFrame(response_parsed)
            self.log.info("Resonse formatted successfully", dataframe = df)
            return df
        except Exception as e:
            self.log.error(f"Error in formatting response: {e}")
            raise Document_Portal_Exception("Error in formatting response",sys)