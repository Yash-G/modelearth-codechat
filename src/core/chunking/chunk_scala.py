"""
scala language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class ScalaChunker(LanguageChunker):
    """Chunker for Scala code."""

    LANGUAGE_EXTENSIONS = ['.scala', '.sc']
    FUNCTION_PATTERNS = [
        r'^\s*def\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*package\s+'
    ]

