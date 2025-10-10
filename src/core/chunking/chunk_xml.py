"""
xml language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class XmlChunker(LanguageChunker):
    """Chunker for XML files."""

    LANGUAGE_EXTENSIONS = ['.xml', '.xsd', '.xsl', '.xslt']
    FUNCTION_PATTERNS = []  # XML doesn't have functions
    CLASS_PATTERNS = []  # XML doesn't have classes
    IMPORT_PATTERNS = []  # XML doesn't have imports

