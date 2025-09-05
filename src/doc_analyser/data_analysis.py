import os
import sys
sys.path.insert(0, 'C:\\Users\\amanm\\Downloads\\Machine Learning\\LLMOPS\\Document_portal')
from utils.model_loader import ModelLoader
from logger.custom_logging import CustomLogger
from exception.custom_exception import Document_Portal_Exception
from model.models import *
from langchain.output_parsers import JsonOutputToolsParser
from langchain.output_parsers import OutputFixingParser


class DocumentAnalyser:
    def __init__(self):
        pass

    def analyse_document(self):
        pass
