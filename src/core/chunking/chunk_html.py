"""
html language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class HtmlChunker(LanguageChunker):
    """Chunker for HTML files."""

    LANGUAGE_EXTENSIONS = ['.html', '.htm', '.xhtml']
    FUNCTION_PATTERNS = []  # HTML doesn't have functions
    CLASS_PATTERNS = []  # HTML doesn't have classes
    IMPORT_PATTERNS = []  # HTML doesn't have imports

