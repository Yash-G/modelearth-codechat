"""
less language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker
from .chunk_css import CssChunker


class LessChunker(CssChunker):
    """Chunker for LESS files."""

    LANGUAGE_EXTENSIONS = ['.less']

