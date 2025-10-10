"""
javascript language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import EnhancedLanguageChunker


class JavaScriptChunker(EnhancedLanguageChunker):
    """Chunker for JavaScript code."""

    LANGUAGE_EXTENSIONS = ['.js', '.jsx', '.mjs', '.cjs']
    FUNCTION_PATTERNS = [
        r'^\s*function\s+(\w+)\s*\([^)]*\)',  # function declarations
        r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*(?:\([^)]*\)\s*=>|function\s*\([^)]*\))',  # function expressions and arrow functions
        r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>',  # arrow function assignments
        r'^\s*(?!if|for|while|switch|try|catch|else|do)(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',  # method definitions (excluding keywords)
        r'^\s*(?:public|private|protected)?\s*(?!if|for|while|switch|try|catch|else|do)(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',  # class methods with access modifiers
    ]
    CLASS_PATTERNS = [
        r'^\s*(?:export\s+)?(?:default\s+)?class\s+(\w+)',
        r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*class\s*\{'
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*(?:const|let|var)\s+.*=\s*require\s*\(',
        r'^\s*export\s+'
    ]

