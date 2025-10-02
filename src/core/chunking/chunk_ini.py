"""
ini language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class IniChunker(LanguageChunker):
    """Chunker for INI files."""

    LANGUAGE_EXTENSIONS = ['.ini', '.cfg', '.conf']
    FUNCTION_PATTERNS = []  # INI doesn't have functions
    CLASS_PATTERNS = []  # INI doesn't have classes
    IMPORT_PATTERNS = []  # INI doesn't have imports

