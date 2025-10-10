"""
swift language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class SwiftChunker(LanguageChunker):
    """Chunker for Swift code."""

    LANGUAGE_EXTENSIONS = ['.swift']
    FUNCTION_PATTERNS = [
        r'^\s*func\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+'
    ]

