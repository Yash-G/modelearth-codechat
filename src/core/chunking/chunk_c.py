"""
c language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class CChunker(LanguageChunker):
    """Chunker for C code."""

    LANGUAGE_EXTENSIONS = ['.c', '.h']
    FUNCTION_PATTERNS = [
        r'^\s*(?:[\w:]+(?:\s*\*|\s*&)?)\s+(\w+)\s*\([^)]*\)\s*\{?',
        r'^\s*\w+\s*\*\s*(\w+)\s*\([^)]*\)\s*\{?'
    ]
    CLASS_PATTERNS = []  # C doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*#include\s+'
    ]

