"""
yaml language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class YamlChunker(LanguageChunker):
    """Chunker for YAML files."""

    LANGUAGE_EXTENSIONS = ['.yaml', '.yml']
    FUNCTION_PATTERNS = []  # YAML doesn't have functions
    CLASS_PATTERNS = []  # YAML doesn't have classes
    IMPORT_PATTERNS = []  # YAML doesn't have imports

