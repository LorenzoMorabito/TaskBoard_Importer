"""Low-level Markdown file reading and hashing."""

import hashlib
import os
from typing import List


def read_markdown_file(path: str, encoding: str = "utf-8") -> List[str]:
    """Read a Markdown file and return lines.
    
    Args:
        path: Path to Markdown file
        encoding: File encoding (default: utf-8)
        
    Returns:
        List of lines from file
        
    Raises:
        FileNotFoundError: If file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    with open(path, "r", encoding=encoding) as f:
        return f.read().splitlines()


def compute_file_hash(path: str) -> str:
    """Compute SHA256 hash of file content.
    
    Args:
        path: Path to file
        
    Returns:
        Hex digest of SHA256 hash
        
    Raises:
        FileNotFoundError: If file does not exist
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()
