"""
dockerfile language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class DockerfileChunker(LanguageChunker):
    """Chunker for Dockerfile."""

    LANGUAGE_EXTENSIONS = ['Dockerfile', '.dockerfile']
    FUNCTION_PATTERNS = []  # Docker doesn't have functions
    CLASS_PATTERNS = []  # Docker doesn't have classes
    IMPORT_PATTERNS = [
        r'^\s*FROM\s+',
        r'^\s*COPY\s+',
        r'^\s*ADD\s+'
    ]

