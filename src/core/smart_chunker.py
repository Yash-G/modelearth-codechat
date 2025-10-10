import os
import tree_sitter
from tree_sitter import Language
import re
import json
import yaml
import pandas as pd
from pathlib import Path
import tiktoken
import uuid
import importlib
import hashlib
from typing import Optional, List, Dict, Any, Tuple
from collections import defaultdict
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

# Import numpy conditionally
try:
    import numpy as np
    NUMPY_AVAILABLE = True
except ImportError:
    np = None
    NUMPY_AVAILABLE = False
    print("Warning: numpy not available. Some features will be limited.")

# Import embedding generator for semantic analysis
try:
    from ..embedding_generator import EmbeddingGenerator
    EMBEDDING_AVAILABLE = True
except ImportError:
    EMBEDDING_AVAILABLE = False
    print("Warning: EmbeddingGenerator not available. Semantic boost will be disabled.")

def cosine_similarity_simple(vec1, vec2):
    """Simple cosine similarity implementation"""
    if not NUMPY_AVAILABLE:
        return 0.0

    vec1 = np.array(vec1)
    vec2 = np.array(vec2)

    dot_product = np.dot(vec1, vec2)
    norm1 = np.linalg.norm(vec1)
    norm2 = np.linalg.norm(vec2)

    if norm1 == 0 or norm2 == 0:
        return 0.0

    return dot_product / (norm1 * norm2)


