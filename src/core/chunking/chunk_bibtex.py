"""
bibtex language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class BibtexChunker(LanguageChunker):
    """Chunker for BibTeX files."""

    LANGUAGE_EXTENSIONS = ['.bib']
    FUNCTION_PATTERNS = []  # BibTeX doesn't have functions
    CLASS_PATTERNS = []  # BibTeX doesn't have classes
    IMPORT_PATTERNS = []  # BibTeX doesn't have imports

