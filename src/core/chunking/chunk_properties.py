"""
properties language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class PropertiesChunker(LanguageChunker):
    """Chunker for Properties files."""

    LANGUAGE_EXTENSIONS = ['.properties']
    FUNCTION_PATTERNS = []  # Properties doesn't have functions
    CLASS_PATTERNS = []  # Properties doesn't have classes
    IMPORT_PATTERNS = []  # Properties doesn't have imports

