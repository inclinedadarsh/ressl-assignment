from mcp.server.fastmcp import FastMCP
from typing import List
from pathlib import Path
import re

from schema import SearchResponse, FileSearchResult, KeywordMatch

mcp = FastMCP("ressl-assignment-mcp-server")

UPLOADS_DIR = Path(__file__).parent.parent / "shared-uploads"


@mcp.tool()
def search_keywords(
    keywords: List[str], files: List[str] = None, regex: bool = False
) -> SearchResponse:
    """
    Search for given keywords in one or more files.

    Args:
        keywords (List[str]): Keywords to search for.
        files (List[str], optional): Specific files to search in.
            If not provided, the search will include all files in the current directory.
        regex (bool, optional): If True, treat keywords as regex patterns. Defaults to False.

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
                    for keyword in keywords:
                        match_found = False

                        if regex:
                            try:
                                # Compile regex pattern with case-insensitive flag
                                pattern = re.compile(keyword, re.IGNORECASE)
                                if pattern.search(line):
                                    match_found = True
                            except re.error as e:
                                raise ValueError(
                                    f"Invalid regex pattern '{keyword}': {str(e)}"
                                )
                        else:
                            # Simple substring matching (case-insensitive)
                            if keyword.lower() in line.lower():
                                match_found = True

                        if match_found:
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


@mcp.tool()
def list_files() -> List[str]:
    """
    List all files in the shared uploads directory.

    Returns:
        List[str]: A list of file names.
    """
    if not UPLOADS_DIR.exists():
        return []

    return [f.name for f in UPLOADS_DIR.iterdir() if f.is_file()]


if __name__ == "__main__":
    mcp.run()
