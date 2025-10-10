"""
css language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class CssChunker(LanguageChunker):
    """Chunker for CSS files."""

    LANGUAGE_EXTENSIONS = ['.css']
    FUNCTION_PATTERNS = []  # CSS doesn't have functions
    CLASS_PATTERNS = []  # CSS doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*@import\s+'
    ]

