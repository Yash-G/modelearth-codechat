"""
elixir language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class ElixirChunker(LanguageChunker):
    """Chunker for Elixir code."""

    LANGUAGE_EXTENSIONS = ['.ex', '.exs']
    FUNCTION_PATTERNS = [
        r'^\s*def\s+(\w+)',
        r'^\s*defp\s+(\w+)'
    ]
    CLASS_PATTERNS = []  # Elixir uses modules
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*alias\s+',
        r'^\s*require\s+',
        r'^\s*use\s+'
    ]

