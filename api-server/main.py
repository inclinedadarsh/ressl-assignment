import os
import shutil
import tempfile
from pathlib import Path
from fastapi import FastAPI, File, UploadFile, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from markitdown import MarkItDown
from schema import GetFilesResponse, UploadFileResponse, FileInfo

app = FastAPI()

# Get shared uploads directory from environment variable or use default
SHARED_UPLOADS_DIR = Path(os.getenv("SHARED_UPLOADS_DIR", "../shared-uploads"))

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
    "pdf",
    "docx",
    "doc",
    "pptx",
    "ppt",
    "xlsx",
    "xls",
}

# Extensions that need to be parsed through markitdown
PARSEABLE_EXTENSIONS = {
    "pdf",
    "docx",
    "doc",
    "pptx",
    "ppt",
    "xlsx",
    "xls",
}


@app.post(
    "/upload", response_model=UploadFileResponse, status_code=status.HTTP_201_CREATED
)
async def upload_file(files: list[UploadFile] = File(..., max_items=10)):
    upload_dir = SHARED_UPLOADS_DIR
    upload_dir.mkdir(parents=True, exist_ok=True)

    markitdown = MarkItDown()
    file_infos = []

    for file in files:
        # Extract file extension
        file_extension = Path(file.filename).suffix.lstrip(".").lower()

        # Validate file extension
        if file_extension not in ALLOWED_EXTENSIONS:
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail=f"File type '{file_extension}' not allowed. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}",
            )

        # If it's a parseable file type, parse it through markitdown
        if file_extension in PARSEABLE_EXTENSIONS:
            # Save uploaded file temporarily
            with tempfile.NamedTemporaryFile(
                delete=False, suffix=f".{file_extension}"
            ) as tmp_file:
                shutil.copyfileobj(file.file, tmp_file)
                tmp_path = Path(tmp_file.name)

            try:
                # Parse with markitdown
                result = markitdown.convert(str(tmp_path))

                # Extract markdown content - handle different return types
                if hasattr(result, "text_content"):
                    markdown_content = result.text_content
                elif hasattr(result, "markdown"):
                    markdown_content = result.markdown
                elif isinstance(result, str):
                    markdown_content = result
                else:
                    # Try to get string representation
                    markdown_content = str(result)

                # Create parsed filename: filename.extension.markdown
                parsed_filename = f"{file.filename}.markdown"
                parsed_file_path = upload_dir / parsed_filename

                # Save parsed content
                with open(parsed_file_path, "w", encoding="utf-8") as f:
                    f.write(markdown_content)

                file_infos.append(
                    FileInfo(
                        filename=parsed_filename,
                        is_original=False,
                        original_filename=file.filename,
                    )
                )
            except Exception as e:
                # If parsing fails, raise an error
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Failed to parse file '{file.filename}': {str(e)}",
                )
            finally:
                # Clean up temporary file
                if tmp_path.exists():
                    tmp_path.unlink()
        else:
            # Store original file as-is
            file_path = upload_dir / file.filename
            with open(file_path, "wb") as f:
                shutil.copyfileobj(file.file, f)

            file_infos.append(
                FileInfo(
                    filename=file.filename,
                    is_original=True,
                    original_filename=None,
                )
            )

    return UploadFileResponse(files=file_infos)


@app.get("/files", response_model=GetFilesResponse, status_code=status.HTTP_200_OK)
async def get_files():
    if not SHARED_UPLOADS_DIR.exists():
        return GetFilesResponse(files=[])
    upload_dir = SHARED_UPLOADS_DIR
    file_infos = []

    for file_path in upload_dir.glob("*"):
        if not file_path.is_file():
            continue

        filename = file_path.name

        # Check if it's a parsed file (ends with .markdown)
        if filename.endswith(".markdown"):
            # Extract original filename: filename.extension.markdown -> filename.extension
            original_filename = filename[:-9]  # Remove ".markdown" suffix
            file_infos.append(
                FileInfo(
                    filename=filename,
                    is_original=False,
                    original_filename=original_filename,
                )
            )
        else:
            # It's an original file
            file_infos.append(
                FileInfo(
                    filename=filename,
                    is_original=True,
                    original_filename=None,
                )
            )

    return GetFilesResponse(files=file_infos)
