"""
haskell language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class HaskellChunker(LanguageChunker):
    """Chunker for Haskell code."""

    LANGUAGE_EXTENSIONS = ['.hs', '.lhs']
    FUNCTION_PATTERNS = [
        r'^\s*(\w+)\s*::',
        r'^\s*(\w+)\s+='
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*module\s+'
    ]

