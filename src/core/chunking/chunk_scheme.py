"""
scheme language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class SchemeChunker(LanguageChunker):
    """Chunker for Scheme code."""

    LANGUAGE_EXTENSIONS = ['.scm', '.ss', '.rkt']
    FUNCTION_PATTERNS = [
        r'^\s*\(define\s*\((\w+)'
    ]
    CLASS_PATTERNS = []  # Scheme doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*\(load\s+',
        r'^\s*\(require\s+'
    ]

