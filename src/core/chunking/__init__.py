"""
Chunking Module for CodeChat

This module provides comprehensive chunking support for all programming languages
supported by tree-sitter, with semantic-aware chunking and metadata extraction.
"""

from .base import BaseChunker, LanguageChunker, TreeSitterChunker
from .utils import *

# Import all language-specific chunkers
from .chunk_python import PythonChunker
from .chunk_javascript import JavaScriptChunker
from .chunk_typescript import TypeScriptChunker
from .chunk_java import JavaChunker
from .chunk_cpp import CppChunker
from .chunk_c import CChunker
from .chunk_go import GoChunker
from .chunk_rust import RustChunker
from .chunk_php import PhpChunker
from .chunk_ruby import RubyChunker
from .chunk_csharp import CSharpChunker
from .chunk_kotlin import KotlinChunker
from .chunk_swift import SwiftChunker
from .chunk_scala import ScalaChunker
from .chunk_haskell import HaskellChunker
from .chunk_lua import LuaChunker
from .chunk_perl import PerlChunker
from .chunk_r import RChunker
from .chunk_julia import JuliaChunker
from .chunk_dart import DartChunker
from .chunk_elixir import ElixirChunker
from .chunk_erlang import ErlangChunker
from .chunk_clojure import ClojureChunker
from .chunk_scheme import SchemeChunker
from .chunk_common_lisp import CommonLispChunker
from .chunk_emacs_lisp import EmacsLispChunker
from .chunk_vim_script import VimScriptChunker
from .chunk_shell import ShellChunker
from .chunk_powershell import PowerShellChunker
from .chunk_dockerfile import DockerfileChunker
from .chunk_yaml import YamlChunker
from .chunk_json import JsonChunker
from .chunk_xml import XmlChunker
from .chunk_html import HtmlChunker
from .chunk_css import CssChunker
from .chunk_scss import ScssChunker
from .chunk_less import LessChunker
from .chunk_markdown import MarkdownChunker
from .chunk_latex import LatexChunker
from .chunk_bibtex import BibtexChunker
from .chunk_sql import SqlChunker
from .chunk_graphql import GraphQLChunker
from .chunk_dockercompose import DockerComposeChunker
from .chunk_toml import TomlChunker
from .chunk_ini import IniChunker
from .chunk_properties import PropertiesChunker
from .chunk_generic import GenericChunker

__all__ = [
    'BaseChunker',
    'LanguageChunker',
    'TreeSitterChunker',
    'PythonChunker',
    'JavaScriptChunker',
    'TypeScriptChunker',
    'JavaChunker',
    'CppChunker',
    'CChunker',
    'GoChunker',
    'RustChunker',
    'PhpChunker',
    'RubyChunker',
    'CSharpChunker',
    'KotlinChunker',
    'SwiftChunker',
    'ScalaChunker',
    'HaskellChunker',
    'LuaChunker',
    'PerlChunker',
    'RChunker',
    'JuliaChunker',
    'DartChunker',
    'ElixirChunker',
    'ErlangChunker',
    'ClojureChunker',
    'SchemeChunker',
    'CommonLispChunker',
    'EmacsLispChunker',
    'VimScriptChunker',
    'ShellChunker',
    'PowerShellChunker',
    'DockerfileChunker',
    'YamlChunker',
    'JsonChunker',
    'XmlChunker',
    'HtmlChunker',
    'CssChunker',
    'ScssChunker',
    'LessChunker',
    'MarkdownChunker',
    'LatexChunker',
    'BibtexChunker',
    'SqlChunker',
    'GraphQLChunker',
    'DockerComposeChunker',
    'TomlChunker',
    'IniChunker',
    'PropertiesChunker',
    'GenericChunker'
    'GenericChunker'
]
