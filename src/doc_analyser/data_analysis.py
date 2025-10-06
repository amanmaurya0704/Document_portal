import os
import sys
from utils.model_loader import ModelLoader
from logger.custom_logging import CustomLogger
from exception.custom_exception import Document_Portal_Exception
from model.models import *
from langchain.output_parsers import PydanticOutputParser
from langchain.output_parsers import OutputFixingParser
from prompt.prompt_library import PROMPT_REGISTRY

class DocumentAnalyser:
    def __init__(self):
        self.log = CustomLogger().get_logger(__name__)
        try:
            self.loader = ModelLoader()
            self.llm = self.loader.load_llm()

            self.parser = PydanticOutputParser(pydantic_object = MetaData)
            self.fixing_parser = OutputFixingParser.from_llm(parser=self.parser, llm=self.llm)

            self.prompt = PROMPT_REGISTRY["document_analysis"]

            self.log.info("Document Analyser Initialised")


        except Exception as e:
            self.log.error(f"Error in initalising Document Analyzer: {e}")
            raise Document_Portal_Exception("Error in intialising Analyser",sys)

    def analyse_document(self, document_text:str)->dict:
        """
        Analyse the document's text and extract structured meta data and summary.
        """

        try:
            chain = self.prompt | self.llm | self.fixing_parser
            self.log.info("Meta data analysis chain initalised")

            response = chain.invoke({
                "format_instructions": self.parser.get_format_instructions(),
                "document_text": document_text
            })

            self.log.info("meta data extraction successful", keys = list(response.model_dump().keys()))

            return response.model_dump()

        except Exception as e:
            self.log.error(f"Error in analysing metadata: {e}")
            raise Document_Portal_Exception("Error in analysing metadata",sys)

