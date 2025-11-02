from pydantic import BaseModel


class UploadFileResponse(BaseModel):
    filenames: list[str]
