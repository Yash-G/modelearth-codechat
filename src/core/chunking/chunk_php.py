"""
php language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class PhpChunker(LanguageChunker):
    """Chunker for PHP code."""

    LANGUAGE_EXTENSIONS = ['.php', '.phtml', '.php3', '.php4', '.php5', '.php7']
    FUNCTION_PATTERNS = [
        r'^\s*function\s+(\w+)\s*\('
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*use\s+',
        r'^\s*require\s+',
        r'^\s*require_once\s+',
        r'^\s*include\s+',
        r'^\s*include_once\s+'
    ]

