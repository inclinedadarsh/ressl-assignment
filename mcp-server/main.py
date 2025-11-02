from mcp.server.fastmcp import FastMCP
from typing import List
from pathlib import Path

from schema import SearchResponse, FileSearchResult, KeywordMatch

mcp = FastMCP("ressl-assignment-mcp-server")

UPLOADS_DIR = Path(__file__).parent.parent / "shared-uploads"


@mcp.tool()
def search_keywords(keywords: List[str], files: List[str] = None) -> SearchResponse:
    """
    Search for given keywords in one or more files.

    Args:
        keywords (List[str]): Keywords to search for.
        files (List[str], optional): Specific files to search in.
            If not provided, the search will include all files in the current directory.

    Returns:
        SearchResponse: A structured response containing the results of the search.
    """
    if not UPLOADS_DIR.exists():
        raise FileNotFoundError(f"Directory '{UPLOADS_DIR}' does not exist.")

    if not UPLOADS_DIR.is_dir():
        raise NotADirectoryError(f"'{UPLOADS_DIR}' is not a directory.")

    files_to_search = []

    if files is not None and len(files) > 0:
        missing_files = []
        for file_name in files:
            file_path = UPLOADS_DIR / file_name
            if not file_path.exists():
                missing_files.append(file_name)
            elif file_path.is_file():
                files_to_search.append(file_name)

        if missing_files:
            raise FileNotFoundError(
                f"The following files were not found in '{UPLOADS_DIR}': {', '.join(missing_files)}"
            )
    else:
        files_to_search = [f.name for f in UPLOADS_DIR.iterdir() if f.is_file()]

    results = []

    for file_name in files_to_search:
        file_path = UPLOADS_DIR / file_name
        matches = []

        try:
            with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                for line_num, line in enumerate(f, start=1):
                    line_lower = line.lower()
                    for keyword in keywords:
                        if keyword.lower() in line_lower:
                            matches.append(
                                KeywordMatch(
                                    keyword=keyword,
                                    line_number=line_num,
                                    line_content=line.rstrip("\n\r"),
                                )
                            )
        except Exception as e:
            raise IOError(f"Error reading file '{file_name}': {str(e)}")

        results.append(FileSearchResult(file_name=file_name, matches=matches))

    return SearchResponse(results=results)


if __name__ == "__main__":
    mcp.run()
