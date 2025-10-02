# CodeChat Archive

This directory contains files that were removed during code cleanup to keep the active codebase focused only on production components.

## Archived Items

### Documentation
- `src_README.md` - Original src directory documentation, now covered by consolidated docs in `docs/`

### Legacy Files Location
- `backend/archive/` - Contains previously archived utility scripts and legacy components
  - `src/utils/` - Development utilities like `run_chunker_demo.py` and `rag_query_test.py`
  - `src/web/` - Legacy web interface components

### Cleanup Summary

**Removed from active codebase:**
1. **Redundant Documentation**: `src/README.md` moved here as it was covered by consolidated documentation
2. **Duplicate Scripts**: Removed `backend/scripts/` directory as all scripts moved to root `scripts/`

**Kept in active codebase:**
- ✅ `src/core/pine.py` - Pinecone client used by ingestion_worker and ingestion.py
- ✅ `src/core/smart_chunker/` - Main orchestrator for 40+ language chunkers
- ✅ `src/core/embedding_generator.py` - OpenAI embeddings integration
- ✅ `src/core/chunking/` - All 50+ language-specific chunkers (essential for code processing)
- ✅ All 4 Lambda functions in `src/lambdas/`
- ✅ `backend/tests/` - Unit and integration tests for chunking system
- ✅ `ingestion.py` - Production bulk ingestion script

**Fixed Issues:**
- 🔧 Corrected import path in `ingestion_worker/index.py` from `core.chunking.smart_chunker` to `core.smart_chunker`

## Active Module Usage

| Module | Used By | Purpose |
|--------|---------|---------|
| `pine.py` | ingestion_worker, ingestion.py | Pinecone vector database operations |
| `smart_chunker/` | ingestion_worker, ingestion.py | Orchestrates all language-specific chunkers |
| `embedding_generator.py` | ingestion_worker, ingestion.py | OpenAI embeddings generation |
| `chunking/*` | smart_chunker | 40+ language-specific code chunkers |

## Notes

- The `query_handler` Lambda uses direct Pinecone/OpenAI clients for performance (not core modules)
- All chunking modules are essential and actively used by the SmartChunker system
- Tests are kept in `backend/tests/` as they validate the chunking functionality
- No unused code was found in the active production paths

The codebase is now lean and focused only on production components.