"""
Advanced Data Model for CodeChat Semantic Search

This module defines the data model for storing code chunks in Pinecone.
The model is designed to be semantically rich to improve the quality of
retrieval for Retrieval-Augmented Generation (RAG).

The goal is to move from a flat metadata structure to a hierarchical and
semantically aware model that captures not just the code, but its context,
purpose, and relationships.
"""

# --- Vector ID Structure ---
# A composite key for uniqueness and easy parsing.
# Format: f"{repo_name}:{file_path}:{chunk_type}:{start_line}-{end_line}"
# Example: "modelearth/codechat:src/core/smart_chunker.py:function:10-45"

# --- Metadata Structure ---

METADATA_STRUCTURE = {
    # 1. Identity & Location (Who and Where)
    "repo_name": "string",          # e.g., "modelearth/codechat"
    "file_path": "string",          # e.g., "src/core/smart_chunker.py"
    "namespace": "string",          # The Pinecone namespace, e.g., "codechat"
    "commit_sha": "string",         # e.g., "fbd509496f6d865d..."
    "timestamp": "float",           # Unix timestamp of ingestion for TTL and relevance

    # 2. Content & Semantics (What and Why)
    "chunk_content": "string",      # The actual code or text of the chunk
    "chunk_type": "string",         # Enum: ["file_docstring", "function", "class", "method", "interface", "test", "markdown", "code_block"]
    "language": "string",           # e.g., "python", "javascript"
    "summary": "string",            # AI-generated summary of the chunk's purpose and functionality.
    "tags": ["list", "of", "strings"], # AI-generated tags (e.g., "api-client", "data-processing", "authentication")

    # 3. Structural & Relational Context (How it fits)
    "parent_chunk_id": "string",    # ID of the parent chunk (e.g., a class for a method)
    "child_chunk_ids": ["list", "of", "strings"], # IDs of nested chunks
    "dependencies": {               # Code dependencies
        "imports": ["list", "of", "modules"], # e.g., ["os", "boto3"]
        "calls": ["list", "of", "functions"]  # Functions/methods called by this chunk
    },
    "line_start": "integer",
    "line_end": "integer",

    # 4. Quality & Ranking Signals (How important)
    "code_complexity": "integer",   # Cyclomatic complexity or similar metric
    "token_count": "integer",       # Number of tokens in the chunk
    "has_docstring": "boolean",     # True if the function/class has a docstring
    "docstring_quality": "float",   # AI-rated score (0.0 to 1.0) of the docstring quality
    "centrality_score": "float",    # A score indicating how central this file/module is to the repo (e.g., based on imports)
    
    # 5. Status & Tracking
    "processed": "boolean",         # Flag to indicate if the repository has been processed
    "tracked": "boolean",           # Flag to indicate if the repository is actively tracked for updates
    "live": "boolean"               # Used for atomic updates, True if this is the current version
}

# --- Example of a Populated Vector ---
"""
{
    "id": "modelearth/codechat:src/core/pine.py:class:15-80",
    "values": [0.1, 0.2, ..., 0.n],
    "metadata": {
        "repo_name": "modelearth/codechat",
        "file_path": "src/core/pine.py",
        "namespace": "codechat",
        "commit_sha": "a1b2c3d4",
        "timestamp": 1758820000.0,
        
        "chunk_content": "class PineconeClient:\n    def __init__(self):\n        ...",
        "chunk_type": "class",
        "language": "python",
        "summary": "A client to interact with the Pinecone vector database, handling initialization, upserting, and querying of vectors.",
        "tags": ["pinecone", "vector-db", "api-client"],
        
        "parent_chunk_id": "modelearth/codechat:src/core/pine.py:file_docstring:1-10",
        "child_chunk_ids": [
            "modelearth/codechat:src/core/pine.py:method:20-35",
            "modelearth/codechat:src/core/pine.py:method:38-80"
        ],
        "dependencies": {
            "imports": ["os", "pinecone"],
            "calls": ["pinecone.Pinecone", "pinecone.Index"]
        },
        "line_start": 15,
        "line_end": 80,
        
        "code_complexity": 5,
        "token_count": 350,
        "has_docstring": true,
        "docstring_quality": 0.85,
        "centrality_score": 0.9,

        "processed": true,
        "tracked": true,
        "live": true
    }
}
"""

# --- How this solves the problems ---
#
# 1. Below Average Performance:
#    - The old model was too flat. The new model's `summary`, `tags`, and `dependencies`
#      provide much richer semantic context for the RAG model to generate accurate answers.
#    - `centrality_score` and `docstring_quality` allow us to rank results, prioritizing
#      important and well-documented code.
#
# 2. Responding to Generic Queries:
#    - Generic queries often relate to core concepts. The `centrality_score` helps
#      surface foundational modules.
#    - AI-generated `summary` and `tags` provide a higher-level understanding of the code,
#      matching the abstraction level of a generic query.
#
# 3. Semantic Chunking and Retrieval:
#    - `chunk_type` allows us to differentiate between high-level documentation and low-level code.
#    - `parent_chunk_id` and `child_chunk_ids` allow the retrieval system to "zoom in" or "zoom out",
#      fetching related context (e.g., the whole class for a method, or just the method's docstring).
#
# 4. Tracking Processed Repositories:
#    - The `processed` and `tracked` flags are now part of the metadata, allowing for
#      easy filtering and management directly within the ingestion scripts.
#
# --- Implementation Plan ---
#
# 1. Update `ingestion.py`:
#    - Read the `tracked` and `processed` flags from `modelearth_repos.yml`.
#    - Only clone and process repositories where `tracked: true`.
#    - After successful processing, update the `processed` flag in the YAML file.
#
# 2. Enhance `SmartChunker` (or a new processing pipeline):
#    - Generate AI summaries and tags for each chunk.
#    - Calculate complexity, token count, and docstring metrics.
#    - Determine parent/child relationships and dependencies.
#    - Calculate a centrality score for each file/module.
#
# 3. Update `ingestion_worker` and `query_handler` Lambdas:
#    - The ingestion worker will be responsible for creating vectors with this new rich metadata.
#    - The query handler can use the new metadata fields for more advanced filtering and ranking,
#      and can construct a more comprehensive context for the RAG model.
#
# This advanced data model provides a solid foundation for a much more powerful and
# accurate semantic search over your codebase.
