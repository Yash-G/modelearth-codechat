"""
ruby language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class RubyChunker(LanguageChunker):
    """Chunker for Ruby code."""

    LANGUAGE_EXTENSIONS = ['.rb', '.rbw']
    FUNCTION_PATTERNS = [
        r'^\s*def\s+(\w+)'
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*require\s+',
        r'^\s*require_relative\s+',
        r'^\s*load\s+'
    ]

