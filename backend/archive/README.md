# Backend Archived Code

This directory contains backend source code that has been moved to archive during codebase reorganization.

## 📦 Archived Directories

### `src/`
Contains unused or legacy source code modules:

- **`utils/`** - Development and testing utilities
  - `restore.py` - Data restoration utilities
  - `run_chunker_demo.py` - Chunker demonstration script
  - `rag_query_test.py` - RAG query testing script

- **`web/`** - Legacy web interface components
  - Old web-based interface files
  - Frontend components that are no longer used

## 🎯 Why These Were Archived

### Utils Directory
- Contains development/testing scripts not used in production
- Utilities that were useful during development but not needed for Lambda deployment
- Testing scripts that have been superseded by newer implementations

### Web Directory  
- Legacy web interface components
- Replaced by the current `chat/` directory frontend
- Historical interface implementations

## 🔍 Finding Current Code

For current active code, see:
- **Active Lambda functions**: `../src/lambdas/`
- **Core modules**: `../src/core/`
- **Frontend**: `../../chat/`
- **Infrastructure**: `../infra/`

## 📅 Archive Information

- **Archive date**: 2025-09-25
- **Reason**: Codebase cleanup and organization
- **Status**: Preserved for historical reference

## 📝 Usage Notes

If you need functionality from these archived files:
1. Check if equivalent functionality exists in current codebase
2. Consider whether the archived code is still compatible
3. Review for security and dependency updates before use
4. Test thoroughly if reintegrating any archived code

## 🗂️ File Inventory

### Utils Scripts
- Development utilities and testing scripts
- Demo applications for core features
- Legacy query testing implementations

### Web Components
- Historical frontend implementations
- Legacy UI components
- Outdated web interface files

These files remain accessible for reference but are not part of the active codebase.