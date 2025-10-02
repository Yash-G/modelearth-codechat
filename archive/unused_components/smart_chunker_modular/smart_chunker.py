"""
Main SmartChunker class that orchestrates all language-specific chunkers.
"""

import os
import re
import hashlib
from typing import Optional, List, Dict, Any, Tuple, Union
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

from ..chunking.base import BaseChunker, EnhancedLanguageChunker
from ..chunking.utils import (
    get_tokenizer,
    count_tokens,
    get_dynamic_chunk_size,
    detect_language_from_extension,
    get_language_config
)

# Import all language chunkers
from ..chunking.chunk_python import PythonChunker
from ..chunking.chunk_javascript import JavaScriptChunker
from ..chunking.chunk_typescript import TypeScriptChunker
from ..chunking.chunk_java import JavaChunker
from ..chunking.chunk_cpp import CppChunker
from ..chunking.chunk_c import CChunker
from ..chunking.chunk_go import GoChunker
from ..chunking.chunk_rust import RustChunker
from ..chunking.chunk_php import PhpChunker
from ..chunking.chunk_ruby import RubyChunker
from ..chunking.chunk_csharp import CSharpChunker
from ..chunking.chunk_kotlin import KotlinChunker
from ..chunking.chunk_swift import SwiftChunker
from ..chunking.chunk_scala import ScalaChunker
from ..chunking.chunk_haskell import HaskellChunker
from ..chunking.chunk_lua import LuaChunker
from ..chunking.chunk_perl import PerlChunker
from ..chunking.chunk_r import RChunker
from ..chunking.chunk_julia import JuliaChunker
from ..chunking.chunk_dart import DartChunker
from ..chunking.chunk_elixir import ElixirChunker
from ..chunking.chunk_erlang import ErlangChunker
from ..chunking.chunk_clojure import ClojureChunker
from ..chunking.chunk_scheme import SchemeChunker
from ..chunking.chunk_common_lisp import CommonLispChunker
from ..chunking.chunk_emacs_lisp import EmacsLispChunker
from ..chunking.chunk_vim_script import VimScriptChunker
from ..chunking.chunk_shell import ShellChunker
from ..chunking.chunk_powershell import PowerShellChunker
from ..chunking.chunk_dockerfile import DockerfileChunker
from ..chunking.chunk_yaml import YamlChunker
from ..chunking.chunk_json import JsonChunker
from ..chunking.chunk_xml import XmlChunker
from ..chunking.chunk_html import HtmlChunker
from ..chunking.chunk_css import CssChunker
from ..chunking.chunk_scss import ScssChunker
from ..chunking.chunk_less import LessChunker
from ..chunking.chunk_markdown import MarkdownChunker
from ..chunking.chunk_latex import LatexChunker
from ..chunking.chunk_bibtex import BibtexChunker
from ..chunking.chunk_sql import SqlChunker
from ..chunking.chunk_graphql import GraphQLChunker
from ..chunking.chunk_dockercompose import DockerComposeChunker
from ..chunking.chunk_toml import TomlChunker
from ..chunking.chunk_ini import IniChunker
from ..chunking.chunk_properties import PropertiesChunker
from ..chunking.chunk_generic import GenericChunker

try:
    from ..embedding_generator import EmbeddingGenerator
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("Warning: EmbeddingGenerator not available. Semantic boost will be disabled.")


