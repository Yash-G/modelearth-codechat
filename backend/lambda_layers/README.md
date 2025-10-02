# Lambda Layers - Clean Structure

This directory contains only the essential Lambda layers for CodeChat.

## Current Structure

### Active Files
- **`lambda-layer-query-handler.zip`** - Built layer with dependencies for query_handler Lambda
- **`lambda_layer_query_handler_requirements.txt`** - Dependencies: pinecone, openai, google-generativeai, PyYAML
- **`build_layers.sh`** - Clean build script for creating the query-handler layer

### Layer Assignment
- **query_handler Lambda** → Uses `lambda-layer-query-handler.zip` (needs AI/vector DB dependencies)
- **get_repositories Lambda** → No layer needed (uses only Python standard library)

## Building Layers

```bash
# Build the query-handler layer
./build_layers.sh

# Build and publish to AWS
./build_layers.sh --publish
```