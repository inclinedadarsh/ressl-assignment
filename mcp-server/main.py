from mcp.server.fastmcp import FastMCP
from typing import List
from pathlib import Path
import re

from schema import SearchResponse, FileSearchResult, KeywordMatch, FileInfo

mcp = FastMCP("ressl-assignment-mcp-server")

UPLOADS_DIR = Path(__file__).parent.parent / "shared-uploads"

# File extensions that get parsed to .markdown files
PARSED_EXTENSIONS = {".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx"}


def resolve_file_name(original_file_name: str) -> tuple[str, str, bool]:
    """
    Resolve the actual file name on disk when user provides an original file name.

    For files with parsed extensions, check if a .markdown version exists.
    If it does, return the .markdown filename. Otherwise, return the original.

    Args:
        original_file_name: The original file name provided by the user

    Returns:
        tuple: (actual_file_name, original_file_name, is_original)
            - actual_file_name: The actual file name on disk to search
            - original_file_name: The original file name (for response)
            - is_original: True if using the original file, False if using .markdown version
    """
    file_path = Path(original_file_name)
    extension = file_path.suffix.lower()

    # If the extension is in the parsed extensions list, check for .markdown version
    if extension in PARSED_EXTENSIONS:
        markdown_file_name = f"{original_file_name}.markdown"
        markdown_path = UPLOADS_DIR / markdown_file_name
        if markdown_path.exists() and markdown_path.is_file():
            return markdown_file_name, original_file_name, False

    # Otherwise, use the original file name
    return original_file_name, original_file_name, True


def get_file_info(file_name: str) -> tuple[str, bool]:
    """
    Determine if a file is original or parsed, and return the original file name.

    Args:
        file_name: The file name to analyze

    Returns:
        tuple: (original_file_name, is_original)
            - original_file_name: The original file name (without .markdown if present)
            - is_original: True if the file is original, False if it's a parsed .markdown file
    """
    if file_name.endswith(".markdown"):
        original_file_name = file_name[:-9]  # Remove .markdown (9 characters)
        return original_file_name, False
    return file_name, True


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
    file_mapping = {}  # Maps actual_file_name -> (original_file_name, is_original)

    if files is not None and len(files) > 0:
        missing_files = []
        for original_file_name in files:
            actual_file_name, resolved_original, is_original = resolve_file_name(
                original_file_name
            )
            file_path = UPLOADS_DIR / actual_file_name
            if not file_path.exists():
                missing_files.append(original_file_name)
            elif file_path.is_file():
                files_to_search.append(actual_file_name)
                file_mapping[actual_file_name] = (resolved_original, is_original)

        if missing_files:
            raise FileNotFoundError(
                f"The following files were not found in '{UPLOADS_DIR}': {', '.join(missing_files)}"
            )
    else:
        files_to_search = [f.name for f in UPLOADS_DIR.iterdir() if f.is_file()]
        # For files found in directory listing, use get_file_info
        for file_name in files_to_search:
            original_file_name, is_original = get_file_info(file_name)
            file_mapping[file_name] = (original_file_name, is_original)

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

        # Get the original file name and is_original flag from the mapping
        original_file_name, is_original = file_mapping.get(
            file_name, get_file_info(file_name)
        )
        results.append(
            FileSearchResult(
                file_name=file_name,
                original_file_name=original_file_name,
                is_original=is_original,
                matches=matches,
            )
        )

    return SearchResponse(results=results)


@mcp.tool()
def list_files() -> List[FileInfo]:
    """
    List all files in the shared uploads directory.

    Returns:
        List[FileInfo]: A list of file information including original file names
            and whether each file is original or parsed.
    """
    if not UPLOADS_DIR.exists():
        return []

    file_infos = []
    for file_path in UPLOADS_DIR.iterdir():
        if file_path.is_file():
            file_name = file_path.name
            original_file_name, is_original = get_file_info(file_name)
            file_infos.append(
                FileInfo(
                    file_name=file_name,
                    original_file_name=original_file_name,
                    is_original=is_original,
                )
            )

    return file_infos


if __name__ == "__main__":
    mcp.run()
