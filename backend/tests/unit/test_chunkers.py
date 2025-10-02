import unittest
import tempfile
import os
import sys
from pathlib import Path

# Add the src directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from src.core.chunker.chunkers import Chunker

class TestChunkers(unittest.TestCase):

    def setUp(self):
        self.chunker = Chunker()

    def test_chunk_python_file(self):
        # Create a temporary Python file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
            f.write("""
def hello_world():
    print("Hello, world!")

class MyClass:
    def __init__(self):
        self.value = 42
""")
            temp_path = f.name

        try:
            chunks = self.chunker.chunk_file(temp_path)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
            for chunk in chunks:
                self.assertLessEqual(self.chunker.count_tokens(chunk), self.chunker.MAX_TOKENS)
        finally:
            os.unlink(temp_path)

    def test_chunk_markdown_file(self):
        # Create a temporary Markdown file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            f.write("""
# Introduction

This is a test markdown file.

## Section 1

Some content here.

## Section 2

More content.
""")
            temp_path = f.name

        try:
            chunks = self.chunker.chunk_file(temp_path)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
            for chunk in chunks:
                self.assertLessEqual(self.chunker.count_tokens(chunk), self.chunker.MAX_TOKENS)
        finally:
            os.unlink(temp_path)

    def test_chunk_json_file(self):
        # Create a temporary JSON file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            f.write('{"key": "value", "array": [1, 2, 3]}')
            temp_path = f.name

        try:
            chunks = self.chunker.chunk_file(temp_path)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
            for chunk in chunks:
                self.assertLessEqual(self.chunker.count_tokens(chunk), self.chunker.MAX_TOKENS)
        finally:
            os.unlink(temp_path)

    def test_chunk_csv_file(self):
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("name,age\nAlice,30\nBob,25\nCharlie,35")
            temp_path = f.name

        try:
            chunks = self.chunker.chunk_file(temp_path)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
            for chunk in chunks:
                self.assertLessEqual(self.chunker.count_tokens(chunk), self.chunker.MAX_TOKENS)
        finally:
            os.unlink(temp_path)

    def test_chunk_unsupported_file(self):
        # Create a temporary unsupported file (e.g., .txt for summary)
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            f.write("This is a plain text file.")
            temp_path = f.name

        try:
            chunks = self.chunker.chunk_file(temp_path)
            self.assertIsInstance(chunks, list)
            self.assertGreater(len(chunks), 0)
            for chunk in chunks:
                self.assertLessEqual(self.chunker.count_tokens(chunk), self.chunker.MAX_TOKENS)
        finally:
            os.unlink(temp_path)

    def test_chunk_nonexistent_file(self):
        # Test with a non-existent file
        chunks = self.chunker.chunk_file('/nonexistent/file.py')
        self.assertIsInstance(chunks, list)
        self.assertEqual(len(chunks), 1)
        self.assertIn("Error reading", chunks[0]['content'])

    def test_count_tokens(self):
        text = "Hello, world!"
        tokens = self.chunker.count_tokens(text)
        self.assertIsInstance(tokens, int)
        self.assertGreater(tokens, 0)

    def test_re_chunk_if_oversize(self):
        # Create a large chunk that exceeds MAX_TOKENS
        large_text = "word " * 10000  # Likely to exceed token limit
        sections = [large_text]
        chunks = self.chunker.re_chunk_if_oversize(sections)
        self.assertIsInstance(chunks, list)
        for chunk in chunks:
            self.assertLessEqual(self.chunker.count_tokens(chunk), self.chunker.MAX_TOKENS)

if __name__ == '__main__':
    unittest.main()