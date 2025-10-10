"""
java language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import EnhancedLanguageChunker


class JavaChunker(EnhancedLanguageChunker):
    """Chunker for Java code."""

    LANGUAGE_EXTENSIONS = ['.java']
    FUNCTION_PATTERNS = [
        r'^\s*(?:public|private|protected)?\s*(?:static)?\s*(?:\w+(?:<[^>]+>)?|\w+(?:\.\w+)*)\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*(?:public|private|protected)?\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*package\s+'
    ]

