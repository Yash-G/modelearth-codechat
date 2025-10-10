"""
powershell language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class PowerShellChunker(LanguageChunker):
    """Chunker for PowerShell scripts."""

    LANGUAGE_EXTENSIONS = ['.ps1', '.psm1', '.psd1']
    FUNCTION_PATTERNS = [
        r'^\s*function\s+(\w+)'
    ]
    CLASS_PATTERNS = [
        r'^\s*class\s+(\w+)'
    ]
    IMPORT_PATTERNS = [
        r'^\s*Import-Module\s+',
        r'^\s*using\s+module\s+',
        r'^\s*using\s+namespace\s+'
    ]

