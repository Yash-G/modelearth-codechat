"""
cpp language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class CppChunker(LanguageChunker):
    """Chunker for C++ code."""

    LANGUAGE_EXTENSIONS = ['.cpp', '.cc', '.cxx', '.c++', '.hpp', '.hxx']
    FUNCTION_PATTERNS = [
        r'^\s*(?:[\w:]+(?:<[^>]+>)?(?:\s*\*|\s*&)?)\s+(\w+)\s*\([^)]*\)\s*\{?',
        r'^\s*\w+\s*\*\s*(\w+)\s*\([^)]*\)\s*\{?'
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*#include\s+'
    ]

