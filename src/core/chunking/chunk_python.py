"""
python language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import EnhancedLanguageChunker


class PythonChunker(EnhancedLanguageChunker):
    """Chunker for Python code."""

    LANGUAGE_EXTENSIONS = ['.py', '.pyw', '.pyi']
    FUNCTION_PATTERNS = [
        r'^\s*def\s+(\w+)\s*\(',
        r'^\s*async\s+def\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*from\s+'
    ]

    def _get_indent_level(self, line: str) -> int:
        """Get indentation level of Python line."""
        return len(line) - len(line.lstrip())

