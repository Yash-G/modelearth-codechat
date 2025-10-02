"""
Base classes and interfaces for the chunking system.
"""

import re
import hashlib
import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple, Union
from pathlib import Path

try:
    import tiktoken
    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    print("Warning: tiktoken not available. Token counting will be limited.")


class BaseChunker(ABC):
    """Base class for all chunkers providing common functionality."""

    def __init__(self):
        self.tokenizer = tiktoken.get_encoding("cl100k_base") if TIKTOKEN_AVAILABLE else None
        self.chunk_cache = {}

    def count_tokens(self, text: str) -> int:
        """Count tokens in text with caching for performance."""
        if not isinstance(text, str):
            text = str(text)

        # Simple caching for repeated token counts
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.chunk_cache:
            return self.chunk_cache[text_hash]

        if self.tokenizer:
            tokens = len(self.tokenizer.encode(text))
        else:
            # Fallback token counting
            tokens = len(text.split())

        self.chunk_cache[text_hash] = tokens
        return tokens

    def calculate_content_complexity(self, content: str) -> float:
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

    @abstractmethod
    def chunk_content(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Abstract method for chunking content with metadata."""
        pass


class EnhancedChunkMetadata:
    """Enhanced metadata structure for code chunks."""

    def __init__(self):
        self.chunk_id: str = ""
        self.content: str = ""
        self.summary: str = ""
        self.detailed_description: str = ""
        self.chunk_type: str = "code"
        self.language: str = ""
        self.language_detected: str = "unknown"

        # Semantic information
        self.functions: List[str] = []
        self.classes: List[str] = []
        self.methods: List[str] = []
        self.variables: List[str] = []
        self.imports: List[str] = []
        self.exports: List[str] = []
        self.dependencies: List[str] = []

        # Code patterns and analysis
        self.code_patterns: List[str] = []
        self.design_patterns: List[str] = []
        self.frameworks_used: List[str] = []
        self.algorithms: List[str] = []

        # Structural information
        self.start_line: int = 1
        self.end_line: int = 1
        self.line_count: int = 0
        self.content_length: int = 0
        self.token_count: int = 0

        # Complexity metrics
        self.complexity_score: float = 0.0
        self.cyclomatic_complexity: int = 1
        self.nesting_depth: int = 0
        self.function_count: int = 0
        self.class_count: int = 0

        # Semantic types
        self.semantic_types: List[str] = []
        self.primary_purpose: str = ""
        self.secondary_purposes: List[str] = []

        # Quality metrics
        self.has_comments: bool = False
        self.comment_ratio: float = 0.0
        self.has_error_handling: bool = False
        self.has_logging: bool = False
        self.has_validation: bool = False

        # Relationships
        self.parent_chunk_id: Optional[str] = None
        self.child_chunk_ids: List[str] = []
        self.related_chunks: List[str] = []

        # Embeddings
        self.embedding: Optional[List[float]] = None
        self.embedding_model: str = ""
        self.embedding_dimensions: int = 0

        # Metadata
        self.file_path: str = ""
        self.repo_name: str = ""
        self.timestamp: str = ""
        self.version: str = ""
        self.tags: List[str] = []

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'summary': self.summary,
            'detailed_description': self.detailed_description,
            'chunk_type': self.chunk_type,
            'language': self.language,
            'language_detected': self.language_detected,
            'functions': self.functions,
            'classes': self.classes,
            'methods': self.methods,
            'variables': self.variables,
            'imports': self.imports,
            'exports': self.exports,
            'dependencies': self.dependencies,
            'code_patterns': self.code_patterns,
            'design_patterns': self.design_patterns,
            'frameworks_used': self.frameworks_used,
            'algorithms': self.algorithms,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'line_count': self.line_count,
            'content_length': self.content_length,
            'token_count': self.token_count,
            'complexity_score': self.complexity_score,
            'cyclomatic_complexity': self.cyclomatic_complexity,
            'nesting_depth': self.nesting_depth,
            'function_count': self.function_count,
            'class_count': self.class_count,
            'semantic_types': self.semantic_types,
            'primary_purpose': self.primary_purpose,
            'secondary_purposes': self.secondary_purposes,
            'has_comments': self.has_comments,
            'comment_ratio': self.comment_ratio,
            'has_error_handling': self.has_error_handling,
            'has_logging': self.has_logging,
            'has_validation': self.has_validation,
            'parent_chunk_id': self.parent_chunk_id,
            'child_chunk_ids': self.child_chunk_ids,
            'related_chunks': self.related_chunks,
            'embedding': self.embedding,
            'embedding_model': self.embedding_model,
            'embedding_dimensions': self.embedding_dimensions,
            'file_path': self.file_path,
            'repo_name': self.repo_name,
            'timestamp': self.timestamp,
            'version': self.version,
            'tags': self.tags
        }

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata to dictionary format."""
        return {
            'chunk_id': self.chunk_id,
            'content': self.content,
            'summary': self.summary,
            'detailed_description': self.detailed_description,
            'chunk_type': self.chunk_type,
            'language': self.language,
            'language_detected': self.language_detected,
            'functions': self.functions,
            'classes': self.classes,
            'methods': self.methods,
            'variables': self.variables,
            'imports': self.imports,
            'exports': self.exports,
            'dependencies': self.dependencies,
            'code_patterns': self.code_patterns,
            'design_patterns': self.design_patterns,
            'frameworks_used': self.frameworks_used,
            'algorithms': self.algorithms,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'line_count': self.line_count,
            'content_length': self.content_length,
            'token_count': self.token_count,
            'complexity_score': self.complexity_score,
            'cyclomatic_complexity': self.cyclomatic_complexity,
            'nesting_depth': self.nesting_depth,
            'function_count': self.function_count,
            'class_count': self.class_count,
            'semantic_types': self.semantic_types,
            'primary_purpose': self.primary_purpose,
            'secondary_purposes': self.secondary_purposes,
            'has_comments': self.has_comments,
            'comment_ratio': self.comment_ratio,
            'has_error_handling': self.has_error_handling,
            'has_logging': self.has_logging,
            'has_validation': self.has_validation,
            'parent_chunk_id': self.parent_chunk_id,
            'child_chunk_ids': self.child_chunk_ids,
            'related_chunks': self.related_chunks,
            'embedding': self.embedding,
            'embedding_model': self.embedding_model,
            'embedding_dimensions': self.embedding_dimensions,
            'file_path': self.file_path,
            'repo_name': self.repo_name,
            'timestamp': self.timestamp,
            'version': self.version,
            'tags': self.tags
        }

    def _is_function_start(self, line: str) -> bool:
        """Check if line starts a function definition."""
        stripped = line.strip()
        return any(re.search(pattern, stripped) for pattern in self.FUNCTION_PATTERNS)

    def _is_class_start(self, line: str) -> bool:
        """Check if line starts a class definition."""
        stripped = line.strip()
        return any(re.search(pattern, stripped) for pattern in self.CLASS_PATTERNS)

    def _is_import(self, line: str) -> bool:
        """Check if line is an import statement."""
        stripped = line.strip()
        return any(re.search(pattern, stripped) for pattern in self.IMPORT_PATTERNS)

    def _extract_function_name(self, line: str) -> Optional[str]:
        """Extract function name from function definition."""
        for pattern in self.FUNCTION_PATTERNS:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return None

class LanguageChunker(BaseChunker):
    """Base class for language-specific chunkers."""

    # Language-specific patterns that subclasses should override
    LANGUAGE_EXTENSIONS = []
    FUNCTION_PATTERNS = []
    CLASS_PATTERNS = []
    IMPORT_PATTERNS = []

    def __init__(self):
        super().__init__()
        self.language_name = self.__class__.__name__.replace('Chunker', '')

    def _is_function_start(self, line: str) -> bool:
        """Check if line starts a function definition."""
        stripped = line.strip()
        return any(re.search(pattern, stripped) for pattern in self.FUNCTION_PATTERNS)

    def _is_class_start(self, line: str) -> bool:
        """Check if line starts a class definition."""
        stripped = line.strip()
        return any(re.search(pattern, stripped) for pattern in self.CLASS_PATTERNS)

    def _is_import(self, line: str) -> bool:
        """Check if line is an import statement."""
        stripped = line.strip()
        return any(re.search(pattern, stripped) for pattern in self.IMPORT_PATTERNS)

    def _extract_function_name(self, line: str) -> Optional[str]:
        """Extract function name from function definition."""
        for pattern in self.FUNCTION_PATTERNS:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return None

    def _extract_class_name(self, line: str) -> Optional[str]:
        """Extract class name from class definition."""
        for pattern in self.CLASS_PATTERNS:
            match = re.search(pattern, line)
            if match:
                return match.group(1)
        return None

    def chunk_content(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Default pattern-based chunking implementation."""
        chunks = []
        lines = content.split('\n')
        current_chunk_lines = []
        current_tokens = 0
        current_metadata = {
            'semantic_types': [],
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 0,
            'start_line': 1,
            'end_line': 1
        }

        i = 0
        while i < len(lines):
            line = lines[i]
            line_tokens = self.count_tokens(line + '\n')

            # Check for semantic boundaries
            if self._is_function_start(line):
                func_name = self._extract_function_name(line)
                if func_name:
                    # Add function to current chunk metadata
                    if 'function' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('function')
                    current_metadata['functions'].append(func_name)
                    current_metadata['complexity'] += 1

            elif self._is_class_start(line):
                class_name = self._extract_class_name(line)
                if class_name:
                    # Add class to current chunk metadata
                    if 'class' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('class')
                    current_metadata['classes'].append(class_name)
                    current_metadata['complexity'] += 1

            elif self._is_import(line):
                if 'import' not in current_metadata['semantic_types']:
                    current_metadata['semantic_types'].append('import')
                current_metadata['imports'].append(line.strip())

            # Add line to current chunk
            if current_tokens + line_tokens <= max_tokens:
                current_chunk_lines.append(line)
                current_tokens += line_tokens
                current_metadata['end_line'] = i + 1
            else:
                # Chunk is full, save it and start new one
                if current_chunk_lines:
                    chunk_content = '\n'.join(current_chunk_lines)
                    chunk_metadata = current_metadata.copy()
                    chunk_metadata['content'] = chunk_content
                    chunk_metadata['token_count'] = current_tokens
                    chunks.append(chunk_metadata)

                current_chunk_lines = [line]
                current_tokens = line_tokens
                current_metadata = {
                    'semantic_types': [],
                    'functions': [],
                    'classes': [],
                    'imports': [],
                    'complexity': 0,
                    'start_line': i + 1,
                    'end_line': i + 1
                }

            i += 1

        # Add remaining content
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            current_metadata['content'] = chunk_content
            current_metadata['token_count'] = current_tokens
            chunks.append(current_metadata)

        return chunks if chunks else [{
            'content': content,
            'semantic_types': ['code'],
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 0,
            'start_line': 1,
            'end_line': len(lines),
            'token_count': self.count_tokens(content)
        }]


class PineconeChunkMetadata:
    """Pinecone-compatible metadata structure for semantic code chunks."""

    def __init__(self):
        # Core content
        self.content: str = ""  # code or text of the chunk (normalized \n)
        self.embedding: Optional[List[float]] = None  # dense vector for content
        self.summary: Optional[str] = None  # very short 1–3 sentence synopsis for reranking/UI
        self.summary_embedding: Optional[List[float]] = None  # dense vector of summary

        # Identification
        self.chunk_id: str = ""  # stable ID (sha1 format)
        self.chunk_type: str = "fallback"  # function | class | method | module | markdown_section | config_block | cell | html_block | xml_node | fallback
        self.symbol_name: Optional[str] = None  # fully qualified name if available
        self.parents: Optional[List[str]] = None  # enclosing scopes (e.g., class/module names)

        # Content metrics
        self.content_length: int = 0  # characters
        self.token_count: int = 0  # model-token estimate (for batching, budget)

        # File information
        self.file_extension: str = ""  # py, ts, md, …
        self.language: str = ""  # detected python, typescript, markdown, …
        self.file_type: str = "other"  # code | docs | config | notebook | markup | data | other
        self.file_path: str = ""  # repo-root-relative path (e.g., src/foo/bar.py)
        self.line_start: int = 1  # inclusive, 1-based
        self.line_end: int = 1  # inclusive, 1-based

        # Repository information
        self.repository_name: str = ""  # owner/name
        self.latest_commit_id: str = ""  # commit SHA of the build that produced this chunk
        self.timestamp_last_modified: str = ""  # ISO string - file's last modified time at that commit
        self.live: bool = True  # whether this chunk belongs to the current "live" commit of its repo
        self.content_sha: str = ""  # sha256 of content after normalization
        self.ref: str = ""  # resolved git ref (usually same as latest_commit_id)

    def generate_chunk_id(self) -> str:
        """Generate stable chunk ID using sha1(repo|ref|file_path|line_start:line_end|content_sha)."""
        import hashlib

        # Create the ID components
        id_components = [
            self.repository_name,
            self.ref,
            self.file_path,
            f"{self.line_start}:{self.line_end}",
            self.content_sha
        ]

        # Join with | separator and hash
        id_string = "|".join(id_components)
        return hashlib.sha1(id_string.encode()).hexdigest()

    def generate_content_sha(self) -> str:
        """Generate sha256 of content after normalization."""
        import hashlib

        # Normalize content (ensure consistent line endings)
        normalized_content = self.content.replace('\r\n', '\n').replace('\r', '\n')
        return hashlib.sha256(normalized_content.encode()).hexdigest()

    def to_pinecone_dict(self) -> Dict[str, Any]:
        """Convert to Pinecone-compatible dictionary format."""
        # Generate IDs if not set
        if not self.content_sha and self.content:
            self.content_sha = self.generate_content_sha()

        if not self.chunk_id:
            self.chunk_id = self.generate_chunk_id()

        # Build the dictionary
        pinecone_dict = {
            'id': self.chunk_id,
            'values': self.embedding,
            'metadata': {
                'content': self.content,
                'summary': self.summary,
                'chunk_type': self.chunk_type,
                'symbol_name': self.symbol_name,
                'parents': self.parents,
                'content_length': self.content_length,
                'token_count': self.token_count,
                'file_extension': self.file_extension,
                'language': self.language,
                'file_type': self.file_type,
                'file_path': self.file_path,
                'line_start': self.line_start,
                'line_end': self.line_end,
                'repository_name': self.repository_name,
                'latest_commit_id': self.latest_commit_id,
                'timestamp_last_modified': self.timestamp_last_modified,
                'live': self.live,
                'content_sha': self.content_sha,
                'ref': self.ref
            }
        }

        # Add summary embedding if available
        if self.summary_embedding:
            pinecone_dict['metadata']['summary_embedding'] = self.summary_embedding

        return pinecone_dict

    def from_dict(self, data: Dict[str, Any]) -> 'PineconeChunkMetadata':
        """Create PineconeChunkMetadata from dictionary."""
        # Handle both Pinecone format and direct metadata format
        if 'metadata' in data:
            # Pinecone format
            metadata = data['metadata']
            self.embedding = data.get('values')
            self.chunk_id = data.get('id', '')
        else:
            # Direct metadata format
            metadata = data
            self.chunk_id = metadata.get('chunk_id', '')

        self.content = metadata.get('content', '')
        self.summary = metadata.get('summary')
        self.chunk_type = metadata.get('chunk_type', 'fallback')
        self.symbol_name = metadata.get('symbol_name')
        self.parents = metadata.get('parents')
        self.content_length = metadata.get('content_length', 0)
        self.token_count = metadata.get('token_count', 0)
        self.file_extension = metadata.get('file_extension', '')
        self.language = metadata.get('language', '')
        self.file_type = metadata.get('file_type', 'other')
        self.file_path = metadata.get('file_path', '')
        self.line_start = metadata.get('line_start', 1)
        self.line_end = metadata.get('line_end', 1)
        self.repository_name = metadata.get('repository_name', '')
        self.latest_commit_id = metadata.get('latest_commit_id', '')
        self.timestamp_last_modified = metadata.get('timestamp_last_modified', '')
        self.live = metadata.get('live', True)
        self.content_sha = metadata.get('content_sha', '')
        self.ref = metadata.get('ref', '')
        self.summary_embedding = metadata.get('summary_embedding')

        return self

    @classmethod
    def from_enhanced_metadata(cls, enhanced_metadata: 'EnhancedChunkMetadata', repo_info: Dict[str, Any]) -> 'PineconeChunkMetadata':
        """Convert EnhancedChunkMetadata to PineconeChunkMetadata."""
        pinecone_metadata = cls()

        # Core content
        pinecone_metadata.content = enhanced_metadata.content
        pinecone_metadata.embedding = enhanced_metadata.embedding
        pinecone_metadata.summary = enhanced_metadata.summary

        # Generate summary embedding if we have an embedding generator
        if enhanced_metadata.embedding and hasattr(enhanced_metadata, 'embedding_generator'):
            try:
                pinecone_metadata.summary_embedding = enhanced_metadata.embedding_generator.generate_embedding(enhanced_metadata.summary)
            except:
                pass

        # Identification
        pinecone_metadata.chunk_id = enhanced_metadata.chunk_id or ""
        pinecone_metadata.chunk_type = cls._determine_chunk_type(enhanced_metadata)
        pinecone_metadata.symbol_name = cls._extract_symbol_name(enhanced_metadata)
        pinecone_metadata.parents = cls._extract_parents(enhanced_metadata)

        # Content metrics
        pinecone_metadata.content_length = enhanced_metadata.content_length
        pinecone_metadata.token_count = enhanced_metadata.token_count

        # File information
        pinecone_metadata.file_extension = cls._extract_file_extension(enhanced_metadata.file_path)
        pinecone_metadata.language = enhanced_metadata.language
        pinecone_metadata.file_type = cls._determine_file_type(enhanced_metadata.file_path)
        pinecone_metadata.file_path = enhanced_metadata.file_path
        pinecone_metadata.line_start = enhanced_metadata.start_line
        pinecone_metadata.line_end = enhanced_metadata.end_line

        # Repository information
        pinecone_metadata.repository_name = repo_info.get('repository_name', enhanced_metadata.repo_name)
        pinecone_metadata.latest_commit_id = repo_info.get('latest_commit_id', '')
        pinecone_metadata.timestamp_last_modified = repo_info.get('timestamp_last_modified', enhanced_metadata.timestamp)
        pinecone_metadata.live = repo_info.get('live', True)
        pinecone_metadata.ref = repo_info.get('ref', repo_info.get('latest_commit_id', ''))

        return pinecone_metadata

    @staticmethod
    def _determine_chunk_type(enhanced_metadata: 'EnhancedChunkMetadata') -> str:
        """Determine chunk type from enhanced metadata."""
        if 'function' in enhanced_metadata.semantic_types and len(enhanced_metadata.functions) == 1:
            return 'function'
        elif 'class' in enhanced_metadata.semantic_types and len(enhanced_metadata.classes) == 1:
            return 'class'
        elif 'method' in enhanced_metadata.semantic_types:
            return 'method'
        elif enhanced_metadata.file_path.endswith(('.md', '.markdown')):
            return 'markdown_section'
        elif enhanced_metadata.file_path.endswith(('.json', '.yaml', '.yml', '.toml', '.ini')):
            return 'config_block'
        elif enhanced_metadata.file_path.endswith(('.ipynb')):
            return 'cell'
        elif enhanced_metadata.file_path.endswith(('.html', '.htm')):
            return 'html_block'
        elif enhanced_metadata.file_path.endswith(('.xml')):
            return 'xml_node'
        else:
            return 'fallback'

    @staticmethod
    def _extract_symbol_name(enhanced_metadata: 'EnhancedChunkMetadata') -> Optional[str]:
        """Extract fully qualified symbol name."""
        if enhanced_metadata.functions:
            return enhanced_metadata.functions[0]
        elif enhanced_metadata.classes:
            return enhanced_metadata.classes[0]
        elif enhanced_metadata.methods:
            return enhanced_metadata.methods[0]
        return None

    @staticmethod
    def _extract_parents(enhanced_metadata: 'EnhancedChunkMetadata') -> Optional[List[str]]:
        """Extract parent scopes."""
        parents = []
        if enhanced_metadata.classes:
            parents.extend(enhanced_metadata.classes)
        # Could extend with module names, etc.
        return parents if parents else None

    @staticmethod
    def _extract_file_extension(file_path: str) -> str:
        """Extract file extension."""
        if '.' in file_path:
            return file_path.split('.')[-1]
        return ''

    @staticmethod
    def _determine_file_type(file_path: str) -> str:
        """Determine file type from path."""
        ext = file_path.split('.')[-1].lower() if '.' in file_path else ''

        if ext in ['py', 'js', 'ts', 'java', 'cpp', 'c', 'go', 'rs', 'php', 'rb', 'cs', 'scala', 'kt', 'swift', 'hs', 'lua', 'r', 'jl', 'dart', 'ex', 'erl', 'clj', 'scm', 'lisp', 'el', 'vim', 'sh', 'ps1']:
            return 'code'
        elif ext in ['md', 'markdown', 'txt', 'rst']:
            return 'docs'
        elif ext in ['json', 'yaml', 'yml', 'toml', 'ini', 'properties', 'xml', 'cfg']:
            return 'config'
        elif ext in ['ipynb']:
            return 'notebook'
        elif ext in ['html', 'htm', 'css', 'scss', 'less']:
            return 'markup'
        elif ext in ['csv', 'tsv', 'parquet', 'avro', 'orc']:
            return 'data'
        else:
            return 'other'


class EnhancedLanguageChunker(LanguageChunker):
    """Enhanced language chunker with rich metadata extraction."""

    def __init__(self):
        super().__init__()
        self.embedding_generator = None
        try:
            from ..embedding_generator import CodeEmbeddingGenerator
            # Note: API key would need to be provided
            # self.embedding_generator = CodeEmbeddingGenerator(api_key="your-key")
        except ImportError:
            pass

    def generate_chunk_id(self, content: str, file_path: str, start_line: int) -> str:
        """Generate a unique chunk ID."""
        content_hash = hashlib.md5(content.encode()).hexdigest()[:16]
        file_hash = hashlib.md5(file_path.encode()).hexdigest()[:8]
        return f"{file_hash}_{start_line}_{content_hash}"

    def analyze_code_patterns(self, content: str) -> List[str]:
        """Analyze code for common patterns and frameworks."""
        patterns = []

        # Framework detection
        if 'import React' in content or 'from "react"' in content:
            patterns.append('react')
        if 'import Vue' in content or 'from "vue"' in content:
            patterns.append('vue')
        if 'import Angular' in content or '@angular' in content:
            patterns.append('angular')
        if 'express' in content:
            patterns.append('express')
        if 'mongoose' in content or 'mongodb' in content:
            patterns.append('mongodb')
        if 'axios' in content or 'fetch(' in content:
            patterns.append('http-client')

        # Design patterns
        if 'singleton' in content.lower() or 'getInstance' in content:
            patterns.append('singleton')
        if 'factory' in content.lower() or 'Factory' in content:
            patterns.append('factory')
        if 'observer' in content.lower() or 'Observer' in content:
            patterns.append('observer')
        if 'strategy' in content.lower() or 'Strategy' in content:
            patterns.append('strategy')

        # Common algorithms
        if 'sort' in content and ('bubble' in content.lower() or 'quick' in content.lower() or 'merge' in content.lower()):
            patterns.append('sorting-algorithm')
        if 'search' in content and ('binary' in content.lower() or 'linear' in content.lower()):
            patterns.append('search-algorithm')
        if 'hash' in content.lower() and 'table' in content.lower():
            patterns.append('hash-table')
        if 'tree' in content.lower() and ('bst' in content.lower() or 'binary' in content.lower()):
            patterns.append('tree-structure')

        return patterns

    def calculate_complexity_metrics(self, content: str) -> Dict[str, Any]:
        """Calculate various complexity metrics."""
        lines = content.split('\n')

        # Basic metrics
        line_count = len(lines)
        comment_lines = len([line for line in lines if line.strip().startswith('//') or line.strip().startswith('/*')])
        comment_ratio = comment_lines / line_count if line_count > 0 else 0

        # Cyclomatic complexity (simplified)
        cyclo_complexity = 1  # Base complexity
        cyclo_complexity += content.count('if ')
        cyclo_complexity += content.count('else if')
        cyclo_complexity += content.count('for ')
        cyclo_complexity += content.count('while ')
        cyclo_complexity += content.count('case ')
        cyclo_complexity += content.count('catch ')
        cyclo_complexity += content.count('&&')
        cyclo_complexity += content.count('||')

        # Nesting depth
        max_nesting = 0
        current_nesting = 0
        for line in lines:
            indent = len(line) - len(line.lstrip())
            current_nesting = indent // 4  # Assuming 4 spaces per indent
            max_nesting = max(max_nesting, current_nesting)

        return {
            'line_count': line_count,
            'comment_lines': comment_lines,
            'comment_ratio': comment_ratio,
            'cyclomatic_complexity': cyclo_complexity,
            'nesting_depth': max_nesting,
            'has_comments': comment_lines > 0,
            'has_error_handling': 'try' in content or 'catch' in content,
            'has_logging': 'console.log' in content or 'logger' in content.lower(),
            'has_validation': 'validate' in content.lower() or 'isValid' in content
        }

    def generate_smart_summary(self, content: str, metadata: EnhancedChunkMetadata) -> str:
        """Generate a smart, contextual summary of the chunk."""
        summary_parts = []

        # Primary purpose based on semantic types
        if 'function' in metadata.semantic_types and metadata.functions:
            if len(metadata.functions) == 1:
                summary_parts.append(f"Implements {metadata.functions[0]} function")
            else:
                summary_parts.append(f"Contains {len(metadata.functions)} functions: {', '.join(metadata.functions[:3])}")

        if 'class' in metadata.semantic_types and metadata.classes:
            if len(metadata.classes) == 1:
                summary_parts.append(f"Defines {metadata.classes[0]} class")
            else:
                summary_parts.append(f"Defines {len(metadata.classes)} classes: {', '.join(metadata.classes[:2])}")

        if 'import' in metadata.semantic_types:
            summary_parts.append(f"Imports {len(metadata.imports)} dependencies")

        # Add framework/pattern context
        if metadata.frameworks_used:
            summary_parts.append(f"Uses {', '.join(metadata.frameworks_used)}")

        if metadata.design_patterns:
            summary_parts.append(f"Implements {', '.join(metadata.design_patterns)} patterns")

        # Add complexity context
        if metadata.complexity_score > 0.5:
            summary_parts.append("with high complexity")
        elif metadata.cyclomatic_complexity > 5:
            summary_parts.append("with complex control flow")

        # Add quality indicators
        quality_indicators = []
        if metadata.has_error_handling:
            quality_indicators.append("error handling")
        if metadata.has_logging:
            quality_indicators.append("logging")
        if metadata.has_validation:
            quality_indicators.append("validation")

        if quality_indicators:
            summary_parts.append(f"including {', '.join(quality_indicators)}")

        return ' '.join(summary_parts) if summary_parts else "Code implementation with mixed functionality"

    def generate_detailed_description(self, content: str, metadata: EnhancedChunkMetadata) -> str:
        """Generate a detailed description of the chunk's functionality."""
        description_parts = []

        # Analyze the main functionality
        if metadata.functions:
            description_parts.append(f"This code chunk contains {len(metadata.functions)} function(s): {', '.join(metadata.functions)}.")

        if metadata.classes:
            description_parts.append(f"It defines {len(metadata.classes)} class(es): {', '.join(metadata.classes)}.")

        if metadata.methods:
            description_parts.append(f"The chunk includes {len(metadata.methods)} method(s) for object-oriented functionality.")

        # Code patterns and frameworks
        if metadata.code_patterns:
            description_parts.append(f"The implementation uses patterns: {', '.join(metadata.code_patterns)}.")

        if metadata.frameworks_used:
            description_parts.append(f"Built with frameworks/libraries: {', '.join(metadata.frameworks_used)}.")

        # Complexity and quality
        complexity_desc = []
        if metadata.cyclomatic_complexity > 1:
            complexity_desc.append(f"cyclomatic complexity of {metadata.cyclomatic_complexity}")
        if metadata.nesting_depth > 2:
            complexity_desc.append(f"nesting depth of {metadata.nesting_depth}")
        if complexity_desc:
            description_parts.append(f"Code complexity metrics: {', '.join(complexity_desc)}.")

        # Quality features
        quality_features = []
        if metadata.has_comments:
            quality_features.append("documentation")
        if metadata.has_error_handling:
            quality_features.append("error handling")
        if metadata.has_logging:
            quality_features.append("logging capabilities")
        if metadata.has_validation:
            quality_features.append("input validation")

        if quality_features:
            description_parts.append(f"Includes: {', '.join(quality_features)}.")

        # Token and size information
        description_parts.append(f"Spanning lines {metadata.start_line}-{metadata.end_line} with {metadata.token_count} tokens.")

        return ' '.join(description_parts)

    def enhanced_chunk_content(self, content: str, file_path: str = "", min_tokens: int = 256, max_tokens: int = 1024, repo_info: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Enhanced chunking with Pinecone-compatible metadata extraction."""
        if repo_info is None:
            repo_info = {}

        chunks = []
        lines = content.split('\n')

        current_chunk_lines = []
        current_tokens = 0
        current_metadata = EnhancedChunkMetadata()
        current_metadata.start_line = 1

        i = 0
        while i < len(lines):
            line = lines[i]
            line_tokens = self.count_tokens(line + '\n')

            # Enhanced semantic analysis
            if self._is_function_start(line):
                func_name = self._extract_function_name(line)
                if func_name and func_name not in current_metadata.functions:
                    current_metadata.functions.append(func_name)
                    if 'function' not in current_metadata.semantic_types:
                        current_metadata.semantic_types.append('function')

            elif self._is_class_start(line):
                class_name = self._extract_class_name(line)
                if class_name and class_name not in current_metadata.classes:
                    current_metadata.classes.append(class_name)
                    if 'class' not in current_metadata.semantic_types:
                        current_metadata.semantic_types.append('class')

            elif self._is_import(line):
                if 'import' not in current_metadata.semantic_types:
                    current_metadata.semantic_types.append('import')
                current_metadata.imports.append(line.strip())

            # Check if we should create a new chunk
            if current_tokens + line_tokens > max_tokens and current_chunk_lines:
                # Finalize current chunk
                self._finalize_pinecone_chunk(current_chunk_lines, current_metadata, chunks, file_path, repo_info)
                # Start new chunk
                current_chunk_lines = [line]
                current_tokens = line_tokens
                current_metadata = EnhancedChunkMetadata()
                current_metadata.start_line = i + 1
            else:
                current_chunk_lines.append(line)
                current_tokens += line_tokens

            current_metadata.end_line = i + 1
            i += 1

        # Finalize last chunk
        if current_chunk_lines:
            self._finalize_pinecone_chunk(current_chunk_lines, current_metadata, chunks, file_path, repo_info)

        return [chunk.to_pinecone_dict() for chunk in chunks]

    def _finalize_pinecone_chunk(self, chunk_lines: List[str], metadata: EnhancedChunkMetadata, chunks: List[PineconeChunkMetadata], file_path: str, repo_info: Dict[str, Any]):
        """Finalize a chunk with Pinecone-compatible metadata."""
        content = '\n'.join(chunk_lines)

        # Basic content info
        metadata.content = content
        metadata.content_length = len(content)
        metadata.line_count = len(chunk_lines)
        metadata.token_count = self.count_tokens(content)
        metadata.language = self.language_name.lower()

        # File information
        metadata.file_path = file_path
        metadata.timestamp = str(time.time())

        # Generate unique ID
        metadata.chunk_id = self.generate_chunk_id(content, file_path, metadata.start_line)

        # Enhanced analysis
        complexity_metrics = self.calculate_complexity_metrics(content)
        metadata.complexity_score = self.calculate_content_complexity(content)
        metadata.cyclomatic_complexity = complexity_metrics['cyclomatic_complexity']
        metadata.nesting_depth = complexity_metrics['nesting_depth']
        metadata.has_comments = complexity_metrics['has_comments']
        metadata.comment_ratio = complexity_metrics['comment_ratio']
        metadata.has_error_handling = complexity_metrics['has_error_handling']
        metadata.has_logging = complexity_metrics['has_logging']
        metadata.has_validation = complexity_metrics['has_validation']

        # Code pattern analysis
        metadata.code_patterns = self.analyze_code_patterns(content)
        metadata.frameworks_used = [p for p in metadata.code_patterns if p in ['react', 'vue', 'angular', 'express', 'mongodb']]
        metadata.design_patterns = [p for p in metadata.code_patterns if p in ['singleton', 'factory', 'observer', 'strategy']]
        metadata.algorithms = [p for p in metadata.code_patterns if 'algorithm' in p or 'structure' in p]

        # Generate summaries
        metadata.summary = self.generate_smart_summary(content, metadata)
        metadata.detailed_description = self.generate_detailed_description(content, metadata)

        # Determine primary purpose
        if metadata.functions:
            metadata.primary_purpose = "function_implementation"
        elif metadata.classes:
            metadata.primary_purpose = "class_definition"
        elif metadata.imports:
            metadata.primary_purpose = "dependency_management"
        else:
            metadata.primary_purpose = "utility_code"

        # Generate embedding if available
        if self.embedding_generator and content.strip():
            metadata.embedding = self.embedding_generator.generate_embedding(content)
            if metadata.embedding:
                metadata.embedding_dimensions = len(metadata.embedding)
                metadata.embedding_model = "text-embedding-ada-002"

        # Convert to Pinecone format
        pinecone_chunk = PineconeChunkMetadata.from_enhanced_metadata(metadata, repo_info)
        chunks.append(pinecone_chunk)

    def chunk_content(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Default pattern-based chunking implementation."""
        chunks = []
        lines = content.split('\n')
        current_chunk_lines = []
        current_tokens = 0
        current_metadata = {
            'semantic_types': [],
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 0,
            'start_line': 1,
            'end_line': 1
        }

        i = 0
        while i < len(lines):
            line = lines[i]
            line_tokens = self.count_tokens(line + '\n')

            # Check for semantic boundaries
            if self._is_function_start(line):
                func_name = self._extract_function_name(line)
                if func_name:
                    # Add function to current chunk metadata
                    if 'function' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('function')
                    current_metadata['functions'].append(func_name)
                    current_metadata['complexity'] += 1

            elif self._is_class_start(line):
                class_name = self._extract_class_name(line)
                if class_name:
                    # Add class to current chunk metadata
                    if 'class' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('class')
                    current_metadata['classes'].append(class_name)
                    current_metadata['complexity'] += 1

            elif self._is_import(line):
                if 'import' not in current_metadata['semantic_types']:
                    current_metadata['semantic_types'].append('import')
                current_metadata['imports'].append(line.strip())

            # Add line to current chunk
            if current_tokens + line_tokens <= max_tokens:
                current_chunk_lines.append(line)
                current_tokens += line_tokens
                current_metadata['end_line'] = i + 1
            else:
                # Chunk is full, save it and start new one
                if current_chunk_lines:
                    chunk_content = '\n'.join(current_chunk_lines)
                    chunk_metadata = current_metadata.copy()
                    chunk_metadata['content'] = chunk_content
                    chunk_metadata['token_count'] = current_tokens
                    chunks.append(chunk_metadata)

                current_chunk_lines = [line]
                current_tokens = line_tokens
                current_metadata = {
                    'semantic_types': [],
                    'functions': [],
                    'classes': [],
                    'imports': [],
                    'complexity': 0,
                    'start_line': i + 1,
                    'end_line': i + 1
                }

            i += 1

        # Add remaining content
        if current_chunk_lines:
            chunk_content = '\n'.join(current_chunk_lines)
            current_metadata['content'] = chunk_content
            current_metadata['token_count'] = current_tokens
            chunks.append(current_metadata)

        return chunks if chunks else [{
            'content': content,
            'semantic_types': ['code'],
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 0,
            'start_line': 1,
            'end_line': len(lines),
            'token_count': self.count_tokens(content)
        }]


class TreeSitterChunker(BaseChunker):
    """Base class for tree-sitter based chunkers."""

    TREE_SITTER_LANGUAGE = None

    def __init__(self):
        super().__init__()
        self.parser = None
        self._initialize_parser()

    def _initialize_parser(self):
        """Initialize tree-sitter parser for this language."""
        if not self.TREE_SITTER_LANGUAGE:
            return

        try:
            import tree_sitter
            from tree_sitter import Language

            # Try to load the language
            try:
                lang = Language(tree_sitter.language())
                self.parser = tree_sitter.Parser()
                self.parser.set_language(lang)
            except Exception as e:
                print(f"Warning: Could not initialize tree-sitter parser for {self.TREE_SITTER_LANGUAGE}: {e}")
                self.parser = None
        except ImportError:
            print("Warning: tree-sitter not available")
            self.parser = None

    def chunk_with_tree_sitter(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Chunk content using tree-sitter for semantic analysis."""
        if not self.parser:
            # Fallback to pattern-based chunking
            return self._fallback_chunking(content, min_tokens, max_tokens)

        try:
            tree = self.parser.parse(bytes(content, 'utf8'))
            root = tree.root_node

            chunks = []
            current_chunk = ""
            current_tokens = 0
            current_metadata = {
                'semantic_types': [],
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'start_line': 0,
                'end_line': 0
            }

            def process_node(node):
                nonlocal current_chunk, current_tokens, chunks, current_metadata

                node_type = node.type
                node_content = content[node.start_byte:node.end_byte]
                node_tokens = self.count_tokens(node_content)

                if node_type in ['function_definition', 'method_definition', 'function', 'class_definition']:
                    # Extract semantic information
                    if node_type in ['function_definition', 'method_definition', 'function']:
                        func_name = self._extract_function_name_from_node(node, content)
                        if func_name:
                            if 'function' not in current_metadata['semantic_types']:
                                current_metadata['semantic_types'].append('function')
                            current_metadata['functions'].append(func_name)
                            current_metadata['complexity'] += 1

                    elif node_type == 'class_definition':
                        class_name = self._extract_class_name_from_node(node, content)
                        if class_name:
                            if 'class' not in current_metadata['semantic_types']:
                                current_metadata['semantic_types'].append('class')
                            current_metadata['classes'].append(class_name)
                            current_metadata['complexity'] += 1

                # Add content to current chunk
                if current_tokens + node_tokens <= max_tokens:
                    current_chunk += node_content
                    current_tokens += node_tokens
                else:
                    # Save current chunk and start new one
                    if current_chunk:
                        chunk_metadata = current_metadata.copy()
                        chunk_metadata['content'] = current_chunk
                        chunk_metadata['token_count'] = current_tokens
                        chunks.append(chunk_metadata)

                    current_chunk = node_content
                    current_tokens = node_tokens
                    current_metadata = {
                        'semantic_types': [],
                        'functions': [],
                        'classes': [],
                        'imports': [],
                        'complexity': 0,
                        'start_line': 0,
                        'end_line': 0
                    }

            # Process all nodes
            def walk_tree(node):
                process_node(node)
                for child in node.children:
                    walk_tree(child)

            walk_tree(root)

            # Add remaining content
            if current_chunk:
                chunk_metadata = current_metadata.copy()
                chunk_metadata['content'] = current_chunk
                chunk_metadata['token_count'] = current_tokens
                chunks.append(chunk_metadata)

            return chunks if chunks else [{
                'content': content,
                'semantic_types': ['code'],
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'start_line': 1,
                'end_line': len(content.split('\n')),
                'token_count': self.count_tokens(content)
            }]

        except Exception as e:
            print(f"Warning: Tree-sitter chunking failed: {e}")
            return self._fallback_chunking(content, min_tokens, max_tokens)

    def _extract_function_name_from_node(self, node, content: str) -> Optional[str]:
        """Extract function name from tree-sitter node."""
        # Default implementation - subclasses should override
        return None

    def _extract_class_name_from_node(self, node, content: str) -> Optional[str]:
        """Extract class name from tree-sitter node."""
        # Default implementation - subclasses should override
        return None

    def _fallback_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Fallback pattern-based chunking."""
        # Default implementation - subclasses should override
        return [{
            'content': content,
            'semantic_types': ['code'],
            'functions': [],
            'classes': [],
            'imports': [],
            'complexity': 0,
            'start_line': 1,
            'end_line': len(content.split('\n')),
            'token_count': self.count_tokens(content)
        }]
