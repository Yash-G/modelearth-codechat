"""
csharp language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class CSharpChunker(LanguageChunker):
    """Chunker for C# code."""

    LANGUAGE_EXTENSIONS = ['.cs']
    FUNCTION_PATTERNS = [
        r'^\s*(?:public|private|protected|internal)?\s*\w+\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*(?:public|private|protected|internal)?\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*using\s+'
    ]

