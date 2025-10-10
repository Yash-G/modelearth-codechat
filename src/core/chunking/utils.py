"""
Utility functions for the chunking system.
"""

import os
import re
import hashlib
from typing import Optional, Dict, Any, List
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False


def get_tokenizer():
    """Get the tokenizer instance."""
    if TIKTOKEN_AVAILABLE:
        return tiktoken.get_encoding("cl100k_base")
    return None


def count_tokens(text: str, tokenizer=None) -> int:
    """Count tokens in text."""
    if not isinstance(text, str):
        text = str(text)

    if tokenizer:
        return len(tokenizer.encode(text))
    else:
        # Fallback token counting
        return len(text.split())


def calculate_complexity(content: str) -> float:
    """Calculate content complexity for dynamic chunk sizing."""
    if not content:
        return 0.0

    complexity = 0.0

    # Code complexity metrics
    function_count = len(re.findall(r'\b(def|class|function|fn|public|private|protected)\b', content))
    complexity += function_count * 0.1

    # Control flow complexity
    control_flow = len(re.findall(r'\b(if|for|while|switch|try|catch|except)\b', content))
    complexity += control_flow * 0.05

    return complexity


def get_file_extension(file_path: str) -> str:
    """Get file extension from file path."""
    return Path(file_path).suffix.lower()


def detect_language_from_extension(extension: str) -> str:
    """Detect programming language from file extension."""
    extension_map = {
        # Programming Languages
        '.py': 'python',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.ts': 'typescript',
        '.tsx': 'typescript',
        '.java': 'java',
        '.cpp': 'cpp',
        '.cc': 'cpp',
        '.cxx': 'cpp',
        '.c++': 'cpp',
        '.hpp': 'cpp',
        '.hxx': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.go': 'go',
        '.rs': 'rust',
        '.php': 'php',
        '.rb': 'ruby',
        '.cs': 'csharp',
        '.kt': 'kotlin',
        '.swift': 'swift',
        '.scala': 'scala',
        '.hs': 'haskell',
        '.lua': 'lua',
        '.pl': 'perl',
        '.pm': 'perl',
        '.r': 'r',
        '.R': 'r',
        '.jl': 'julia',
        '.dart': 'dart',
        '.ex': 'elixir',
        '.exs': 'elixir',
        '.erl': 'erlang',
        '.hrl': 'erlang',
        '.clj': 'clojure',
        '.cljs': 'clojure',
        '.cljc': 'clojure',
        '.scm': 'scheme',
        '.ss': 'scheme',
        '.rkt': 'scheme',
        '.lisp': 'commonlisp',
        '.lsp': 'commonlisp',
        '.cl': 'commonlisp',
        '.el': 'emacslisp',
        '.vim': 'vimscript',
        '.vimrc': 'vimscript',
        '.sh': 'shell',
        '.bash': 'shell',
        '.zsh': 'shell',
        '.fish': 'shell',
        '.ksh': 'shell',
        '.ps1': 'powershell',
        '.psm1': 'powershell',
        '.psd1': 'powershell',

        # Configuration and Data Files
        'Dockerfile': 'dockerfile',
        '.dockerfile': 'dockerfile',
        '.yaml': 'yaml',
        '.yml': 'yaml',
        '.json': 'json',
        '.xml': 'xml',
        '.xsd': 'xml',
        '.xsl': 'xml',
        '.xslt': 'xml',
        '.html': 'html',
        '.htm': 'html',
        '.xhtml': 'html',
        '.css': 'css',
        '.scss': 'scss',
        '.less': 'less',
        '.md': 'markdown',
        '.markdown': 'markdown',
        '.tex': 'latex',
        '.latex': 'latex',
        '.bib': 'bibtex',
        '.sql': 'sql',
        '.graphql': 'graphql',
        '.gql': 'graphql',
        'docker-compose.yml': 'dockercompose',
        'docker-compose.yaml': 'dockercompose',
        '.toml': 'toml',
        '.ini': 'ini',
        '.cfg': 'ini',
        '.conf': 'ini',
        '.properties': 'properties'
    }

    return extension_map.get(extension, 'generic')


