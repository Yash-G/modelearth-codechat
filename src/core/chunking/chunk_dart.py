"""
dart language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class DartChunker(LanguageChunker):
    """Chunker for Dart code."""

    LANGUAGE_EXTENSIONS = ['.dart']
    FUNCTION_PATTERNS = [
        r'^\s*\w+\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*export\s+',
        r'^\s*part\s+'
    ]

