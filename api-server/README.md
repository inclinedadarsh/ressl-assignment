# API Server

FastAPI server for uploading and managing files. Automatically parses Office documents (PDF, DOCX, PPTX, etc.) into Markdown format.

## Setup

```bash
cd api-server
uv sync
```

## Running

```bash
uv run uvicorn main:app --reload
```

Server runs on `http://localhost:8000` by default.

## Endpoints

- `GET /health` - Health check
- `POST /upload` - Upload files (up to 10 at once). Office docs are auto-parsed to `.markdown`
- `GET /files` - List all uploaded files

For interactive API docs, visit `http://localhost:8000/docs` once the server is running.

## Environment Variables

- `SHARED_UPLOADS_DIR` - Path to uploads directory (default: `../shared-uploads`)
