"""
erlang language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class ErlangChunker(LanguageChunker):
    """Chunker for Erlang code."""

    LANGUAGE_EXTENSIONS = ['.erl', '.hrl']
    FUNCTION_PATTERNS = [
        r'^\s*(\w+)\s*\([^)]*\)\s*->'
    ]
    CLASS_PATTERNS = []  # Erlang uses modules
    IMPORT_PATTERNS = [
        r'^\s*-include\s*\(',
        r'^\s*-include_lib\s*\('
    ]

