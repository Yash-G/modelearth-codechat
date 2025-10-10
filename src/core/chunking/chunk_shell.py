"""
shell language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class ShellChunker(LanguageChunker):
    """Chunker for shell scripts."""

    LANGUAGE_EXTENSIONS = ['.sh', '.bash', '.zsh', '.fish', '.ksh']
    FUNCTION_PATTERNS = [
        r'^\s*(\w+)\s*\(\)\s*\{'
    ]
    CLASS_PATTERNS = []  # Shell doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*source\s+',
        r'^\s*\.\s+'
    ]

