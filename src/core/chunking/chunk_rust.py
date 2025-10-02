"""
rust language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class RustChunker(LanguageChunker):
    """Chunker for Rust code."""

    LANGUAGE_EXTENSIONS = ['.rs']
    FUNCTION_PATTERNS = [
        r'^\s*fn\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = []  # Rust uses structs and impl
    IMPORT_PATTERNS = [
        r'^\s*use\s+',
        r'^\s*extern\s+crate\s+'
    ]

