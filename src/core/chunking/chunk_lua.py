"""
lua language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class LuaChunker(LanguageChunker):
    """Chunker for Lua code."""

    LANGUAGE_EXTENSIONS = ['.lua']
    FUNCTION_PATTERNS = [
        r'^\s*function\s+(\w+)',
        r'^\s*local\s+function\s+(\w+)'
    ]
    CLASS_PATTERNS = []  # Lua uses tables for OOP
    IMPORT_PATTERNS = [
        r'^\s*require\s+'
    ]

