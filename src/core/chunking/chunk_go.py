"""
go language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import EnhancedLanguageChunker


class GoChunker(EnhancedLanguageChunker):
    """Chunker for Go code."""

    LANGUAGE_EXTENSIONS = ['.go']
    FUNCTION_PATTERNS = [
        r'^\s*func\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = []  # Go doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*package\s+'
    ]