class SmartChunker:
    """Enhanced chunker with advanced features for optimal RAG performance"""

    def __init__(self, embedding_generator=None, max_workers=4):
        self.parsers = {}
        # Supported extensions from rag_ingestion_pipeline
        self.code_exts = {".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".cpp", ".c", ".cs", ".go", ".rb", ".php", ".rs", ".swift", ".kt", ".kts", ".scala", ".cjs", ".mjs", ".ipynb", ".sh"}
        self.markdown_exts = {".md", ".mdx", ".txt", ".rst", ".adoc"}
        self.data_exts = {".csv", ".tsv", ".xls", ".xlsx", ".parquet", ".feather", ".h5", ".hdf5", ".pkl"}
        self.json_exts = {".json", ".yaml", ".yml", ".jsonl", ".webmanifest"}
        self.image_exts = {".png", ".jpg", ".jpeg", ".gif", ".svg", ".psd", ".bmp", ".tiff", ".ico"}
        self.font_exts = {".woff", ".woff2", ".ttf", ".otf", ".eot"}
        self.binary_exts = {".map", ".zip", ".exe", ".bin", ".dll", ".so", ".o", ".gz"}
        self.minified_exts = {".min.js", ".min.css", ".js.map", ".css.map"}
        self.docs_exts = {".pdf", ".docx", ".doc", ".rtf", ".odt"}
        self.html_exts = {".html", ".htm", ".xhtml"}
        self.css_exts = {".css", ".scss", ".sass", ".less"}
        self.xml_exts = {".xml", ".xsd", ".xsl"}

        # Initialize embedding generator for semantic analysis
        self.embedding_generator = embedding_generator
        self.semantic_patterns_cache = {}  # Cache for semantic pattern embeddings

        # Performance and caching
        self.max_workers = max_workers
        self.chunk_cache = {}  # Cache for expensive computations
        self.file_hashes = {}  # Track file changes for incremental updates

        # Cross-file relationship tracking
        self.relationship_graph = defaultdict(list)
        self.import_graph = defaultdict(list)

        # Dynamic chunk sizing parameters
        self.dynamic_sizing = {
            'code': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.5},
            'documentation': {'min_tokens': 512, 'max_tokens': 2048, 'complexity_factor': 1.2},
            'data': {'min_tokens': 128, 'max_tokens': 512, 'complexity_factor': 1.0},
            'web': {'min_tokens': 256, 'max_tokens': 1024, 'complexity_factor': 1.3}
        }

        # Mapping of extensions to tree-sitter module names for dynamic path resolution
        self.languages_modules = {
            '.py': ('tree_sitter_python', 'python'),
            '.js': ('tree_sitter_javascript', 'javascript'),
            '.jsx': ('tree_sitter_javascript', 'javascript'),
            '.cjs': ('tree_sitter_javascript', 'javascript'),
            '.ts': ('tree_sitter_typescript', 'typescript'),
            '.java': ('tree_sitter_java', 'java'),
            '.cpp': ('tree_sitter_cpp', 'cpp'),
            '.c': ('tree_sitter_c', 'c'),
            '.cs': ('tree_sitter_c_sharp', 'c_sharp'),
            '.go': ('tree_sitter_go', 'go'),
            '.rb': ('tree_sitter_ruby', 'ruby'),
            '.php': ('tree_sitter_php', 'php'),
            '.rs': ('tree_sitter_rust', 'rust'),
            '.swift': ('tree_sitter_swift', 'swift'),
            '.html': ('tree_sitter_html', 'html'),
            '.css': ('tree_sitter_css', 'css'),
            '.xml': ('tree_sitter_xml', 'xml'),
            '.scss': ('tree_sitter_css', 'css'),  # Same as CSS
            '.sh': ('tree_sitter_bash', 'bash'),
        }

        # Dynamically resolve paths and initialize parsers
        self.languages = {}
        for ext, (module_name, lang_name) in self.languages_modules.items():
            try:
                module = importlib.import_module(module_name)
                # Common paths for .so file: try 'languages.so' or 'tree_sitter_<lang>.so'
                possible_paths = [
                    os.path.join(os.path.dirname(module.__file__), 'languages.so'),
                    os.path.join(os.path.dirname(module.__file__), f'tree_sitter_{lang_name}.so'),
                    os.path.join(os.path.dirname(module.__file__), f'{lang_name}.so'),
                    os.path.join(os.path.dirname(module.__file__), '_binding.abi3.so'),
                ]
                lang_path = None
                for path in possible_paths:
                    if os.path.exists(path):
                        lang_path = path
                        break
                if lang_path:
                    # For tree-sitter 0.25+, use module.language() if available
                    try:
                        lang_capsule = module.language()
                        lang = tree_sitter.Language(lang_capsule)
                    except AttributeError:
                        # Some modules may have different attribute names
                        lang_attr = getattr(module, 'language_' + lang_name, None)
                        if lang_attr:
                            lang_capsule = lang_attr()
                            lang = tree_sitter.Language(lang_capsule)
                        else:
                            print(f"Warning: Could not find language attribute for {module_name}")
                            lang = None
                    if lang:
                        self.languages[ext] = lang
                else:
                    print(f"Warning: Could not find .so file for {module_name} at expected paths: {possible_paths}")
            except ImportError as e:
                print(f"Warning: Could not import {module_name}: {e}")
            except Exception as e:
                print(f"Warning: Error loading Tree-sitter for {ext}: {e}")

        # Initialize parsers
        for ext, lang in self.languages.items():
            try:
                parser = tree_sitter.Parser(lang)
                self.parsers[ext] = parser
            except Exception as e:
                print(f"Warning: Could not initialize parser for {ext}: {e}")

        # Tokenizer for token counting
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.MAX_TOKENS = 8192

    def count_tokens(self, text):
        """Count tokens in text with caching for performance"""
        if isinstance(text, dict) and 'content' in text:
            text = text['content']
        elif not isinstance(text, str):
            text = str(text)

        # Simple caching for repeated token counts
        text_hash = hashlib.md5(text.encode()).hexdigest()
        if text_hash in self.chunk_cache:
            return self.chunk_cache[text_hash]

        tokens = len(self.tokenizer.encode(text))
        self.chunk_cache[text_hash] = tokens
        return tokens

    def calculate_content_complexity(self, content: str, ext: str) -> float:
        """Calculate content complexity for dynamic chunk sizing"""
        if not content:
            return 0.0

        complexity = 0.0

        # Code complexity metrics
        if ext in self.code_exts:
            # Function/class density
            function_count = len(re.findall(r'\b(def|class|function|fn|public|private|protected)\b', content))
            complexity += function_count * 0.1

            # Control flow complexity
            control_flow = len(re.findall(r'\b(if|for|while|switch|try|catch|except)\b', content))
            complexity += control_flow * 0.05

            # Import density
            import_count = len(re.findall(r'\b(import|from|require|include)\b', content))
            complexity += import_count * 0.03

            # Nesting depth (rough estimate)
            nesting_indicators = len(re.findall(r'\s{4,}|\t', content))
            complexity += min(nesting_indicators * 0.01, 0.2)

        # Documentation complexity
        elif ext in self.markdown_exts:
            # Header density
            headers = len(re.findall(r'^#{1,6}\s', content, re.MULTILINE))
            complexity += headers * 0.05

            # Link density
            links = len(re.findall(r'\[.*?\]\(.*?\)', content))
            complexity += links * 0.02

            # Code block density
            code_blocks = len(re.findall(r'```.*?```', content, re.DOTALL))
            complexity += code_blocks * 0.1

        # Data complexity
        elif ext in self.data_exts or ext in self.json_exts:
            # Size-based complexity
            size_factor = min(len(content) / 10000, 1.0)
            complexity += size_factor * 0.3

            # Structure complexity (JSON)
            if ext in self.json_exts:
                try:
                    data = json.loads(content) if content.strip().startswith('{') else yaml.safe_load(content)
                    complexity += self._calculate_json_complexity(data) * 0.2
                except:
                    pass

        return min(complexity, 2.0)  # Cap at 2.0

    def _calculate_json_complexity(self, data, depth=0):
        """Calculate complexity of JSON/YAML structure"""
        if depth > 5:  # Prevent infinite recursion
            return 0.1

        complexity = 0.0
        if isinstance(data, dict):
            complexity += len(data) * 0.1
            for value in data.values():
                complexity += self._calculate_json_complexity(value, depth + 1)
        elif isinstance(data, list):
            complexity += len(data) * 0.05
            if data:
                complexity += self._calculate_json_complexity(data[0], depth + 1)
        return complexity

    def get_dynamic_chunk_size(self, content: str, ext: str) -> Tuple[int, int]:
        """Determine optimal chunk size based on content analysis"""
        content_type = self._get_content_type_from_extension(ext)
        config = self.dynamic_sizing.get(content_type, self.dynamic_sizing['code'])

        complexity = self.calculate_content_complexity(content, ext)

        # Adjust size based on complexity
        base_min = config['min_tokens']
        base_max = config['max_tokens']

        # Higher complexity = smaller chunks for better granularity
        complexity_factor = config['complexity_factor']
        adjusted_min = int(base_min / complexity_factor) if complexity > 0.5 else base_min
        adjusted_max = int(base_max / complexity_factor) if complexity > 0.5 else base_max

        # Ensure reasonable bounds
        adjusted_min = max(128, min(adjusted_min, 512))
        adjusted_max = max(512, min(adjusted_max, self.MAX_TOKENS))

        return adjusted_min, adjusted_max

    def smart_chunk_content(self, content: str, ext: str) -> List[str]:
        """Smart chunking with dynamic sizing and semantic boundaries"""
        if not content:
            return []

        min_tokens, max_tokens = self.get_dynamic_chunk_size(content, ext)

        # Use semantic boundaries for chunking
        if ext in self.code_exts:
            return self._semantic_code_chunking(content, ext, min_tokens, max_tokens)
        elif ext in self.markdown_exts:
            return self._semantic_markdown_chunking(content, min_tokens, max_tokens)
        elif ext in self.html_exts:
            return self._semantic_html_chunking(content, min_tokens, max_tokens)
        else:
            return self._fallback_chunking(content, min_tokens, max_tokens)

    def smart_chunk_with_metadata(self, content: str, ext: str) -> List[Dict[str, Any]]:
        """Smart chunking that returns rich metadata along with content"""
        if not content:
            return []

        min_tokens, max_tokens = self.get_dynamic_chunk_size(content, ext)

        # Try Tree-sitter first for languages with good support, otherwise use pattern-based
        try:
            # Use pattern-based chunking for languages with robust patterns
            if ext in ['.py', '.js', '.ts', '.jsx', '.tsx', '.java', '.go', '.rs', '.php', '.rb']:
                return self._pattern_based_chunking_with_metadata(content, ext, min_tokens, max_tokens)
            # Use Tree-sitter for other languages
            elif ext in self.code_exts:
                return self._semantic_code_chunking_with_metadata(content, ext, min_tokens, max_tokens)
            elif ext in self.markdown_exts:
                return self._semantic_markdown_chunking_with_metadata(content, min_tokens, max_tokens)
            elif ext in self.html_exts:
                return self._semantic_html_chunking_with_metadata(content, min_tokens, max_tokens)
            else:
                return self._pattern_based_chunking_with_metadata(content, ext, min_tokens, max_tokens)
        except Exception as e:
            print(f"Warning: Primary chunking failed for {ext}: {e}")
            # Fallback to robust pattern-based chunking
            return self._pattern_based_chunking_with_metadata(content, ext, min_tokens, max_tokens)

    def _semantic_code_chunking(self, content: str, ext: str, min_tokens: int, max_tokens: int) -> List[str]:
        """Advanced code chunking that respects semantic boundaries"""
        parser = self.parsers.get(ext)
        if not parser:
            return self._fallback_chunking(content, min_tokens, max_tokens)

        try:
            tree = parser.parse(bytes(content, 'utf8'))
            root = tree.root_node

            chunks = []
            current_chunk = ""
            current_tokens = 0

            def process_node(node):
                nonlocal current_chunk, current_tokens, chunks

                if node.type in ['function_definition', 'class_definition', 'method_definition', 'function', 'class']:
                    # Complete semantic unit - check if it fits
                    node_content = content[node.start_byte:node.end_byte]
                    node_tokens = self.count_tokens(node_content)

                    if current_tokens + node_tokens <= max_tokens:
                        current_chunk += node_content + "\n"
                        current_tokens += node_tokens
                    else:
                        # Current chunk is full, start new one
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        current_chunk = node_content + "\n"
                        current_tokens = node_tokens

                # Process children
                for child in node.children:
                    process_node(child)

            process_node(root)

            # Add remaining content
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            return chunks if chunks else [content]

        except Exception as e:
            print(f"Warning: Semantic code chunking failed: {e}")
            return self._fallback_chunking(content, min_tokens, max_tokens)

    def _semantic_code_chunking_with_metadata(self, content: str, ext: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Advanced code chunking that returns semantic metadata"""
        parser = self.parsers.get(ext)
        if not parser:
            return self._fallback_chunking_with_metadata(content, min_tokens, max_tokens)

        try:
            tree = parser.parse(bytes(content, 'utf8'))
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
                start_line = content[:node.start_byte].count('\n') + 1
                end_line = start_line + node_content.count('\n')

                if node_type in ['function_definition', 'method_definition']:
                    # Extract function name
                    func_name = self._extract_function_name(node_content, ext)
                    if func_name:
                        current_metadata['functions'].append(func_name)
                        current_metadata['semantic_types'].append('function')

                elif node_type in ['class_definition']:
                    # Extract class name
                    class_name = self._extract_class_name(node_content, ext)
                    if class_name:
                        current_metadata['classes'].append(class_name)
                        current_metadata['semantic_types'].append('class')

                elif node_type in ['import_statement', 'import_from_statement']:
                    current_metadata['imports'].append(node_content.strip())
                    current_metadata['semantic_types'].append('import')

                # Update complexity based on control structures
                if node_type in ['if_statement', 'for_statement', 'while_statement', 'try_statement']:
                    current_metadata['complexity'] += 1

                if node_type in ['function_definition', 'class_definition', 'method_definition']:
                    # Complete semantic unit - check if it fits
                    if current_tokens + node_tokens <= max_tokens:
                        current_chunk += node_content + "\n"
                        current_tokens += node_tokens
                        current_metadata['end_line'] = end_line
                    else:
                        # Current chunk is full, start new one
                        if current_chunk.strip():
                            chunk_metadata = current_metadata.copy()
                            chunk_metadata['content'] = current_chunk.strip()
                            chunk_metadata['token_count'] = current_tokens
                            chunks.append(chunk_metadata)

                        # Start new chunk
                        current_chunk = node_content + "\n"
                        current_tokens = node_tokens
                        current_metadata = {
                            'semantic_types': current_metadata.get('semantic_types', [])[-1:],  # Keep last type
                            'functions': [func_name] if 'func_name' in locals() and func_name else [],
                            'classes': [class_name] if 'class_name' in locals() and class_name else [],
                            'imports': [],
                            'complexity': 1 if node_type in ['function_definition', 'method_definition'] else 0,
                            'start_line': start_line,
                            'end_line': end_line
                        }
                else:
                    # Regular code - add to current chunk
                    if current_tokens + node_tokens <= max_tokens:
                        current_chunk += node_content + "\n"
                        current_tokens += node_tokens
                        current_metadata['end_line'] = end_line
                    else:
                        # Split here
                        if current_chunk.strip():
                            chunk_metadata = current_metadata.copy()
                            chunk_metadata['content'] = current_chunk.strip()
                            chunk_metadata['token_count'] = current_tokens
                            chunks.append(chunk_metadata)

                        current_chunk = node_content + "\n"
                        current_tokens = node_tokens
                        current_metadata = {
                            'semantic_types': [],
                            'functions': [],
                            'classes': [],
                            'imports': [],
                            'complexity': 0,
                            'start_line': start_line,
                            'end_line': end_line
                        }

                # Process children
                for child in node.children:
                    process_node(child)

            process_node(root)

            # Add remaining content
            if current_chunk.strip():
                current_metadata['content'] = current_chunk.strip()
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
                'end_line': content.count('\n') + 1,
                'token_count': self.count_tokens(content)
            }]

        except Exception as e:
            print(f"Warning: Semantic code chunking with metadata failed: {e}")
            return self._fallback_chunking_with_metadata(content, min_tokens, max_tokens)

    def _extract_function_name(self, content: str, ext: str) -> Optional[str]:
        """Extract function name from function definition"""
        try:
            if ext == '.py':
                match = re.search(r'def\s+(\w+)\s*\(', content)
                return match.group(1) if match else None
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                match = re.search(r'(?:function\s+|const\s+\w+\s*=\s*)\s*(\w+)\s*\(', content)
                return match.group(1) if match else None
            elif ext == '.java':
                match = re.search(r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(', content)
                return match.group(1) if match else None
            # Add more languages as needed
            return None
        except:
            return None

    def _extract_class_name(self, content: str, ext: str) -> Optional[str]:
        """Extract class name from class definition"""
        try:
            if ext in ['.py', '.js', '.ts', '.java', '.cpp', '.c']:
                match = re.search(r'class\s+(\w+)', content)
                return match.group(1) if match else None
            # Add more languages as needed
            return None
        except:
            return None

    def _fallback_chunking_with_metadata(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Fallback chunking that returns basic metadata"""
        chunks = []
        lines = content.split('\n')
        current_chunk = []
        current_tokens = 0
        start_line = 1

        for i, line in enumerate(lines):
            line_tokens = self.count_tokens(line)

            if current_tokens + line_tokens > max_tokens and current_tokens >= min_tokens:
                # Create chunk
                chunk_content = '\n'.join(current_chunk)
                chunks.append({
                    'content': chunk_content,
                    'semantic_types': ['code'],
                    'functions': [],
                    'classes': [],
                    'imports': [],
                    'complexity': 0,
                    'start_line': start_line,
                    'end_line': start_line + len(current_chunk) - 1,
                    'token_count': current_tokens
                })

                # Start new chunk
                current_chunk = [line]
                current_tokens = line_tokens
                start_line = i + 2  # 1-indexed, next line
            else:
                current_chunk.append(line)
                current_tokens += line_tokens

        # Add remaining content
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            chunks.append({
                'content': chunk_content,
                'semantic_types': ['code'],
                'functions': [],
                'classes': [],
                'imports': [],
                'complexity': 0,
                'start_line': start_line,
                'end_line': start_line + len(current_chunk) - 1,
                'token_count': current_tokens
            })

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

    def _is_python_function_start(self, line: str) -> bool:
        """Check if line starts a Python function definition"""
        stripped = line.strip()
        return (stripped.startswith('def ') or
                stripped.startswith('async def ')) and '(' in stripped

    def _is_python_class_start(self, line: str) -> bool:
        """Check if line starts a Python class definition"""
        stripped = line.strip()
        return stripped.startswith('class ') and ':' in stripped

    def _is_python_import(self, line: str) -> bool:
        """Check if line is a Python import statement"""
        stripped = line.strip()
        return (stripped.startswith('import ') or
                stripped.startswith('from ') or
                stripped.startswith('try:') or
                stripped.startswith('except'))

    def _extract_python_function_name(self, line: str) -> Optional[str]:
        """Extract function name from Python function definition"""
        try:
            match = re.search(r'def\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        except:
            return None

    def _extract_python_class_name(self, line: str) -> Optional[str]:
        """Extract class name from Python class definition"""
        try:
            match = re.search(r'class\s+(\w+)', line)
            return match.group(1) if match else None
        except:
            return None

    def _get_python_indent_level(self, line: str) -> int:
        """Get indentation level of Python line"""
        return len(line) - len(line.lstrip())

    def _javascript_pattern_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """JavaScript/TypeScript-specific pattern-based chunking"""
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
        brace_depth = 0

        while i < len(lines):
            line = lines[i]
            line_tokens = self.count_tokens(line + '\n')

            # Track brace depth for function/class boundaries
            brace_depth += line.count('{') - line.count('}')

            # Check for function definitions
            if self._is_js_function_start(line):
                func_name = self._extract_js_function_name(line)
                if func_name:
                    # Add function to current chunk metadata
                    if 'function' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('function')
                    current_metadata['functions'].append(func_name)
                    current_metadata['complexity'] += 1

            # Check for class definitions
            elif self._is_js_class_start(line):
                class_name = self._extract_js_class_name(line)
                if class_name:
                    # Add class to current chunk metadata
                    if 'class' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('class')
                    current_metadata['classes'].append(class_name)
                    current_metadata['complexity'] += 1

            # Check for imports
            elif self._is_js_import(line):
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

    def _is_js_function_start(self, line: str) -> bool:
        """Check if line starts a JavaScript function"""
        stripped = line.strip()
        return (stripped.startswith('function ') or
                (stripped.startswith('const ') and '=>' in stripped) or
                (stripped.startswith('let ') and '=>' in stripped) or
                (stripped.startswith('var ') and '=>' in stripped) or
                ('=>' in stripped and '(' in stripped and not stripped.startswith('const ') and not stripped.startswith('let ') and not stripped.startswith('var ')))

    def _is_js_class_start(self, line: str) -> bool:
        """Check if line starts a JavaScript class"""
        stripped = line.strip()
        return stripped.startswith('class ')

    def _is_js_import(self, line: str) -> bool:
        """Check if line is a JavaScript import"""
        stripped = line.strip()
        return (stripped.startswith('import ') or
                stripped.startswith('const ') and 'require(' in stripped or
                stripped.startswith('let ') and 'require(' in stripped or
                stripped.startswith('var ') and 'require(' in stripped)

    def _extract_js_function_name(self, line: str) -> Optional[str]:
        """Extract function name from JavaScript function definition"""
        try:
            stripped = line.strip()
            if stripped.startswith('function '):
                match = re.search(r'function\s+(\w+)\s*\(', stripped)
                return match.group(1) if match else None
            elif '=>' in stripped:
                # Arrow function or const function
                match = re.search(r'(?:const|let|var)\s+(\w+)\s*[:=]', stripped)
                if match:
                    return match.group(1)
                # Anonymous arrow function in assignment
                match = re.search(r'(\w+)\s*[:=]\s*\([^)]*\)\s*=>', stripped)
                return match.group(1) if match else None
            return None
        except:
            return None

    def _extract_js_class_name(self, line: str) -> Optional[str]:
        """Extract class name from JavaScript class definition"""
        try:
            match = re.search(r'class\s+(\w+)', line)
            return match.group(1) if match else None
        except:
            return None

    def _java_pattern_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Java-specific pattern-based chunking"""
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
        brace_depth = 0

        while i < len(lines):
            line = lines[i]
            line_tokens = self.count_tokens(line + '\n')

            # Track brace depth
            brace_depth += line.count('{') - line.count('}')

            # Check for class definitions
            if self._is_java_class_start(line):
                class_name = self._extract_java_class_name(line)
                if class_name:
                    # Add class to current chunk metadata
                    if 'class' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('class')
                    current_metadata['classes'].append(class_name)
                    current_metadata['complexity'] += 1

            # Check for method definitions
            elif self._is_java_method_start(line):
                method_name = self._extract_java_method_name(line)
                if method_name:
                    # Add method to current chunk metadata
                    if 'function' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('function')
                    current_metadata['functions'].append(method_name)
                    current_metadata['complexity'] += 1

            # Check for imports
            elif self._is_java_import(line):
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

    def _is_java_class_start(self, line: str) -> bool:
        """Check if line starts a Java class"""
        stripped = line.strip()
        return (stripped.startswith('public class ') or
                stripped.startswith('private class ') or
                stripped.startswith('protected class ') or
                stripped.startswith('class ')) and '{' in stripped

    def _is_java_method_start(self, line: str) -> bool:
        """Check if line starts a Java method"""
        stripped = line.strip()
        # Look for method signature pattern
        return (('(' in stripped and ')' in stripped and '{' in stripped) and
                not stripped.startswith('if ') and
                not stripped.startswith('for ') and
                not stripped.startswith('while ') and
                not stripped.startswith('class '))

    def _is_java_import(self, line: str) -> bool:
        """Check if line is a Java import"""
        stripped = line.strip()
        return stripped.startswith('import ') or stripped.startswith('package ')

    def _extract_java_class_name(self, line: str) -> Optional[str]:
        """Extract class name from Java class definition"""
        try:
            match = re.search(r'class\s+(\w+)', line)
            return match.group(1) if match else None
        except:
            return None

    def _extract_java_method_name(self, line: str) -> Optional[str]:
        """Extract method name from Java method definition"""
        try:
            # Extract method name from pattern like: public void methodName(
            match = re.search(r'(?:public|private|protected)?\s*\w+\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        except:
            return None

    def _generic_pattern_chunking(self, content: str, ext: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Generic pattern-based chunking for languages without specific support"""
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

            # Look for common patterns across languages
            if self._is_generic_function_start(line, ext):
                func_name = self._extract_generic_function_name(line, ext)
                if func_name:
                    # Add function to current chunk metadata
                    if 'function' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('function')
                    current_metadata['functions'].append(func_name)
                    current_metadata['complexity'] += 1

            # Check for imports
            elif self._is_generic_import(line, ext):
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

    def _is_generic_function_start(self, line: str, ext: str) -> bool:
        """Generic function detection across languages"""
        stripped = line.strip()
        if ext == '.go':
            return stripped.startswith('func ')
        elif ext == '.rs':
            return stripped.startswith('fn ') and '(' in stripped
        elif ext == '.php':
            return stripped.startswith('function ') and '(' in stripped
        elif ext == '.rb':
            return stripped.startswith('def ') and '(' in stripped
        # Default patterns
        return ('function' in stripped.lower() or
                'def ' in stripped or
                'fn ' in stripped) and '(' in stripped

    def _extract_generic_function_name(self, line: str, ext: str) -> Optional[str]:
        """Generic function name extraction"""
        try:
            if ext == '.go':
                match = re.search(r'func\s+(\w+)\s*\(', line)
            elif ext == '.rs':
                match = re.search(r'fn\s+(\w+)\s*\(', line)
            elif ext == '.php':
                match = re.search(r'function\s+(\w+)\s*\(', line)
            elif ext == '.rb':
                match = re.search(r'def\s+(\w+)\s*\(', line)
            else:
                match = re.search(r'(?:function|def|fn)\s+(\w+)\s*\(', line)
            return match.group(1) if match else None
        except:
            return None

    def _is_generic_import(self, line: str, ext: str) -> bool:
        """Generic import detection across languages"""
        stripped = line.strip()
        if ext == '.go':
            return stripped.startswith('import ') or stripped == 'import ('
        elif ext == '.rs':
            return stripped.startswith('use ')
        elif ext == '.php':
            return stripped.startswith('use ') or stripped.startswith('require ') or stripped.startswith('include ')
        elif ext == '.rb':
            return stripped.startswith('require ') or stripped.startswith('require_relative ')
        else:
            return (stripped.startswith('import ') or
                    stripped.startswith('from ') or
                    stripped.startswith('require ') or
                    stripped.startswith('include ') or
                    stripped.startswith('use '))

    def _semantic_markdown_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[str]:
        """Smart markdown chunking that preserves section boundaries"""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_tokens = 0

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a header
            if re.match(r'^#{1,6}\s', line):
                # If we have content in current chunk, save it
                if current_chunk and current_tokens >= min_tokens:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0

                # Start new section with this header
                current_chunk = [line]
                current_tokens = self.count_tokens(line)

                # Include content until next header or end
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    if re.match(r'^#{1,6}\s', next_line):
                        # Next header found, break
                        break

                    current_chunk.append(next_line)
                    current_tokens += self.count_tokens(next_line)

                    # Check if chunk is getting too large
                    if current_tokens >= max_tokens:
                        # Find a good break point (paragraph, list, etc.)
                        break_point = self._find_markdown_break_point(current_chunk)
                        if break_point > 0:
                            chunks.append('\n'.join(current_chunk[:break_point]))
                            current_chunk = current_chunk[break_point:]
                            current_tokens = self.count_tokens('\n'.join(current_chunk))
                        else:
                            # Force break
                            chunks.append('\n'.join(current_chunk))
                            current_chunk = []
                            current_tokens = 0
                            break

                    i += 1

                # Add completed section
                if current_chunk:
                    chunks.append('\n'.join(current_chunk))
                    current_chunk = []
                    current_tokens = 0
            else:
                i += 1

        # Add any remaining content
        if current_chunk:
            chunks.append('\n'.join(current_chunk))

        return chunks if chunks else [content]

    def _semantic_markdown_chunking_with_metadata(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Smart markdown chunking that returns semantic metadata"""
        lines = content.split('\n')
        chunks = []
        current_chunk = []
        current_tokens = 0
        current_metadata = {
            'semantic_types': [],
            'sections': [],
            'headers': [],
            'start_line': 1,
            'end_line': 1
        }

        i = 0
        while i < len(lines):
            line = lines[i]

            # Check if this is a header
            header_match = re.match(r'^(#{1,6})\s+(.+)', line)
            if header_match:
                # If we have content in current chunk, save it
                if current_chunk and current_tokens >= min_tokens:
                    chunk_content = '\n'.join(current_chunk)
                    chunk_metadata = current_metadata.copy()
                    chunk_metadata['content'] = chunk_content
                    chunk_metadata['token_count'] = current_tokens
                    chunks.append(chunk_metadata)

                # Start new section with this header
                header_level = len(header_match.group(1))
                header_text = header_match.group(2).strip()
                current_chunk = [line]
                current_tokens = self.count_tokens(line)
                current_metadata = {
                    'semantic_types': ['section'],
                    'sections': [header_text],
                    'headers': [{'level': header_level, 'text': header_text}],
                    'start_line': i + 1,
                    'end_line': i + 1
                }

                # Include content until next header or end
                i += 1
                while i < len(lines):
                    next_line = lines[i]
                    next_header_match = re.match(r'^#{1,6}\s', next_line)
                    if next_header_match:
                        # Next header found, break
                        break

                    current_chunk.append(next_line)
                    current_tokens += self.count_tokens(next_line)
                    current_metadata['end_line'] = i + 1

                    # Check if chunk is getting too large
                    if current_tokens >= max_tokens:
                        # Find a good break point (paragraph, list, etc.)
                        break_point = self._find_markdown_break_point(current_chunk)
                        if break_point > 0:
                            chunk_content = '\n'.join(current_chunk[:break_point])
                            chunk_metadata = current_metadata.copy()
                            chunk_metadata['content'] = chunk_content
                            chunk_metadata['token_count'] = self.count_tokens(chunk_content)
                            chunks.append(chunk_metadata)

                            current_chunk = current_chunk[break_point:]
                            current_tokens = self.count_tokens('\n'.join(current_chunk))
                            current_metadata['start_line'] = current_metadata['end_line'] - len(current_chunk) + 1
                        else:
                            # Force break
                            chunk_content = '\n'.join(current_chunk)
                            chunk_metadata = current_metadata.copy()
                            chunk_metadata['content'] = chunk_content
                            chunk_metadata['token_count'] = current_tokens
                            chunks.append(chunk_metadata)

                            current_chunk = []
                            current_tokens = 0
                            break

                    i += 1

                # Add completed section
                if current_chunk:
                    chunk_content = '\n'.join(current_chunk)
                    current_metadata['content'] = chunk_content
                    current_metadata['token_count'] = current_tokens
                    chunks.append(current_metadata)
                    current_chunk = []
                    current_tokens = 0
            else:
                i += 1

        # Add any remaining content
        if current_chunk:
            chunk_content = '\n'.join(current_chunk)
            current_metadata['content'] = chunk_content
            current_metadata['token_count'] = current_tokens
            chunks.append(current_metadata)

        return chunks if chunks else [{
            'content': content,
            'semantic_types': ['markdown'],
            'sections': [],
            'headers': [],
            'start_line': 1,
            'end_line': len(lines),
            'token_count': self.count_tokens(content)
        }]

    def _find_markdown_break_point(self, lines: List[str]) -> int:
        """Find optimal break point in markdown content"""
        for i in range(len(lines) - 1, 0, -1):
            line = lines[i].strip()
            # Prefer breaking at paragraph breaks, list items, etc.
            if not line:  # Empty line (paragraph break)
                return i
            if line.startswith(('- ', '* ', '1. ', '2. ', '3. ')):  # List items
                return i
        return len(lines) // 2  # Fallback to middle

    def _semantic_html_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[str]:
        """Smart HTML chunking that preserves element boundaries"""
        parser = self.parsers.get('.html')
        if not parser:
            return self._fallback_chunking(content, min_tokens, max_tokens)

        try:
            tree = parser.parse(bytes(content, 'utf8'))
            root = tree.root_node

            chunks = []
            current_chunk = ""
            current_tokens = 0

            def process_html_node(node, depth=0):
                nonlocal current_chunk, current_tokens, chunks

                if node.type == 'element':
                    # Get element content
                    element_content = content[node.start_byte:node.end_byte]
                    element_tokens = self.count_tokens(element_content)

                    # Check if element fits in current chunk
                    if current_tokens + element_tokens <= max_tokens:
                        current_chunk += element_content
                        current_tokens += element_tokens
                    else:
                        # Save current chunk and start new one
                        if current_chunk.strip():
                            chunks.append(current_chunk.strip())
                        current_chunk = element_content
                        current_tokens = element_tokens

                # Process children
                for child in node.children:
                    process_html_node(child, depth + 1)

            process_html_node(root)

            # Add remaining content
            if current_chunk.strip():
                chunks.append(current_chunk.strip())

            return chunks if chunks else [content]

        except Exception as e:
            print(f"Warning: Semantic HTML chunking failed: {e}")
            return self._fallback_chunking(content, min_tokens, max_tokens)

    def _semantic_html_chunking_with_metadata(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Smart HTML chunking that returns semantic metadata"""
        parser = self.parsers.get('.html')
        if not parser:
            return self._fallback_chunking_with_metadata(content, min_tokens, max_tokens)

        try:
            tree = parser.parse(bytes(content, 'utf8'))
            root = tree.root_node

            chunks = []
            current_chunk = ""
            current_tokens = 0
            current_metadata = {
                'semantic_types': [],
                'elements': [],
                'tags': [],
                'start_line': 1,
                'end_line': 1
            }

            def process_html_node(node, depth=0):
                nonlocal current_chunk, current_tokens, chunks, current_metadata

                if node.type == 'element':
                    # Get element content
                    element_content = content[node.start_byte:node.end_byte]
                    element_tokens = self.count_tokens(element_content)

                    # Extract tag information
                    tag_match = re.search(r'<(\w+)', element_content)
                    tag_name = tag_match.group(1) if tag_match else 'element'

                    # Update metadata
                    current_metadata['elements'].append(tag_name)
                    if tag_name not in current_metadata['tags']:
                        current_metadata['tags'].append(tag_name)

                    # Determine semantic type
                    if tag_name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                        current_metadata['semantic_types'].append('heading')
                    elif tag_name in ['p', 'div', 'section', 'article']:
                        current_metadata['semantic_types'].append('content')
                    elif tag_name in ['ul', 'ol', 'li']:
                        current_metadata['semantic_types'].append('list')
                    elif tag_name == 'table':
                        current_metadata['semantic_types'].append('table')

                    start_line = content[:node.start_byte].count('\n') + 1
                    end_line = start_line + element_content.count('\n')

                    # Check if element fits in current chunk
                    if current_tokens + element_tokens <= max_tokens:
                        current_chunk += element_content
                        current_tokens += element_tokens
                        current_metadata['end_line'] = end_line
                    else:
                        # Save current chunk and start new one
                        if current_chunk.strip():
                            chunk_metadata = current_metadata.copy()
                            chunk_metadata['content'] = current_chunk.strip()
                            chunk_metadata['token_count'] = current_tokens
                            chunks.append(chunk_metadata)

                        current_chunk = element_content
                        current_tokens = element_tokens
                        current_metadata = {
                            'semantic_types': [current_metadata['semantic_types'][-1]] if current_metadata['semantic_types'] else [],
                            'elements': [tag_name],
                            'tags': [tag_name],
                            'start_line': start_line,
                            'end_line': end_line
                        }

                # Process children
                for child in node.children:
                    process_html_node(child, depth + 1)

            process_html_node(root)

            # Add remaining content
            if current_chunk.strip():
                current_metadata['content'] = current_chunk.strip()
                current_metadata['token_count'] = current_tokens
                chunks.append(current_metadata)

            return chunks if chunks else [{
                'content': content,
                'semantic_types': ['html'],
                'elements': [],
                'tags': [],
                'start_line': 1,
                'end_line': content.count('\n') + 1,
                'token_count': self.count_tokens(content)
            }]

        except Exception as e:
            print(f"Warning: Semantic HTML chunking with metadata failed: {e}")
            return self._fallback_chunking_with_metadata(content, min_tokens, max_tokens)

    def _pattern_based_chunking_with_metadata(self, content: str, ext: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Robust pattern-based chunking that works across languages and environments"""
        try:
            # Language-specific pattern-based chunking
            if ext == '.py':
                return self._python_pattern_chunking(content, min_tokens, max_tokens)
            elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                return self._javascript_pattern_chunking(content, min_tokens, max_tokens)
            elif ext == '.java':
                return self._java_pattern_chunking(content, min_tokens, max_tokens)
            elif ext in ['.cpp', '.c', '.cc', '.cxx']:
                return self._generic_pattern_chunking(content, ext, min_tokens, max_tokens)
            elif ext == '.go':
                return self._generic_pattern_chunking(content, ext, min_tokens, max_tokens)
            elif ext == '.rs':
                return self._generic_pattern_chunking(content, ext, min_tokens, max_tokens)
            elif ext == '.php':
                return self._generic_pattern_chunking(content, ext, min_tokens, max_tokens)
            elif ext == '.rb':
                return self._generic_pattern_chunking(content, ext, min_tokens, max_tokens)
            else:
                # Generic pattern-based chunking for other languages
                return self._generic_pattern_chunking(content, ext, min_tokens, max_tokens)

        except Exception as e:
            print(f"Warning: Pattern-based chunking failed: {e}")
            return self._fallback_chunking_with_metadata(content, min_tokens, max_tokens)

    def _python_pattern_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[Dict[str, Any]]:
        """Python-specific pattern-based chunking with semantic awareness"""
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
            if self._is_python_function_start(line):
                func_name = self._extract_python_function_name(line)
                if func_name:
                    # Add function to current chunk metadata
                    if 'function' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('function')
                    current_metadata['functions'].append(func_name)
                    current_metadata['complexity'] += 1

            elif self._is_python_class_start(line):
                class_name = self._extract_python_class_name(line)
                if class_name:
                    # Add class to current chunk metadata
                    if 'class' not in current_metadata['semantic_types']:
                        current_metadata['semantic_types'].append('class')
                    current_metadata['classes'].append(class_name)
                    current_metadata['complexity'] += 1

            elif self._is_python_import(line):
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

    def _fallback_chunking(self, content: str, min_tokens: int, max_tokens: int) -> List[str]:
        """Fallback chunking when semantic parsing fails"""
        words = content.split()
        chunks = []
        current_chunk = []
        current_tokens = 0

        for word in words:
            word_tokens = self.count_tokens(word + " ")
            if current_tokens + word_tokens > max_tokens and current_tokens >= min_tokens:
                chunks.append(' '.join(current_chunk))
                current_chunk = [word]
                current_tokens = word_tokens
            else:
                current_chunk.append(word)
                current_tokens += word_tokens

        if current_chunk:
            chunks.append(' '.join(current_chunk))

        return chunks

    def smart_overlap(self, chunks: List[str], overlap_chars: int = 200) -> List[str]:
        """Intelligent overlap that preserves semantic context"""
        if not chunks or overlap_chars <= 0:
            return chunks

        overlapped = []
        for i, chunk in enumerate(chunks):
            if i == 0:
                overlapped.append(chunk)
                continue

            prev_chunk = chunks[i-1]

            # Extract meaningful overlap from previous chunk
            overlap_text = self._extract_semantic_overlap(prev_chunk, overlap_chars)

            # Combine with current chunk
            overlapped_chunk = overlap_text + "\n\n" + chunk
            overlapped.append(overlapped_chunk)

        return overlapped

    def _extract_semantic_overlap(self, chunk: str, max_chars: int) -> str:
        """Extract semantically meaningful overlap from chunk"""
        if len(chunk) <= max_chars:
            return chunk

        # Try to find natural break points
        lines = chunk.split('\n')

        overlap_text = ""
        for line in reversed(lines):
            if len(overlap_text) + len(line) + 1 > max_chars:
                break
            overlap_text = line + "\n" + overlap_text

        # If no good break found, use character limit
        if not overlap_text.strip():
            overlap_text = chunk[-max_chars:]

        return overlap_text.strip()

    def build_hierarchical_chunks(self, chunks: List[str], file_path: str) -> List[Dict[str, Any]]:
        """Build hierarchical chunk structure with parent-child relationships"""
        hierarchical_chunks = []

        for i, chunk in enumerate(chunks):
            chunk_id = f"{os.path.basename(file_path)}:{i}"

            # Determine parent relationships
            parent_id = None
            if i > 0:
                # Check if this chunk is a continuation of the previous
                if self._are_chunks_related(chunks[i-1], chunk):
                    parent_id = f"{os.path.basename(file_path)}:{i-1}"

            hierarchical_chunk = {
                "id": chunk_id,
                "content": chunk,
                "parent_id": parent_id,
                "children": [],
                "level": self._determine_chunk_level(chunk),
                "metadata": {
                    "file_path": file_path,
                    "chunk_index": i,
                    "is_leaf": True,  # Will be updated if children are found
                    "semantic_type": self._classify_semantic_type(chunk)
                }
            }

            hierarchical_chunks.append(hierarchical_chunk)

        # Update parent-child relationships
        for chunk in hierarchical_chunks:
            if chunk["parent_id"]:
                parent = next((c for c in hierarchical_chunks if c["id"] == chunk["parent_id"]), None)
                if parent:
                    parent["children"].append(chunk["id"])
                    parent["metadata"]["is_leaf"] = False

        return hierarchical_chunks

    def _are_chunks_related(self, chunk1: str, chunk2: str) -> bool:
        """Determine if two chunks are semantically related"""
        # Simple heuristics for relatedness
        chunk1_lower = chunk1.lower()
        chunk2_lower = chunk2.lower()

        # Check for shared keywords, functions, classes
        words1 = set(re.findall(r'\b\w+\b', chunk1_lower))
        words2 = set(re.findall(r'\b\w+\b', chunk2_lower))

        overlap = len(words1.intersection(words2))
        total_words = len(words1.union(words2))

        return overlap / total_words > 0.3 if total_words > 0 else False

    def _determine_chunk_level(self, chunk: str) -> int:
        """Determine hierarchical level of chunk"""
        # Count indentation or structural indicators
        lines = chunk.split('\n')
        indent_levels = []

        for line in lines:
            if line.strip():
                indent = len(line) - len(line.lstrip())
                indent_levels.append(indent)

        return max(indent_levels) // 4 if indent_levels else 0

    def _classify_semantic_type(self, chunk: str) -> str:
        """Classify the semantic type of a chunk"""
        chunk_lower = chunk.lower()

        # Function/class definitions
        if re.search(r'\b(def|class|function|fn)\b', chunk_lower):
            return "definition"

        # Documentation/comments
        if re.search(r'"""|///|/\*|\*|# ', chunk):
            return "documentation"

        # Configuration/data
        if re.search(r'(\w+\s*=\s*[\'"]\w+[\'"]|\w+\s*:\s*\w+)', chunk):
            return "configuration"

        # Logic/control flow
        if re.search(r'\b(if|for|while|try|except)\b', chunk_lower):
            return "logic"

        return "implementation"

    def extract_cross_file_relationships(self, file_path: str, content: str, ext: str):
        """Extract relationships between files for better context"""
        file_key = os.path.basename(file_path)

        if ext in self.code_exts:
            # Extract imports and dependencies
            imports = self._extract_imports(content, ext)
            for imp in imports:
                self.import_graph[file_key].append(imp)
                # Reverse relationship
                self.relationship_graph[imp].append(file_key)

        # Extract function/class references
        if ext == '.py':
            functions = re.findall(r'def\s+(\w+)\s*\(', content)
            classes = re.findall(r'class\s+(\w+)\s*[:\(]', content)

            for func in functions:
                self.relationship_graph[f"{file_key}:{func}"].append(file_key)

            for cls in classes:
                self.relationship_graph[f"{file_key}:{cls}"].append(file_key)

    def _extract_imports(self, content: str, ext: str) -> List[str]:
        """Extract import statements from code"""
        imports = []

        if ext == '.py':
            # Python imports
            py_imports = re.findall(r'^(?:from\s+(\w+)|import\s+(\w+))', content, re.MULTILINE)
            imports.extend([imp[0] or imp[1] for imp in py_imports if imp[0] or imp[1]])

        elif ext in ['.js', '.jsx', '.ts', '.tsx']:
            # JavaScript/TypeScript imports
            js_imports = re.findall(r'import\s+.*?\s+from\s+[\'"]([^\'"]+)[\'"]', content)
            imports.extend(js_imports)

        elif ext == '.java':
            # Java imports
            java_imports = re.findall(r'import\s+([^;]+);', content)
            imports.extend(java_imports)

        return imports

    def chunk_file_smart(self, file_path: str, overlap: int = 200) -> List[Dict[str, Any]]:
        """Main smart chunking method with all enhancements"""
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as file:
                content = file.read()
        except Exception as e:
            return [{"content": f"⚠️ Error reading {os.path.basename(file_path)}: {e}", "metadata": {}}]

        # Check if file has changed (for incremental updates)
        file_hash = self._get_file_hash(file_path)
        if file_path in self.file_hashes and self.file_hashes[file_path] == file_hash:
            # File unchanged, return cached result
            return self.chunk_cache.get(file_path, [])

        ext = os.path.splitext(file_path)[1].lower()

        # Extract cross-file relationships
        self.extract_cross_file_relationships(file_path, content, ext)

        # Smart chunking with dynamic sizing
        raw_chunks = self.smart_chunk_content(content, ext)

        # Apply intelligent overlap
        if overlap > 0:
            raw_chunks = self.smart_overlap(raw_chunks, overlap)

        # Build hierarchical structure
        hierarchical_chunks = self.build_hierarchical_chunks(raw_chunks, file_path)

        # Add comprehensive metadata
        final_chunks = self.add_enhanced_metadata(hierarchical_chunks, file_path, ext)

        # Cache result
        self.chunk_cache[file_path] = final_chunks
        self.file_hashes[file_path] = file_hash

        return final_chunks

    def _get_file_hash(self, file_path: str) -> str:
        """Get file hash for change detection"""
        try:
            with open(file_path, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""

    def add_enhanced_metadata(self, chunks: List[Dict[str, Any]], file_path: str, ext: str) -> List[Dict[str, Any]]:
        """Add comprehensive metadata with all enhancements"""
        # Extract file information
        file_name = os.path.basename(file_path)
        file_dir = os.path.dirname(file_path)
        file_size = os.path.getsize(file_path) if os.path.exists(file_path) else 0

        # Determine language and content type
        language = self._get_language_from_extension(ext)
        content_type = self._get_content_type_from_extension(ext)

        # Extract enhanced semantic context
        semantic_context = self._extract_enhanced_semantic_context(file_path, ext)

        base_metadata = {
            "file_path": file_path,
            "file_name": file_name,
            "file_directory": file_dir,
            "file_extension": ext,
            "file_size": file_size,
            "language": language,
            "content_type": content_type,
            "chunk_count": len(chunks),
            "last_modified": os.path.getmtime(file_path) if os.path.exists(file_path) else None,
        }

        # Add semantic context
        base_metadata.update(semantic_context)

        enhanced_chunks = []
        for chunk in chunks:
            chunk_metadata = base_metadata.copy()
            chunk_metadata.update(chunk.get("metadata", {}))

            # Add chunk-specific metadata
            chunk_metadata.update({
                "chunk_length": len(chunk["content"]),
                "token_count": self.count_tokens(chunk["content"]),
                "chunk_type": self._classify_chunk_type(chunk["content"], ext),
                "has_code": self._chunk_contains_code(chunk["content"], ext),
                "has_documentation": self._chunk_contains_documentation(chunk["content"]),
                "importance_score": self._calculate_enhanced_importance_score(chunk, ext),
                "cross_references": self._find_cross_references(chunk["content"], file_path),
                "complexity_score": self.calculate_content_complexity(chunk["content"], ext)
            })

            enhanced_chunk = {
                "id": chunk["id"],
                "content": self._clean_chunk_content(chunk["content"]),
                "metadata": chunk_metadata,
                "parent_id": chunk.get("parent_id"),
                "children": chunk.get("children", []),
                "level": chunk.get("level", 0)
            }

            enhanced_chunks.append(enhanced_chunk)

        return enhanced_chunks

    def _extract_enhanced_semantic_context(self, file_path: str, ext: str) -> Dict[str, Any]:
        """Extract enhanced semantic context with cross-file relationships"""
        context = {
            "functions": [],
            "classes": [],
            "imports": [],
            "sections": [],
            "dependencies": [],
            "cross_file_refs": []
        }

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if ext in self.code_exts:
                context.update(self._extract_advanced_code_context(content, ext))
            elif ext in self.markdown_exts:
                context.update(self._extract_enhanced_markdown_context(content))
            elif ext in self.json_exts:
                context.update(self._extract_enhanced_json_context(content))

            # Add cross-file references
            file_key = os.path.basename(file_path)
            context["cross_file_refs"] = self.relationship_graph.get(file_key, [])

        except Exception as e:
            context["extraction_error"] = str(e)

        return context

    def _extract_advanced_code_context(self, content: str, ext: str) -> Dict[str, Any]:
        """Advanced code context extraction with AST analysis"""
        context = {"functions": [], "classes": [], "imports": [], "dependencies": []}

        try:
            parser = self.parsers.get(ext)
            if parser:
                tree = parser.parse(bytes(content, 'utf8'))
                root = tree.root_node

                def extract_from_node(node):
                    if node.type in ['function_definition', 'method_definition']:
                        func_name = content[node.start_byte:node.end_byte].split('(')[0].split()[-1]
                        context["functions"].append(func_name)
                    elif node.type in ['class_definition', 'class']:
                        class_name = content[node.start_byte:node.end_byte].split('(')[0].split()[-1]
                        context["classes"].append(class_name)

                    for child in node.children:
                        extract_from_node(child)

                extract_from_node(root)

            # Fallback regex extraction
            if not context["functions"]:
                if ext == '.py':
                    context["functions"] = re.findall(r'def\s+(\w+)\s*\(', content)
                    context["classes"] = re.findall(r'class\s+(\w+)\s*[:\(]', content)
                    context["imports"] = re.findall(r'^(?:from\s+\w+\s+import|import\s+\w+)', content, re.MULTILINE)

        except Exception:
            pass

        return context

    def _extract_enhanced_markdown_context(self, content: str) -> Dict[str, Any]:
        """Enhanced markdown context with structure analysis"""
        context = {"sections": [], "links": [], "code_blocks": []}

        try:
            # Extract headers with hierarchy
            headers = re.findall(r'^(#{1,6})\s+(.+)$', content, re.MULTILINE)
            context["sections"] = [{"level": len(h[0]), "title": h[1].strip()} for h in headers]

            # Extract links
            links = re.findall(r'\[([^\]]+)\]\(([^)]+)\)', content)
            context["links"] = [{"text": link[0], "url": link[1]} for link in links]

            # Extract code blocks
            code_blocks = re.findall(r'```(\w+)?\n(.*?)\n```', content, re.DOTALL)
            context["code_blocks"] = [{"language": cb[0] or "text", "code": cb[1]} for cb in code_blocks]

        except Exception:
            pass

        return context

    def _extract_enhanced_json_context(self, content: str) -> Dict[str, Any]:
        """Enhanced JSON context with structure analysis"""
        context = {"structure": [], "keys": []}

        try:
            if content.strip().startswith('{') or content.strip().startswith('['):
                data = json.loads(content)
                context["keys"] = list(self._extract_json_keys(data))
                context["structure"] = self._analyze_json_structure(data)
        except Exception:
            pass

        return context

    def _analyze_json_structure(self, data, path="") -> List[Dict[str, Any]]:
        """Analyze JSON structure for better understanding"""
        structure = []

        if isinstance(data, dict):
            for key, value in data.items():
                full_path = f"{path}.{key}" if path else key
                item = {
                    "path": full_path,
                    "type": type(value).__name__,
                    "has_children": isinstance(value, (dict, list))
                }
                structure.append(item)
                if isinstance(value, (dict, list)):
                    structure.extend(self._analyze_json_structure(value, full_path))
        elif isinstance(data, list) and data:
            item = {
                "path": f"{path}[]",
                "type": type(data[0]).__name__,
                "has_children": isinstance(data[0], (dict, list))
            }
            structure.append(item)

        return structure

    def _calculate_enhanced_importance_score(self, chunk: Dict[str, Any], ext: str) -> float:
        """Enhanced importance scoring with all factors"""
        score = 0.5  # Base score

        content = chunk["content"]

        # 1. Advanced keyword analysis (+0.3 max)
        score += self._advanced_keyword_boost(content, ext)

        # 2. Code quality metrics (+0.2 max)
        score += self._code_quality_boost(content)

        # 3. Position and structure (+0.1 max)
        chunk_index = chunk.get("metadata", {}).get("chunk_index", 0)
        total_chunks = chunk.get("metadata", {}).get("chunk_count", 1)
        score += self._structural_boost(chunk_index, total_chunks)

        # 4. Semantic similarity boost (+0.2 max)
        score += self._semantic_boost(content)

        # 5. Hierarchical boost (+0.1 max)
        score += self._hierarchical_boost(chunk)

        # 6. Cross-reference boost (+0.1 max)
        score += self._cross_reference_boost(chunk)

        return min(score, 1.0)

    def _hierarchical_boost(self, chunk: Dict[str, Any]) -> float:
        """Boost based on hierarchical position"""
        boost = 0.0

        level = chunk.get("level", 0)
        is_leaf = chunk.get("metadata", {}).get("is_leaf", True)
        children_count = len(chunk.get("children", []))

        # Root level chunks get boost
        if level == 0:
            boost += 0.03

        # Chunks with many children (important hubs)
        boost += min(children_count * 0.01, 0.05)

        # Leaf nodes with high specificity
        if is_leaf and level > 2:
            boost += 0.02

        return boost

    def _cross_reference_boost(self, chunk: Dict[str, Any]) -> float:
        """Boost based on cross-file references"""
        boost = 0.0

        cross_refs = chunk.get("metadata", {}).get("cross_references", [])
        boost += min(len(cross_refs) * 0.02, 0.1)

        return boost

    def _find_cross_references(self, content: str, file_path: str) -> List[str]:
        """Find cross-references to other files or symbols"""
        references = []

        # Find function calls, class instantiations, etc.
        # This is a simplified version - could be much more sophisticated
        words = re.findall(r'\b\w+\b', content)
        for word in words:
            if word in self.relationship_graph:
                references.extend(self.relationship_graph[word])

        return list(set(references))

    def _advanced_keyword_boost(self, chunk, ext):
        """Advanced keyword analysis with weighted scoring"""
        boost = 0.0

        # Language-specific patterns with weights
        patterns = {
            '.py': {
                'def ': 0.15, 'class ': 0.15, 'import ': 0.05, 'from ': 0.05,
                '__init__': 0.1, 'main': 0.1, 'async def': 0.1, 'if __name__': 0.08
            },
            '.js': {
                'function ': 0.15, 'class ': 0.15, 'import ': 0.05, 'export ': 0.1,
                'const ': 0.05, '=>': 0.05, 'async ': 0.08
            },
            '.ts': {
                'function ': 0.15, 'class ': 0.15, 'interface ': 0.12, 'type ': 0.08,
                'import ': 0.05, 'export ': 0.1, 'async ': 0.08
            },
            '.java': {
                'public class ': 0.15, 'private class ': 0.12, 'public static ': 0.1,
                'public void ': 0.12, 'import ': 0.05
            },
            '.cpp': {
                'class ': 0.15, 'void ': 0.12, 'int main': 0.1, '#include ': 0.05,
                'public:': 0.08, 'private:': 0.06
            },
            '.c': {
                'int main': 0.1, 'void ': 0.12, '#include ': 0.05, 'struct ': 0.08
            },
            '.go': {
                'func ': 0.15, 'type ': 0.12, 'package main': 0.1, 'import ': 0.05
            },
            '.rs': {
                'fn ': 0.15, 'struct ': 0.12, 'impl ': 0.1, 'pub ': 0.08
            },
            '.md': {
                '# ': 0.15, '## ': 0.12, '### ': 0.1, 'TODO': 0.08, 'FIXME': 0.08
            }
        }

        # Check for patterns in the chunk
        if ext in patterns:
            for pattern, weight in patterns[ext].items():
                if pattern in chunk:
                    boost += weight

        return min(boost, 0.3)  # Cap at 0.3

    def _code_quality_boost(self, chunk):
        """Analyze code quality and structure"""
        boost = 0.0

        # Function/class definitions
        if re.search(r'(def |class |function |fn |public class )', chunk):
            boost += 0.1

        # Documentation presence
        if re.search(r'(""".*"""|# .*|/\*.*\*/|/// )', chunk, re.DOTALL):
            boost += 0.05

        # Code density (avoid pure comment chunks)
        lines = chunk.split('\n')
        code_lines = [l for l in lines if l.strip() and not l.strip().startswith(('#', '//', '/*', '*', '///'))]
        if code_lines:
            code_ratio = len(code_lines) / len(lines)
            boost += min(code_ratio * 0.05, 0.05)  # Up to 0.05 for dense code

        # Error handling patterns
        if re.search(r'(try:|catch|except|throw|raise)', chunk):
            boost += 0.03

        # Control flow complexity
        control_flow_count = len(re.findall(r'\b(if|for|while|switch)\b', chunk))
        boost += min(control_flow_count * 0.01, 0.02)  # Up to 0.02 for complex logic

        return min(boost, 0.2)  # Cap at 0.2

    def _structural_boost(self, chunk_index, total_chunks):
        """Boost based on position and structure"""
        boost = 0.0

        # First chunk (often contains setup/imports)
        if chunk_index == 0:
            boost += 0.06

        # Last chunk (often contains main logic/conclusions)
        elif chunk_index == total_chunks - 1:
            boost += 0.06

        # Middle chunks with high index (potentially core logic)
        elif total_chunks > 5 and chunk_index >= total_chunks * 0.4:
            boost += 0.02

        return boost

    def _semantic_boost(self, chunk):
        """Semantic similarity boost using embeddings"""
        if not EMBEDDING_AVAILABLE or not self.embedding_generator:
            return 0.0

        try:
            # Generate embedding for this chunk
            chunk_embedding = self.embedding_generator.generate_embedding(chunk)
            if not chunk_embedding:
                return 0.0

            # Important semantic patterns for code
            important_patterns = [
                "function definition", "class definition", "main function",
                "API endpoint", "error handling", "database query",
                "business logic", "configuration", "test case"
            ]

            # Cache pattern embeddings to avoid recomputing
            if not self.semantic_patterns_cache:
                pattern_embeddings = self.embedding_generator.generate_embeddings_batch(important_patterns)
                self.semantic_patterns_cache = dict(zip(important_patterns, pattern_embeddings))

            # Calculate similarities
            similarities = []
            for pattern, pattern_embedding in self.semantic_patterns_cache.items():
                if pattern_embedding:
                    sim = cosine_similarity_simple(chunk_embedding, pattern_embedding)
                    similarities.append(sim)

            if similarities:
                max_similarity = max(similarities)
                return min(max_similarity * 0.2, 0.2)  # Scale to 0-0.2 range

        except Exception as e:
            print(f"Warning: Semantic boost failed: {e}")
            return 0.0

        return 0.0

    def _get_language_from_extension(self, ext: str) -> str:
        """Map file extension to programming language."""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.jsx': 'javascript',
            '.ts': 'typescript',
            '.tsx': 'typescript',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.cs': 'csharp',
            '.go': 'go',
            '.rb': 'ruby',
            '.php': 'php',
            '.rs': 'rust',
            '.swift': 'swift',
            '.kt': 'kotlin',
            '.scala': 'scala',
            '.sh': 'bash',
            '.html': 'html',
            '.css': 'css',
            '.scss': 'scss',
            '.xml': 'xml',
            '.json': 'json',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.md': 'markdown',
            '.rst': 'restructuredtext'
        }
        return language_map.get(ext.lower(), 'unknown')

    def _get_content_type_from_extension(self, ext: str) -> str:
        """Classify content type based on file extension."""
        if ext in self.code_exts:
            return 'code'
        elif ext in self.markdown_exts:
            return 'documentation'
        elif ext in self.html_exts:
            return 'web'
        elif ext in self.css_exts:
            return 'stylesheet'
        elif ext in self.json_exts:
            return 'data'
        elif ext in self.xml_exts:
            return 'markup'
        elif ext in self.data_exts:
            return 'dataset'
        else:
            return 'other'

    def _clean_chunk_content(self, chunk: str) -> str:
        """Clean up chunk content by removing unnecessary escape characters and formatting."""
        if not isinstance(chunk, str):
            return str(chunk)

        # Remove excessive whitespace and normalize line endings
        cleaned = chunk.strip()

        # Remove escape characters that make JSON ugly
        cleaned = cleaned.replace('\\n', '\n')
        cleaned = cleaned.replace('\\t', '\t')
        cleaned = cleaned.replace('\\"', '"')
        cleaned = cleaned.replace("\\'", "'")

        # Normalize multiple spaces to single spaces (but preserve indentation)
        lines = cleaned.split('\n')
        cleaned_lines = []
        for line in lines:
            # Only normalize spaces in non-indented lines
            if not line.startswith(' ') and not line.startswith('\t'):
                # Replace multiple spaces with single space
                line = re.sub(r' +', ' ', line)
            cleaned_lines.append(line)

        return '\n'.join(cleaned_lines)

    def _classify_chunk_type(self, chunk: str, ext: str) -> str:
        """Classify the type of chunk based on its content."""
        if ext in self.code_exts:
            if any(keyword in chunk.lower() for keyword in ['def ', 'function ', 'class ']):
                return 'function_definition'
            elif any(keyword in chunk.lower() for keyword in ['import ', 'from ', 'require']):
                return 'imports'
            elif any(keyword in chunk.lower() for keyword in ['if ', 'for ', 'while ', 'try:']):
                return 'logic'
            else:
                return 'implementation'
        elif ext in self.markdown_exts:
            if chunk.startswith('#'):
                return 'header'
            elif '```' in chunk:
                return 'code_block'
            else:
                return 'text'
        else:
            return 'content'

    def _chunk_contains_code(self, chunk: str, ext: str) -> bool:
        """Check if chunk contains code elements."""
        if ext in self.code_exts:
            return True

        # Check for code patterns in other file types
        code_indicators = ['```', 'function', 'def ', 'class ', 'import ', 'const ', 'let ', 'var ']
        return any(indicator in chunk for indicator in code_indicators)

    def _chunk_contains_documentation(self, chunk: str) -> bool:
        """Check if chunk contains documentation elements."""
        doc_indicators = ['# ', '/*', '*/', '"""', "'''", 'TODO', 'FIXME', 'NOTE:']
        return any(indicator in chunk for indicator in doc_indicators)

    def process_repository_parallel(self, repo_path: str, max_files: int = None) -> List[Dict[str, Any]]:
        """Process entire repository with parallel chunking for performance"""
        all_chunks = []

        # Find all supported files
        supported_files = []
        for root, dirs, files in os.walk(repo_path):
            for file in files:
                ext = os.path.splitext(file)[1].lower()
                if ext in self.code_exts | self.markdown_exts | self.html_exts | self.json_exts:
                    supported_files.append(os.path.join(root, file))

        if max_files:
            supported_files = supported_files[:max_files]

        # Process files in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {executor.submit(self.chunk_file_smart, file_path): file_path for file_path in supported_files}

            for future in as_completed(future_to_file):
                file_path = future_to_file[future]
                try:
                    chunks = future.result()
                    all_chunks.extend(chunks)
                except Exception as e:
                    print(f"Error processing {file_path}: {e}")

        return all_chunks

    def get_repository_stats(self, repo_path: str) -> Dict[str, Any]:
        """Get comprehensive repository statistics"""
        stats = {
            "total_files": 0,
            "supported_files": 0,
            "file_types": defaultdict(int),
            "languages": defaultdict(int),
            "total_chunks": 0,
            "total_tokens": 0,
            "avg_chunk_size": 0,
            "complexity_distribution": defaultdict(int)
        }

        for root, dirs, files in os.walk(repo_path):
            for file in files:
                stats["total_files"] += 1
                ext = os.path.splitext(file)[1].lower()

                if ext in self.code_exts | self.markdown_exts | self.html_exts | self.json_exts:
                    stats["supported_files"] += 1
                    stats["file_types"][ext] += 1

                    file_path = os.path.join(root, file)
                    try:
                        chunks = self.chunk_file_smart(file_path)
                        stats["total_chunks"] += len(chunks)

                        for chunk in chunks:
                            stats["total_tokens"] += chunk["metadata"]["token_count"]
                            complexity = chunk["metadata"]["complexity_score"]
                            complexity_bucket = round(complexity * 2) / 2  # Round to nearest 0.5
                            stats["complexity_distribution"][complexity_bucket] += 1

                        language = self._get_language_from_extension(ext)
                        stats["languages"][language] += 1

                    except Exception as e:
                        print(f"Error analyzing {file_path}: {e}")

        if stats["total_chunks"] > 0:
            stats["avg_chunk_size"] = stats["total_tokens"] / stats["total_chunks"]

        return dict(stats)
