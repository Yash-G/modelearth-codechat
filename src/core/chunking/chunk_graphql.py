"""
graphql language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker


class GraphQLChunker(LanguageChunker):
    """Chunker for GraphQL files."""

    LANGUAGE_EXTENSIONS = ['.graphql', '.gql']
    FUNCTION_PATTERNS = []  # GraphQL doesn't have functions
    CLASS_PATTERNS = []  # GraphQL doesn't have classes
    IMPORT_PATTERNS = []  # GraphQL doesn't have imports

