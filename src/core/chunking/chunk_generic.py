"""
generic language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class GenericChunker(LanguageChunker):
    """Generic chunker for unsupported languages."""

    LANGUAGE_EXTENSIONS = []  # Catch-all
    FUNCTION_PATTERNS = [
        r'\bfunction\s+(\w+)\b',
        r'\bdef\s+(\w+)\b',
        r'\bfn\s+(\w+)\b',
        r'\bsub\s+(\w+)\b'
    ]
    CLASS_PATTERNS = [
        r'\bclass\s+(\w+)\b'
    ]
    IMPORT_PATTERNS = [
        r'\bimport\b',
        r'\brequire\b',
        r'\binclude\b',
        r'\busing\b',
        r'\buse\b'
    ]

