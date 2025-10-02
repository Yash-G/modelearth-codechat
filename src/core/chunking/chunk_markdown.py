"""
markdown language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class MarkdownChunker(LanguageChunker):
    """Chunker for Markdown files."""

    LANGUAGE_EXTENSIONS = ['.md', '.markdown']
    FUNCTION_PATTERNS = []  # Markdown doesn't have functions
    CLASS_PATTERNS = []  # Markdown doesn't have classes
    IMPORT_PATTERNS = []  # Markdown doesn't have imports

