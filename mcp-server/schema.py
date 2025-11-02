from typing import List
from pydantic import BaseModel


class KeywordMatch(BaseModel):
    keyword: str
    line_number: int
    line_content: str


class FileSearchResult(BaseModel):
    file_name: str
    original_file_name: str
    is_original: bool
    matches: List[KeywordMatch]


class FileInfo(BaseModel):
    file_name: str
    original_file_name: str
    is_original: bool


class SearchResponse(BaseModel):
    results: List[FileSearchResult]
