# Lambda Layers - Clean Structure

This directory contains only the essential Lambda layer artifacts for CodeChat.

## Current Structure

### Active Files
- **`lambda-layer-query-handler.zip`** - Built layer with dependencies for the query_handler Lambda.
- **`lambda_layer_query_handler_requirements.txt`** - Dependency list (pinecone, openai, google-generativeai, PyYAML).
- **`build_layers.py`** - Cross-platform build script that generates the layer zip.

### Layer Assignment
- **query_handler Lambda** - Uses `lambda-layer-query-handler.zip` because it needs AI/vector DB dependencies.
- **get_repositories Lambda** - Uses only the Python standard library, so no external layer is required.

## Building Layers

```bash
# Build the query-handler layer
python build_layers.py

# Build and publish to AWS
python build_layers.py --publish
```
