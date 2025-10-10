"""
perl language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class PerlChunker(LanguageChunker):
    """Chunker for Perl code."""

    LANGUAGE_EXTENSIONS = ['.pl', '.pm', '.t']
    FUNCTION_PATTERNS = [
        r'^\s*sub\s+(\w+)'
    ]
    CLASS_PATTERNS = [
        r'^\s*package\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*use\s+',
        r'^\s*require\s+'
    ]

