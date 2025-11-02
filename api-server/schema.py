from pydantic import BaseModel


class FileInfo(BaseModel):
    filename: str
    is_original: bool
    original_filename: str | None = None


class UploadFileResponse(BaseModel):
    files: list[FileInfo]


class GetFilesResponse(BaseModel):
    files: list[FileInfo]
