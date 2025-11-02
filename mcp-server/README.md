# MCP Server

MCP server for searching through uploaded files. Supports keyword search and regex patterns.

## Setup

```bash
cd mcp-server
uv sync
```

## Running

- To run the MCP server:

    ```bash
    uv run main.py
    ```

- To run the MCP inspector:

    - You will need `bun` and `node` installed. Run:
    ```bash
    bunx modelcontextprotocol/inspector uv run main.py
    ```

Can also be integrated with MCP-compatible clients like Claude Desktop or Cursor.

## Tools

- `search_keywords` - Search for keywords or regex patterns in files
- `list_files` - List all files in the uploads directory

When searching Office documents (PDF, DOCX, etc.), the server automatically uses the parsed `.markdown` version if available.

## Environment Variables

- `SHARED_UPLOADS_DIR` - Path to uploads directory (default: `../shared-uploads`)