class SmartChunker(BaseChunker):
    """
    Main chunking orchestrator that supports all tree-sitter languages
    and provides semantic-aware chunking with metadata extraction.
    """

    def __init__(self, embedding_generator=None, max_workers=4):
        super().__init__()

        # Initialize tokenizer
        self.tokenizer = get_tokenizer()

        # Initialize embedding generator
        self.embedding_generator = embedding_generator
        self.max_workers = max_workers

        # Language chunker registry
        self.chunkers = {}
        self._initialize_chunkers()

        # Tree-sitter parsers (if available)
        self.parsers = {}
        self._initialize_tree_sitter()

        # Chunk cache for performance
        self.chunk_cache = {}

    def _initialize_chunkers(self):
        """Initialize all language-specific chunkers."""
        # Programming Languages
        self.chunkers.update({
            'python': PythonChunker(),
            'javascript': JavaScriptChunker(),
            'typescript': TypeScriptChunker(),
            'java': JavaChunker(),
            'cpp': CppChunker(),
            'c': CChunker(),
            'go': GoChunker(),
            'rust': RustChunker(),
            'php': PhpChunker(),
            'ruby': RubyChunker(),
            'csharp': CSharpChunker(),
            'kotlin': KotlinChunker(),
            'swift': SwiftChunker(),
            'scala': ScalaChunker(),
            'haskell': HaskellChunker(),
            'lua': LuaChunker(),
            'perl': PerlChunker(),
            'r': RChunker(),
            'julia': JuliaChunker(),
            'dart': DartChunker(),
            'elixir': ElixirChunker(),
            'erlang': ErlangChunker(),
            'clojure': ClojureChunker(),
            'scheme': SchemeChunker(),
            'commonlisp': CommonLispChunker(),
            'emacslisp': EmacsLispChunker(),
            'vimscript': VimScriptChunker(),
            'shell': ShellChunker(),
            'powershell': PowerShellChunker(),

            # Configuration and Data Files
            'dockerfile': DockerfileChunker(),
            'yaml': YamlChunker(),
            'json': JsonChunker(),
            'xml': XmlChunker(),
            'html': HtmlChunker(),
            'css': CssChunker(),
            'scss': ScssChunker(),
            'less': LessChunker(),
            'markdown': MarkdownChunker(),
            'latex': LatexChunker(),
            'bibtex': BibtexChunker(),
            'sql': SqlChunker(),
            'graphql': GraphQLChunker(),
            'dockercompose': DockerComposeChunker(),
            'toml': TomlChunker(),
            'ini': IniChunker(),
            'properties': PropertiesChunker(),

            # Generic fallback
            'generic': GenericChunker()
        })

    def _initialize_tree_sitter(self):
        """Initialize tree-sitter parsers for supported languages."""
        try:
            import tree_sitter
            from tree_sitter import Language

            # Language mappings for tree-sitter
            tree_sitter_languages = {
                '.py': ('tree_sitter_python', 'python'),
                '.js': ('tree_sitter_javascript', 'javascript'),
                '.jsx': ('tree_sitter_javascript', 'javascript'),
                '.ts': ('tree_sitter_typescript', 'typescript'),
                '.tsx': ('tree_sitter_typescript', 'typescript'),
                '.java': ('tree_sitter_java', 'java'),
                '.go': ('tree_sitter_go', 'go'),
                '.rs': ('tree_sitter_rust', 'rust'),
                '.php': ('tree_sitter_php', 'php'),
                '.rb': ('tree_sitter_ruby', 'ruby'),
                '.c': ('tree_sitter_c', 'c'),
                '.cpp': ('tree_sitter_cpp', 'cpp'),
                '.cs': ('tree_sitter_c_sharp', 'csharp'),
                '.scala': ('tree_sitter_scala', 'scala'),
                '.swift': ('tree_sitter_swift', 'swift'),
                '.kt': ('tree_sitter_kotlin', 'kotlin'),
                '.hs': ('tree_sitter_haskell', 'haskell'),
                '.lua': ('tree_sitter_lua', 'lua'),
                '.r': ('tree_sitter_r', 'r'),
                '.jl': ('tree_sitter_julia', 'julia'),
                '.dart': ('tree_sitter_dart', 'dart'),
                '.ex': ('tree_sitter_elixir', 'elixir'),
                '.erl': ('tree_sitter_erlang', 'erlang'),
                '.clj': ('tree_sitter_clojure', 'clojure'),
                '.scm': ('tree_sitter_scheme', 'scheme'),
                '.lisp': ('tree_sitter_commonlisp', 'commonlisp'),
                '.el': ('tree_sitter_emacs_lisp', 'emacslisp'),
                '.vim': ('tree_sitter_vim', 'vimscript'),
                '.sh': ('tree_sitter_bash', 'shell'),
                '.ps1': ('tree_sitter_powershell', 'powershell'),
                '.yaml': ('tree_sitter_yaml', 'yaml'),
                '.json': ('tree_sitter_json', 'json'),
                '.xml': ('tree_sitter_xml', 'xml'),
                '.html': ('tree_sitter_html', 'html'),
                '.css': ('tree_sitter_css', 'css'),
                '.scss': ('tree_sitter_scss', 'scss'),
                '.less': ('tree_sitter_less', 'less'),
                '.md': ('tree_sitter_markdown', 'markdown'),
                '.tex': ('tree_sitter_latex', 'latex'),
                '.sql': ('tree_sitter_sql', 'sql'),
                '.graphql': ('tree_sitter_graphql', 'graphql'),
                '.toml': ('tree_sitter_toml', 'toml'),
                '.ini': ('tree_sitter_ini', 'ini'),
                '.properties': ('tree_sitter_properties', 'properties')
            }

            for ext, (module_name, lang_name) in tree_sitter_languages.items():
                try:
                    module = __import__(module_name, fromlist=[lang_name])
                    lang = getattr(module, 'language', lambda: None)()
                    if lang:
                        parser = tree_sitter.Parser()
                        parser.set_language(lang)
                        self.parsers[ext] = parser
                except (ImportError, AttributeError) as e:
                    # Tree-sitter language not available, will use pattern-based chunking
                    pass

        except ImportError:
            print("Warning: tree-sitter not available, using pattern-based chunking only")

    def smart_chunk_with_metadata(self, content: str, ext: str, repo_info: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """
        Smart chunking that returns rich metadata along with content.

        Args:
            content: The content to chunk
            ext: File extension (e.g., '.py', '.js')
            repo_info: Repository information for Pinecone metadata

        Returns:
            List of chunk dictionaries with enhanced metadata
        """
        if not content:
            return []

        if repo_info is None:
            repo_info = {}

        # Get dynamic chunk size
        min_tokens, max_tokens = get_dynamic_chunk_size(content, ext)

        # Detect language
        language = detect_language_from_extension(ext)

        # Get appropriate chunker
        chunker = self.chunkers.get(language, self.chunkers['generic'])

        # Check if chunker supports enhanced chunking
        if hasattr(chunker, 'enhanced_chunk_content'):
            # Use enhanced chunking with rich metadata
            try:
                return chunker.enhanced_chunk_content(content, file_path="", min_tokens=min_tokens, max_tokens=max_tokens, repo_info=repo_info)
            except Exception as e:
                print(f"Warning: Enhanced chunking failed for {ext}: {e}")

        # Try tree-sitter first if available
        if ext in self.parsers and hasattr(chunker, 'chunk_with_tree_sitter'):
            try:
                return chunker.chunk_with_tree_sitter(content, min_tokens, max_tokens)
            except Exception as e:
                print(f"Warning: Tree-sitter chunking failed for {ext}: {e}")

        # Fall back to pattern-based chunking
        return chunker.chunk_content(content, min_tokens, max_tokens)

    def smart_chunk_with_legacy_metadata(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """
        Smart chunking that returns legacy metadata format for backward compatibility.

        Args:
            content: The content to chunk
            ext: File extension (e.g., '.py', '.js')

        Returns:
            List of chunk dictionaries with legacy metadata format
        """
        if not content:
            return []

        # Get dynamic chunk size
        min_tokens, max_tokens = get_dynamic_chunk_size(content, ext)

        # Detect language
        language = detect_language_from_extension(ext)

        # Get appropriate chunker
        chunker = self.chunkers.get(language, self.chunkers['generic'])

        # Check if chunker supports enhanced chunking
        if hasattr(chunker, 'enhanced_chunk_content'):
            # Use enhanced chunking but convert to legacy format
            try:
                pinecone_chunks = chunker.enhanced_chunk_content(content, file_path="", min_tokens=min_tokens, max_tokens=max_tokens)
                return self._convert_pinecone_to_legacy(pinecone_chunks)
            except Exception as e:
                print(f"Warning: Enhanced chunking failed for {ext}: {e}")

        # Try tree-sitter first if available
        if ext in self.parsers and hasattr(chunker, 'chunk_with_tree_sitter'):
            try:
                return chunker.chunk_with_tree_sitter(content, min_tokens, max_tokens)
            except Exception as e:
                print(f"Warning: Tree-sitter chunking failed for {ext}: {e}")

        # Fall back to pattern-based chunking
        return chunker.chunk_content(content, min_tokens, max_tokens)

    def _convert_pinecone_to_legacy(self, pinecone_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Convert Pinecone format chunks to legacy format for backward compatibility."""
        legacy_chunks = []

        for pinecone_chunk in pinecone_chunks:
            metadata = pinecone_chunk.get('metadata', {})

            # Convert to legacy format
            legacy_chunk = {
                'content': metadata.get('content', ''),
                'summary': metadata.get('summary', ''),
                'chunk_type': metadata.get('chunk_type', 'code'),
                'language': metadata.get('language', 'unknown'),
                'start_line': metadata.get('line_start', 1),
                'end_line': metadata.get('line_end', 1),
                'token_count': metadata.get('token_count', 0),
                'semantic_types': [],  # Will be populated from other metadata
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0
            }

            # Extract semantic information from Pinecone metadata
            if metadata.get('chunk_type') == 'function' and metadata.get('symbol_name'):
                legacy_chunk['functions'] = [metadata['symbol_name']]
                legacy_chunk['semantic_types'].append('function')
            elif metadata.get('chunk_type') == 'class' and metadata.get('symbol_name'):
                legacy_chunk['classes'] = [metadata['symbol_name']]
                legacy_chunk['semantic_types'].append('class')

            # Add parents if available
            if metadata.get('parents'):
                legacy_chunk['classes'].extend(metadata['parents'])

            legacy_chunks.append(legacy_chunk)

        return legacy_chunks

    def smart_chunk_content(self, content: str, ext: str) -> List[str]:
        """
        Smart chunking that returns content chunks only.

        Args:
            content: The content to chunk
            ext: File extension

        Returns:
            List of content chunks
        """
        chunks_with_metadata = self.smart_chunk_with_metadata(content, ext)
        return [chunk['content'] for chunk in chunks_with_metadata]

    def get_supported_languages(self) -> List[str]:
        """Get list of all supported languages."""
        return list(self.chunkers.keys())

    def get_language_extensions(self, language: str) -> List[str]:
        """Get file extensions for a specific language."""
        chunker = self.chunkers.get(language)
        if chunker and hasattr(chunker, 'LANGUAGE_EXTENSIONS'):
            return chunker.LANGUAGE_EXTENSIONS
        return []

    def chunk(self, file_path: Union[str, Path]) -> List[Dict[str, Any]]:
        """
        Chunk a single file. Main entry point used by ingestion_worker.
        
        Args:
            file_path: Path to the file to chunk
            
        Returns:
            List of chunks with metadata compatible with ingestion_worker
        """
        file_path = Path(file_path)
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # Get file extension for language detection
            ext = file_path.suffix
            
            # Create repository info from file path
            repo_info = {
                'file_path': str(file_path),
                'file_name': file_path.name,
                'extension': ext
            }
            
            # Use the comprehensive chunking system
            chunks = self.smart_chunk_with_metadata(content, ext, repo_info)
            
            # Convert to format expected by ingestion_worker
            formatted_chunks = []
            for chunk in chunks:
                formatted_chunk = {
                    'content': chunk.get('content', ''),
                    'start_line': chunk.get('start_line', 1),
                    'end_line': chunk.get('end_line', 1),
                    'metadata': chunk.get('metadata', {}),
                    'tokens': chunk.get('tokens', 0)
                }
                formatted_chunks.append(formatted_chunk)
                
            return formatted_chunks
            
        except Exception as e:
            print(f"Error chunking file {file_path}: {e}")
            return []

    def batch_chunk_files(self, file_paths: List[str], max_workers: Optional[int] = None, repo_info: Optional[Dict[str, Any]] = None) -> Dict[str, List[Dict[str, Any]]]:
        """
        Batch chunk multiple files in parallel.

        Args:
            file_paths: List of file paths to chunk
            max_workers: Maximum number of worker threads
            repo_info: Repository information for Pinecone metadata

        Returns:
            Dictionary mapping file paths to their chunks
        """
        if max_workers is None:
            max_workers = self.max_workers

        if repo_info is None:
            repo_info = {}

        results = {}

        def process_file(file_path: str) -> Tuple[str, List[Dict[str, Any]]]:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                ext = Path(file_path).suffix
                chunks = self.smart_chunk_with_metadata(content, ext, repo_info)
                return file_path, chunks
            except Exception as e:
                print(f"Error processing {file_path}: {e}")
                return file_path, []

        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = [executor.submit(process_file, file_path) for file_path in file_paths]

            for future in as_completed(futures):
                file_path, chunks = future.result()
                results[file_path] = chunks

        return results

    def chunk_content(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """
        Abstract method implementation for chunking content with enhanced metadata.
        This is the main entry point for chunking any content.

        Args:
            content: The content to chunk
            min_tokens: Minimum tokens per chunk
            max_tokens: Maximum tokens per chunk

        Returns:
            List of chunks with enhanced metadata
        """
        # Use generic extension for content without extension
        return self.smart_chunk_with_metadata(content, '')

    def get_chunking_stats(self) -> Dict[str, Any]:
        """Get statistics about the chunking system."""
        stats = {
            'supported_languages': len(self.chunkers),
            'tree_sitter_languages': len(self.parsers),
            'pattern_based_languages': len(self.chunkers) - len(self.parsers),
            'cache_size': len(self.chunk_cache),
            'embedding_available': EMBEDDING_AVAILABLE
        }

        # Language breakdown
        language_stats = {}
        for lang, chunker in self.chunkers.items():
            extensions = getattr(chunker, 'LANGUAGE_EXTENSIONS', [])
            language_stats[lang] = {
                'extensions': extensions,
                'has_tree_sitter': any(ext in self.parsers for ext in extensions)
            }

        stats['language_details'] = language_stats
        return stats
