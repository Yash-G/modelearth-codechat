"""
dockercompose language chunker.
"""

import re
from typing import Optional, List, Dict, Any
from .base import LanguageChunker
from .chunk_yaml import YamlChunker


class DockerComposeChunker(YamlChunker):
    """Chunker for Docker Compose files."""

    LANGUAGE_EXTENSIONS = ['docker-compose.yml', 'docker-compose.yaml']

