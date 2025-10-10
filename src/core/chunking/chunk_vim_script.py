"""
vimscript language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class VimScriptChunker(LanguageChunker):
    """Chunker for VimScript code."""

    LANGUAGE_EXTENSIONS = ['.vim', '.vimrc']
    FUNCTION_PATTERNS = [
        r'^\s*function!\?\s+(\w+)'
    ]
    CLASS_PATTERNS = []  # VimScript doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*source\s+',
        r'^\s*runtime\s+'
    ]

