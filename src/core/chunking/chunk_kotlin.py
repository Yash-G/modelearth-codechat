"""
kotlin language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class KotlinChunker(LanguageChunker):
    """Chunker for Kotlin code."""

    LANGUAGE_EXTENSIONS = ['.kt', '.kts']
    FUNCTION_PATTERNS = [
        r'^\s*fun\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*package\s+'
    ]

