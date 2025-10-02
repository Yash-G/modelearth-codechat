"""
r language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class RChunker(LanguageChunker):
    """Chunker for R code."""

    LANGUAGE_EXTENSIONS = ['.r', '.R']
    FUNCTION_PATTERNS = [
        r'^\s*(\w+)\s*<-\s*function'
    ]
    CLASS_PATTERNS = []  # R uses S3/S4 classes
    IMPORT_PATTERNS = [
        r'^\s*library\s*\(',
        r'^\s*require\s*\(',
        r'^\s*source\s*\('
    ]

