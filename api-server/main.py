import shutil
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from schema import UploadFileResponse

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health_check():
    return {"status": "ok"}


ALLOWED_EXTENSIONS = {
    "txt",
    "csv",
    "json",
    "jsonl",
    "xml",
    "html",
    "md",
    "py",
    "js",
    "ts",
    "log",
}


@app.post(
    "/upload", response_model=UploadFileResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(files: list[UploadFile] = File(..., max_items=10)):
    upload_dir = Path("../shared-uploads")
    upload_dir.mkdir(parents=True, exist_ok=True)

    filenames = []
    for file in files:
        # Extract file extension
        file_extension = Path(file.filename).suffix.lstrip(".").lower()

        # Validate file extension
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{file_extension}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        file_path = upload_dir / file.filename
        with open(file_path, "wb") as f:
            shutil.copyfileobj(file.file, f)
            filenames.append(file.filename)
    return UploadFileResponse(filenames=filenames)
