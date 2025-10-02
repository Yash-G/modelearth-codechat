"""
scss language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker
from .chunk_css import CssChunker


class ScssChunker(CssChunker):
    """Chunker for SCSS files."""

    LANGUAGE_EXTENSIONS = ['.scss']

