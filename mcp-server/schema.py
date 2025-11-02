from typing import List
from pydantic import BaseModel


class KeywordMatch(BaseModel):
    keyword: str
    line_number: int
    line_content: str


class FileSearchResult(BaseModel):
    file_name: str
    matches: List[KeywordMatch]


class SearchResponse(BaseModel):
    results: List[FileSearchResult]
