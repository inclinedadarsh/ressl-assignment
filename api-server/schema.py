from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    filenames: list[str]


class GetFilesResponse(BaseModel):
    filenames: list[str]