def get_language_config(language: str) -> Dict[str, Any]:
    """Get configuration for a specific language."""
    configs = {
        'python': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'javascript': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'typescript': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'java': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'cpp': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'c': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'go': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'rust': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'php': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'ruby': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'csharp': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'kotlin': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'swift': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'scala': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'haskell': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'lua': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'perl': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'r': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'julia': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'dart': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'elixir': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'erlang': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'clojure': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'scheme': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'commonlisp': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'emacslisp': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'vimscript': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'shell': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'powershell': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
        'dockerfile': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'yaml': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'json': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'xml': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'html': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'css': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'scss': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'less': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'markdown': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.2},
        'latex': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.2},
        'bibtex': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'sql': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.2},
        'graphql': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.2},
        'dockercompose': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'toml': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'ini': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'properties': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
        'generic': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.0}
    }

    return configs.get(language, configs['generic'])


def get_dynamic_chunk_size(content: str, extension: str) -> tuple[int, int]:
    """Determine optimal chunk size based on content analysis."""
    language = detect_language_from_extension(extension)
    config = get_language_config(language)

    complexity = calculate_complexity(content)

    # Adjust size based on complexity
    base_min = config['min_tokens']
    base_max = config['max_tokens']

    # Higher complexity = smaller chunks for better granularity
    complexity_factor = config['complexity_factor']
    adjusted_min = int(base_min / complexity_factor) if complexity > 0.5 else base_min
    adjusted_max = int(base_max / complexity_factor) if complexity > 0.5 else base_max

    # Ensure reasonable bounds
    adjusted_min = max(128, min(adjusted_min, 512))
    adjusted_max = max(512, min(adjusted_max, 2048))

    return adjusted_min, adjusted_max


def extract_function_name(content: str, language: str) -> Optional[str]:
    """Extract function name from content based on language."""
    patterns = {
        'python': r'def\s+(\w+)\s*\(',
        'javascript': r'function\s+(\w+)\s*\(',
        'typescript': r'function\s+(\w+)\s*\(',
        'java': r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(',
        'cpp': r'\w+\s+\w+\s*\([^)]*\)\s*\{',
        'c': r'\w+\s+\w+\s*\([^)]*\)\s*\{',
        'go': r'func\s+(\w+)\s*\(',
        'rust': r'fn\s+(\w+)\s*\(',
        'php': r'function\s+(\w+)\s*\(',
        'ruby': r'def\s+(\w+)',
        'csharp': r'(?:public|private|protected|internal)?\s*\w+\s+(\w+)\s*\(',
        'kotlin': r'fun\s+(\w+)\s*\(',
        'swift': r'func\s+(\w+)\s*\(',
        'scala': r'def\s+(\w+)\s*\(',
        'haskell': r'(\w+)\s*::',
        'lua': r'function\s+(\w+)',
        'perl': r'sub\s+(\w+)',
        'r': r'(\w+)\s*<-\s*function',
        'julia': r'function\s+(\w+)',
        'dart': r'\w+\s+(\w+)\s*\(',
        'elixir': r'def\s+(\w+)',
        'erlang': r'(\w+)\s*\([^)]*\)\s*->',
        'clojure': r'\(defn\s+(\w+)',
        'scheme': r'\(define\s*\((\w+)',
        'commonlisp': r'\(defun\s+(\w+)',
        'emacslisp': r'\(defun\s+(\w+)',
        'vimscript': r'function!\?\s+(\w+)',
        'shell': r'(\w+)\s*\(\)\s*\{',
        'powershell': r'function\s+(\w+)',
        'sql': r'CREATE\s+(?:OR\s+REPLACE\s+)?FUNCTION\s+(\w+)'
    }

    pattern = patterns.get(language)
    if pattern:
        match = re.search(pattern, content)
        return match.group(1) if match else None

    return None


def extract_class_name(content: str, language: str) -> Optional[str]:
    """Extract class name from content based on language."""
    patterns = {
        'python': r'class\s+(\w+)',
        'javascript': r'class\s+(\w+)',
        'typescript': r'class\s+(\w+)',
        'java': r'(?:public|private|protected)?\s*class\s+(\w+)',
        'cpp': r'class\s+(\w+)',
        'csharp': r'(?:public|private|protected|internal)?\s*class\s+(\w+)',
        'kotlin': r'class\s+(\w+)',
        'swift': r'class\s+(\w+)',
        'scala': r'class\s+(\w+)',
        'haskell': r'class\s+(\w+)',
        'dart': r'class\s+(\w+)',
        'powershell': r'class\s+(\w+)',
        'commonlisp': r'\(defclass\s+(\w+)',
        'julia': r'struct\s+(\w+)'
    }

    pattern = patterns.get(language)
    if pattern:
        match = re.search(pattern, content)
        return match.group(1) if match else None

    return None
