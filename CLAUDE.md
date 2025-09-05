# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

CodeChat is a RAG (Retrieval-Augmented Generation) pipeline that enables querying across ModelEarth's codebase ecosystem. The system chunks repository files using Tree-sitter, embeds them with OpenAI's `text-embedding-3-small`, stores them in Pinecone VectorDB, and provides a chat interface for developer queries using Gemini 1.5 Flash.

## Architecture

### Core Components
- **RAG Pipeline**: Python-based ingestion using Tree-sitter for code parsing
- **Vector Database**: Pinecone with namespaced repositories
- **Chat Frontend**: Vanilla JavaScript web interface (`chat/`)
- **Backend**: AWS Lambda (to be implemented) for query processing
- **Sync System**: GitHub Actions workflow for VectorDB updates

### Directory Structure
```
codechat/
├── rag_query_test.py           # Test script for RAG functionality
├── ingestion/
│   └── rag_ingestion_pipeline.ipynb  # Jupyter notebook for data processing
├── chat/
│   ├── index.html              # Chat interface
│   └── script.js              # Frontend JavaScript
└── requirements.txt            # Python dependencies
```

## Development Commands

### Environment Setup
```bash
# Create and activate virtual environment
python3 -m venv env
source env/bin/activate  # Mac/Linux
# env\Scripts\activate.bat  # Windows

# Install dependencies
pip install -r requirements.txt
```

### Running the RAG System
```bash
# Test RAG queries (requires API keys in .env)
python rag_query_test.py

# Start local HTTP server for chat interface
python -m http.server 8887
# Navigate to http://localhost:8887/chat/
```

### Required API Keys
Create `.env` file from `.env.example` with:
- `PINECONE_API_KEY`: For vector database operations
- `OPENAI_API_KEY`: For embedding generation
- `GOOGLE_API_KEY`: For Gemini responses

## Code Architecture

### RAG Pipeline (`ingestion/rag_ingestion_pipeline.ipynb`)
**File Processing Strategy**: The pipeline supports comprehensive file type handling:

| File Category | Extensions | Chunking Method | Purpose |
|---------------|------------|-----------------|---------|
| Code | `.py`, `.js`, `.ts`, `.jsx`, `.tsx`, `.java`, `.cpp`, `.c`, `.cs`, `.go`, `.rb`, `.php`, `.rs`, `.swift`, `.kt`, `.scala`, `.sh` | Tree-sitter AST parsing (functions, classes, methods) | Semantic code understanding |
| Notebooks | `.ipynb` | Cell-based splitting (code + markdown) | Interactive analysis content |
| HTML/XML | `.html`, `.xml`, `.xsd`, `.xsl` | Tree-sitter DOM-based elements | Structural markup segments |
| Text/Docs | `.md`, `.txt`, `.rst`, `.adoc`, `.mdx` | Header-based sectioning | Documentation content |
| Data | `.csv`, `.tsv`, `.xls`, `.xlsx`, `.parquet`, `.feather` | Column preview + sample rows | Data structure understanding |
| Config | `.json`, `.yaml`, `.yml`, `.jsonl` | Recursive key-level splitting | Configuration insights |
| Stylesheets | `.css`, `.scss`, `.sass`, `.less` | Tree-sitter style rules | UI styling logic |
| Binary/Media | Images, fonts, executables | Metadata summary only | File inventory |

**Chunking Logic**:
- **Token Limit**: 8,192 tokens per chunk (configurable)
- **Re-chunking**: Oversized content gets semantically split by sentences, then hard-split if needed
- **Metadata**: Each chunk includes `repo_name`, `file_path`, `file_type`, `chunk_type`, `line_range`, `content`

### Query System (`rag_query_test.py`)
**Multi-namespace Search**: Queries all Pinecone namespaces simultaneously
- **Per-namespace results**: 3-5 chunks per repository
- **Global ranking**: Combines and ranks by similarity score
- **Prompt Engineering**: Strict grounding in retrieved context with file path references

### Chat Interface (`chat/script.js`)
**Features**:
- Repository-scoped queries via dropdown
- Conversation persistence in localStorage
- Code block highlighting and copy functionality
- Responsive sidebar design
- Mock/development mode with fallback responses

**API Integration**: Designed for AWS Lambda backend (endpoint configurable)

## Development Workflow

### Adding New Repositories
1. Update `REPOS` dictionary in ingestion notebook with local paths
2. Run chunking and embedding cells
3. Upsert to Pinecone with repository-specific namespace
4. Update frontend repository dropdown

### File Type Support
When adding new file extensions:
1. Define extension set in appropriate category (e.g., `code_exts`, `markdown_exts`)
2. Implement chunking strategy in `dispatch_chunking()`
3. Update file type handling table in documentation
4. Test with representative files

### Vector Database Management
- **Namespaces**: One per repository (e.g., `ModelEarth_localsite`)
- **Index**: `model-earth-jam-stack` (1536 dimensions, cosine similarity)
- **Batch Size**: 10-20 records per upsert operation
- **Metadata Limits**: 40KB per chunk (content gets truncated if needed)

### GitHub Actions Integration
The system uses `vector_sync.yml` workflow for automatic VectorDB updates:
- **Trigger**: PR merges to main branch
- **Process**: Detects changed files, re-chunks, re-embeds, updates Pinecone
- **Strategy**: Replace vectors by `file_path` metadata for incremental updates

## Testing and Debugging

### RAG Query Testing
```bash
python rag_query_test.py
# Tests predefined questions against the knowledge base
# Outputs similarity scores and retrieved contexts
```

### Chat Interface Development
- **Mock Mode**: Frontend works without Lambda backend
- **Local Testing**: Use Python HTTP server for static file serving
- **API Endpoint**: Update `apiEndpoint` in `script.js` for production

### Common Issues
- **Token Limits**: Monitor chunk sizes with tokenizer validation
- **Tree-sitter Setup**: Requires compiled language grammars in specified path
- **Metadata Size**: Large content chunks may exceed Pinecone limits
- **API Rate Limits**: Implement backoff for OpenAI/Gemini API calls

## Integration with ModelEarth Ecosystem

This repository is part of the ModelEarth webroot system:
- **Submodule Integration**: Processes content from all webroot submodules
- **Cross-repository Queries**: Enables searching across the entire codebase
- **Documentation Hub**: Serves as knowledge base for developer onboarding

The RAG system provides semantic search capabilities across:
- Core utilities (`localsite`)
- Data visualization components (`comparison`, `io`)
- API services (`team` Rust backend)
- Documentation and project information (`projects`, `home`)