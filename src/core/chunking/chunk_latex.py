"""
latex language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class LatexChunker(LanguageChunker):
    """Chunker for LaTeX files."""

    LANGUAGE_EXTENSIONS = ['.tex', '.latex']
    FUNCTION_PATTERNS = []  # LaTeX doesn't have functions
    CLASS_PATTERNS = []  # LaTeX doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*\\input\s*\{',
        r'^\s*\\include\s*\{',
        r'^\s*\\usepackage\s*\{'
    ]

