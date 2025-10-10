"""
emacslisp language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class EmacsLispChunker(LanguageChunker):
    """Chunker for Emacs Lisp code."""

    LANGUAGE_EXTENSIONS = ['.el', '.elc']
    FUNCTION_PATTERNS = [
        r'^\s*\(defun\s+(\w+)',
        r'^\s*\(defmacro\s+(\w+)'
    ]
    CLASS_PATTERNS = []  # Emacs Lisp doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*\(require\s+',
        r'^\s*\(load\s+',
        r'^\s*\(load-file\s+'
    ]

