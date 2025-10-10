"""
julia language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class JuliaChunker(LanguageChunker):
    """Chunker for Julia code."""

    LANGUAGE_EXTENSIONS = ['.jl']
    FUNCTION_PATTERNS = [
        r'^\s*function\s+(\w+)',
        r'^\s*(\w+)\s*\([^)]*\)\s*='
    ]
    CLASS_PATTERNS = [
        r'^\s*struct\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*using\s+',
        r'^\s*import\s+'
    ]

