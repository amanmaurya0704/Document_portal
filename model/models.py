from pydantic import BaseModel, Field, RootModel
from typing import Optional, List, Dict, Any, Union
from enum import Enum

class MetaData(BaseModel):
    Summary: List[str] = Field(default_factory = list, description = "Summary of the Document")
    Title: str
    Author: str
    DateCreated: str
    Publisher: str
    LastModifiedDate:str
    Language: str
    PageCount: Union[int, str]
    SentimentTone :str


class ChangeFormat(BaseModel):
    Page: str
    changes: str


class SummaryResponse(RootModel[list[ChangeFormat]]):
    pass


class PromptType(str,Enum):
    DOCUMENT_ANALYSIS = "document_analysis"
    DOCUMENT_COMPARISON = "document_comparison"
    CONTEXTUALIZE_QUESTION = "contextualize_question"
    CONTEXT_QA = "context_qa"
