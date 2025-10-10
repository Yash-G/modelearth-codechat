"""
commonlisp language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class CommonLispChunker(LanguageChunker):
    """Chunker for Common Lisp code."""

    LANGUAGE_EXTENSIONS = ['.lisp', '.lsp', '.cl']
    FUNCTION_PATTERNS = [
        r'^\s*\(defun\s+(\w+)',
        r'^\s*\(defmethod\s+(\w+)'
    ]
    CLASS_PATTERNS = [
        r'^\s*\(defclass\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*\(require\s+',
        r'^\s*\(asdf:load-system\s+',
        r'^\s*\(ql:quickload\s+'
    ]

