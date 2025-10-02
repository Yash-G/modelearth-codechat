"""
toml language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class TomlChunker(LanguageChunker):
    """Chunker for TOML files."""

    LANGUAGE_EXTENSIONS = ['.toml']
    FUNCTION_PATTERNS = []  # TOML doesn't have functions
    CLASS_PATTERNS = []  # TOML doesn't have classes
    IMPORT_PATTERNS = []  # TOML doesn't have imports

