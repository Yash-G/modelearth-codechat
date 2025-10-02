#!/usr/bin/env python3

import os
import sys
from pathlib import Path

# Add the project root directory to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.core.chunker.chunkers import Chunker

def main():
    chunker = Chunker()

    dummy_dir = Path(__file__).parent / 'test_extension' / 'input'
    output_dir = Path(__file__).parent / 'test_extension' / 'output'

    print(dummy_dir, output_dir)

    if not dummy_dir.exists():
        print("Test extension directory not found!")
        return

    output_dir.mkdir(exist_ok=True)

    for file_path in dummy_dir.glob('*'):
        if file_path.is_file():
            print(f"Processing {file_path.name}...")
            try:
                chunks = chunker.chunk_file(str(file_path))
                op_path = file_path.name.replace('.', '_')
                output_file = output_dir / f"{op_path}_chunks.txt"
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(f"Chunks for {file_path.name}:\n\n")
                    for i, chunk in enumerate(chunks, 1):
                        f.write(f"Chunk {i}:\n{chunk}\n\n{'-'*50}\n\n")

                print(f"Saved chunks to {output_file}")

            except Exception as e:
                print(f"Error processing {file_path.name}: {e}")

if __name__ == '__main__':
    main()
