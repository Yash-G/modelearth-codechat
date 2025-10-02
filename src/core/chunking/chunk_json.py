"""
json language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class JsonChunker(LanguageChunker):
    """Chunker for JSON files."""

    LANGUAGE_EXTENSIONS = ['.json']
    FUNCTION_PATTERNS = []  # JSON doesn't have functions
    CLASS_PATTERNS = []  # JSON doesn't have classes
    IMPORT_PATTERNS = []  # JSON doesn't have imports

