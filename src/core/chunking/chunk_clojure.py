"""
clojure language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class ClojureChunker(LanguageChunker):
    """Chunker for Clojure code."""

    LANGUAGE_EXTENSIONS = ['.clj', '.cljs', '.cljc', '.edn']
    FUNCTION_PATTERNS = [
        r'^\s*\(defn\s+(\w+)',
        r'^\s*\(defn-\s+(\w+)'
    ]
    CLASS_PATTERNS = []  # Clojure uses records and types
    IMPORT_PATTERNS = [
        r'^\s*\(ns\s+',
        r'^\s*\(require\s+',
        r'^\s*\(import\s+',
        r'^\s*\(use\s+'
    ]

