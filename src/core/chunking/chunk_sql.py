"""
sql language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class SqlChunker(LanguageChunker):
    """Chunker for SQL files."""

    LANGUAGE_EXTENSIONS = ['.sql']
    FUNCTION_PATTERNS = [
        r'^\s*CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)'
    ]
    CLASS_PATTERNS = []  # SQL doesn't have classes
    IMPORT_PATTERNS = []  # SQL doesn't have imports

