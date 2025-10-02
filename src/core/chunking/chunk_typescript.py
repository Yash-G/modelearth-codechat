"""
TypeScript language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import EnhancedLanguageChunker


class TypeScriptChunker(EnhancedLanguageChunker):
    """Chunker for TypeScript code."""

    LANGUAGE_EXTENSIONS = ['.ts', '.tsx', '.d.ts']

    # TypeScript supports all JavaScript patterns plus some additional ones
    FUNCTION_PATTERNS = [
        r'^\s*function\s+(\w+)\s*\([^)]*\)',  # function declarations
        r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*(?::\s*[^)]*)?\)\s*(?::\s*\w+(?:<[^>]*>)?)?\s*=>',  # arrow function assignments with TypeScript types
        r'^\s*(?:export\s+)?(?:const|let|var)\s+(\w+)\s*=\s*\([^)]*\)\s*=>',  # arrow function assignments (simpler)
        r'^\s*(?:public|private|protected)?\s*(?:async\s+)?(?:static\s+)?(\w+)\s*\([^)]*(?::\s*[^)]*)?\)\s*(?::\s*\w+(?:<[^>]*>)?)?\s*\{',  # method definitions in classes with TypeScript types
        r'^\s*(?!if|for|while|switch|try|catch|else|do|return|throw|new|typeof|instanceof|delete|void|set|get)\s*(?:public|private|protected)?\s*(?:async\s+)?(\w+)\s*\([^)]*\)\s*\{',  # method definitions (excluding keywords and common patterns)
        r'^\s*(?!if|for|while|switch|try|catch|else|do|return|throw|new|typeof|instanceof|delete|void|set|get)\s*(?:public|private|protected)?\s*(?:static\s+)?(\w+)\s*\([^)]*\)\s*\{',  # static methods (excluding keywords)
    ]
    CLASS_PATTERNS = [
        r'^\s*(?:export\s+)?(?:abstract\s+)?class\s+(\w+)',
        r'^\s*(?:const|let|var)\s+(\w+)\s*=\s*class\s*\{',
        r'^\s*interface\s+(\w+)',
        r'^\s*type\s+(\w+)\s*='
    ]
    IMPORT_PATTERNS = [
        r'^\s*import\s+',
        r'^\s*(?:const|let|var)\s+.*=\s*require\s*\(',
        r'^\s*export\s+'
    ]
