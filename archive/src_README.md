# CodeChat Backend Source Code

This directory contains the core source code for the CodeChat Lambda functions and supporting modules.

## Directory Structure

### 📁 `lambdas/`
Contains the AWS Lambda function implementations:

- **`query_handler/`** - Handles RAG (Retrieval Augmented Generation) queries
  - Processes user questions using Pinecone vector search
  - Generates responses using Google Gemini or OpenAI models
  - Returns contextual answers based on indexed code

- **`ingestion_worker/`** - Processes repositories for code indexing
  - Clones repositories from GitHub
  - Uses SmartChunker for intelligent code segmentation
  - Generates embeddings and stores them in Pinecone
  - Handles SQS queue processing for batch ingestion

- **`ingestion_webhook/`** - GitHub webhook endpoint
  - Receives GitHub webhook notifications
  - Queues repository processing jobs in SQS
  - Handles repository update events

- **`get_repositories/`** - Returns available repositories
  - Simple endpoint to list available repositories
  - Used by frontend to populate repository dropdown

### 📁 `core/`
Core modules shared by Lambda functions:

- **`pine.py`** - Pinecone vector database client
  - Handles connection and operations with Pinecone
  - Manages vector storage and retrieval

- **`embedding_generator.py`** - Text embedding generation
  - Creates vector embeddings from text using OpenAI
  - Supports various embedding models

- **`smart_chunker/`** - Intelligent code chunking system
  - **`smart_chunker.py`** - Main chunking orchestrator
  - **`__init__.py`** - Module initialization
  - Breaks code into meaningful, semantically coherent chunks
  - Supports multiple programming languages

- **`chunking/`** - Language-specific chunkers
  - Contains specialized chunkers for different programming languages
  - Each chunker understands language-specific syntax and semantics
  - Enables context-aware code segmentation

## Dependencies

### Lambda Function Dependencies
- **Query Handler**: `pinecone`, `openai`, `google-generativeai`
- **Ingestion Worker**: `GitPython`, `boto3`, `pinecone`, `openai`, `tiktoken`
- **Ingestion Webhook**: `boto3`
- **Get Repositories**: No external dependencies (uses Python stdlib)

### Core Module Dependencies
- **Smart Chunker**: `tiktoken`, `numpy` (optional), Tree-sitter (for advanced parsing)
- **Pine**: `pinecone`
- **Embedding Generator**: `openai`

## Usage

These modules are designed to be used within AWS Lambda functions. The Lambda layer system provides the necessary dependencies, while the core modules handle the business logic.

### Import Pattern
```python
# In Lambda functions
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.pine import PineconeClient
from core.smart_chunker import SmartChunker
from core.embedding_generator import EmbeddingGenerator
```

## Architecture Notes

- **Modular Design**: Core functionality is separated into reusable modules
- **Lambda Optimized**: Designed for serverless execution with cold start considerations
- **Scalable**: Uses SQS for asynchronous processing of large repositories
- **Resilient**: Handles errors gracefully with proper logging

## Archived Files

Unused files have been moved to `../archive/src/` including:
- `utils/` - Utility scripts for development/testing
- `web/` - Legacy web interface components

## Bulk Ingestion

For initial setup, use the bulk ingestion script to process all repositories:

```bash
# From project root
python ingestion.py
```

See `../BULK_INGESTION.md` for detailed instructions on bulk repository processing.