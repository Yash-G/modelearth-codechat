# Test Extension Files

This folder contains example files and their corresponding chunk outputs used for testing the CodeChat chunking functionality.

## File Types

### Source Files
- `example.{extension}` - Sample source files for various programming languages and formats
- Supported extensions: cpp, css, csv, html, java, js, json, jsx, md, py, sh, ts

### Chunk Output Files
- `example_{extension}_chunks.txt` - Chunked output for the corresponding source file
- `example_chunks.txt` - General chunks file (if applicable)

## Usage

These files are used by:
- `run_chunker_demo.py` - Demonstrates chunking functionality
- Unit tests in `../unit/test_chunkers.py` - Validates chunking logic
- Integration tests - End-to-end testing

## Adding New Test Files

1. Add your example source file as `example.{new_extension}`
2. Run the chunker on it to generate `example_{new_extension}_chunks.txt`
3. Update any relevant tests to include the new file type
