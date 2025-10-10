#!/usr/bin/env python3
"""
Bulk Repository Ingestion Script

This script reads repository configurations from YAML files and processes them
for chunking and vector storage using the comprehensive language-specific chunkers.

This script runs standalone - just execute it directly:
    python bulk_ingestion.py
"""

import yaml
import json
import sys
import os
import boto3
from pathlib import Path
from typing import List, Dict, Any

# Configuration - Edit these values as needed
DEFAULT_CONFIG_FILE = "config/modelearth_repos.yml"
PROCESSING_MODE = "local"  # "local" or "lambda"

# Processing options
BATCH_SIZE = 100  # Number of vectors to upload in each batch
MAX_WORKERS = 4   # Parallel processing threads
VERBOSE = True    # Show detailed processing info

# Environment variable defaults
DEFAULT_NAMESPACE = "codechat-main"

# Add the src directory to Python path for local imports
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src"))

def load_repository_config(config_file: str) -> Dict[str, Any]:
    """Load repository configuration from YAML file."""
    with open(config_file, 'r') as f:
        config = yaml.safe_load(f)
    
    if 'repositories' in config:
        return config
    else:
        # Simple format: list of URLs
        repositories = [{'url': url, 'name': url.split('/')[-2] + '/' + url.split('/')[-1].replace('.git', '')} 
                       for url in config if isinstance(url, str)]
        return {
            'repositories': repositories,
            'processing': {'default_namespace': DEFAULT_NAMESPACE}
        }

def normalize_repository_entry(repo_entry) -> Dict[str, str]:
    """Normalize repository entry to standard format."""
    if isinstance(repo_entry, str):
        # Simple URL format
        url = repo_entry
        if url.endswith('.git'):
            name = '/'.join(url.replace('.git', '').split('/')[-2:])
        else:
            name = '/'.join(url.split('/')[-2:])
        namespace = name.split('/')[-1]  # Use repo name as namespace
        return {'url': url, 'name': name, 'namespace': namespace}
    
    elif isinstance(repo_entry, dict):
        # Detailed configuration format
        url = repo_entry.get('url', '')
        name = repo_entry.get('name', '')
        namespace = repo_entry.get('namespace', '')
        
        if not name and url:
            if url.endswith('.git'):
                name = '/'.join(url.replace('.git', '').split('/')[-2:])
            else:
                name = '/'.join(url.split('/')[-2:])
        
        if not namespace:
            namespace = name.split('/')[-1] if name else ''
            
        return {'url': url, 'name': name, 'namespace': namespace}
    
    else:
        raise ValueError(f"Invalid repository entry format: {repo_entry}")

def process_local_ingestion(config: Dict[str, Any]):
    """Process repositories using local ingestion worker code."""
    try:
        # Import local ingestion modules
        from src.core.pine import PineconeClient
        from src.core.smart_chunker import SmartChunker
        from src.core.embedding_generator import EmbeddingGenerator
        import tempfile
        from git import Repo
        
        repositories = config.get('repositories', [])
        processing_config = config.get('processing', {})
        default_namespace = processing_config.get('default_namespace', DEFAULT_NAMESPACE)
        
        print("🚀 Starting local bulk ingestion...")
        print("📊 Using comprehensive chunking system with language-specific chunkers")
        print(f"🏷️  Using individual namespaces per repository")
        
        # Get OpenAI API key
        openai_api_key = os.environ.get('OPENAI_API_KEY')
        if not openai_api_key:
            print("❌ OPENAI_API_KEY environment variable not set.")
            sys.exit(1)

        # Initialize clients
        pinecone_client = PineconeClient()
        chunker = SmartChunker(max_workers=MAX_WORKERS)
        embed_generator = EmbeddingGenerator(api_key=openai_api_key)
        
        # Show chunking system stats
        stats = chunker.get_chunking_stats()
        print(f"   • Supported languages: {stats['supported_languages']}")
        print(f"   • Tree-sitter languages: {stats['tree_sitter_languages']}")
        print(f"   • Pattern-based languages: {stats['pattern_based_languages']}")
        
        for repo_entry in repositories:
            # Skip repositories that are not tracked or already processed
            if not repo_entry.get('tracked', False) or repo_entry.get('processed', False):
                print(f"\n🚫 Skipping repository: {repo_entry.get('name', 'N/A')} (Tracked: {repo_entry.get('tracked', False)}, Processed: {repo_entry.get('processed', False)})")
                continue

            repo_config = normalize_repository_entry(repo_entry)
            repo_url = repo_config['url']
            repo_name = repo_config['name']
            repo_namespace = repo_config['namespace'] or default_namespace
            
            print(f"\n📁 Processing repository: {repo_name}")
            print(f"   URL: {repo_url}")
            print(f"   Namespace: {repo_namespace}")
            
            try:
                # Process repository (similar to ingestion_worker logic)
                with tempfile.TemporaryDirectory() as temp_dir:
                    repo_path = Path(temp_dir) / "repo"
                    print(f"   Cloning to: {repo_path}")
                    
                    # Clone repository
                    repo = Repo.clone_from(repo_url, str(repo_path))
                    commit_sha = repo.head.commit.hexsha
                    print(f"   Latest commit: {commit_sha[:8]}")
                    
                    all_vectors = []
                    processed_files = 0
                    language_stats = {}
                    
                    # Process files using the comprehensive chunking system
                    for file_path in repo_path.rglob('*'):
                        if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                            # Skip binary files
                            binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp', 
                                               '.pdf', '.zip', '.tar', '.gz', '.so', '.dll', '.exe', '.bin', '.dat'}
                            if file_path.suffix.lower() in binary_extensions:
                                continue
                                
                            try:
                                relative_path = file_path.relative_to(repo_path)
                                if VERBOSE:
                                    print(f"   Processing: {relative_path}")
                                
                                # Use the SmartChunker to process file with language-specific chunkers
                                chunks = chunker.chunk(str(file_path))
                                
                                if chunks:
                                    # Track language statistics
                                    file_ext = file_path.suffix
                                    language_stats[file_ext] = language_stats.get(file_ext, 0) + 1
                                    
                                    # Filter out empty chunks and generate embeddings for valid chunks only
                                    valid_chunks = [chunk for chunk in chunks if chunk.get('content', '').strip()]
                                    if not valid_chunks:
                                        continue
                                        
                                    chunk_contents = [chunk['content'].strip() for chunk in valid_chunks]
                                    embeddings = embed_generator.generate_embeddings_batch(chunk_contents)
                                    
                                    # Convert chunks to vectors with the new advanced data model
                                    for i, chunk in enumerate(valid_chunks):
                                        if embeddings[i] is not None:  # Only process if embedding was successful
                                            vector_id = f"{repo_name}:{relative_path}:{chunk.get('type', 'code')}:{chunk.get('start_line', 0)}-{chunk.get('end_line', 0)}"
                                            vector = {
                                                'id': vector_id,
                                                'values': embeddings[i],
                                                'metadata': {
                                                    # 1. Identity & Location (Who and Where)
                                                    'repo_name': repo_name,
                                                    'file_path': str(relative_path),
                                                    'namespace': repo_namespace,
                                                    'commit_sha': commit_sha,
                                                    'timestamp': float(os.path.getmtime(file_path)),
                                                    
                                                    # 2. Content & Semantics (What and Why)
                                                    'chunk_content': str(chunk['content']),  # Store as raw string, no escaping
                                                    'chunk_type': chunk.get('type', 'code'),
                                                    'language': chunk.get('language', ''),
                                                    'summary': f"Code chunk from {relative_path} containing {chunk.get('type', 'code')}", # AI-generated summary placeholder
                                                    'tags': [chunk.get('language', ''), chunk.get('type', 'code')], # Language and type as tags
                                                    
                                                    # 3. Structural & Relational Context (How it fits)
                                                    'parent_chunk_id': '',  # Placeholder for parent relationships
                                                    'child_chunk_ids': '',  # JSON string of child relationships
                                                    'dependencies_imports': '',  # Comma-separated list of imports
                                                    'dependencies_calls': '',   # Comma-separated list of function calls
                                                    'line_start': int(chunk.get('start_line', 0)),
                                                    'line_end': int(chunk.get('end_line', 0)),
                                                    
                                                    # 4. Quality & Ranking Signals (How important)
                                                    'code_complexity': 0,  # Cyclomatic complexity placeholder
                                                    'token_count': len(chunk['content'].split()),
                                                    'has_docstring': 'docstring' in chunk.get('type', '').lower() or '"""' in chunk['content'] or "'''" in chunk['content'],
                                                    'docstring_quality': 0.5 if ('"""' in chunk['content'] or "'''" in chunk['content']) else 0.0,
                                                    'centrality_score': 0.5,  # Default centrality, can be calculated later
                                                    
                                                    # 5. Status & Tracking
                                                    'processed': True,
                                                    'tracked': repo_entry.get('tracked', False),
                                                    'live': True
                                                }
                                            }
                                            all_vectors.append(vector)
                                    
                                    processed_files += 1
                                
                            except Exception as e:
                                if VERBOSE:
                                    print(f"   ⚠️  Error processing {relative_path}: {e}")
                                continue
                    
                    print(f"   ✅ Processed {processed_files} files, generated {len(all_vectors)} vectors")
                    print(f"   📊 Language breakdown: {dict(sorted(language_stats.items()))}")
                    
                    # Upload vectors to Pinecone in batches
                    if all_vectors:
                        print(f"   📤 Uploading to Pinecone namespace '{repo_namespace}'...")
                        
                        # Upload in batches to the repository-specific namespace
                        for i in range(0, len(all_vectors), BATCH_SIZE):
                            batch = all_vectors[i:i + BATCH_SIZE]
                            
                            # Ensure chunk_content is clean raw text without escape characters
                            for vector in batch:
                                if 'chunk_content' in vector['metadata']:
                                    # Strip any unwanted escaping and keep as plain text
                                    content = vector['metadata']['chunk_content']
                                    if isinstance(content, str):
                                        # Remove any JSON-style escaping that may have been added
                                        content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
                                        content = content.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                                        vector['metadata']['chunk_content'] = content
                            
                            # Use the direct Pinecone index upsert method with namespace
                            pinecone_client.index.upsert(vectors=batch, namespace=repo_namespace)
                            
                            if VERBOSE:
                                print(f"   📊 Uploaded batch {i//BATCH_SIZE + 1}/{(len(all_vectors) + BATCH_SIZE - 1)//BATCH_SIZE}")
                        
                        print(f"   ✅ Successfully uploaded {len(all_vectors)} vectors to namespace '{repo_namespace}'")
                        
                        # Mark as processed in the YAML file
                        repo_entry['processed'] = True
                        with open(DEFAULT_CONFIG_FILE, 'w') as f:
                            yaml.dump(config, f, sort_keys=False)
                        print(f"   💾 Marked '{repo_name}' as processed in the configuration file.")

                    else:
                        print(f"   ℹ️  No vectors generated for repository {repo_name}")
            
            except Exception as e:
                print(f"   ❌ Error processing repository {repo_name}: {e}")
                continue
        
        print("\n🎉 Bulk ingestion completed!")
        print("💡 The comprehensive chunking system has processed all files with language-specific chunkers")
        print("🏷️  Each repository is stored in its own namespace for better organization")
        
    except ImportError as e:
        print(f"❌ Missing dependencies for local processing: {e}")
        print("   Make sure you have all required packages installed:")
        print("   pip install pinecone-client openai gitpython pyyaml tiktoken")
        sys.exit(1)

def process_lambda_ingestion(config: Dict[str, Any]):
    """Process repositories by triggering Lambda functions via SQS."""
    
    # Get environment variables
    queue_url = os.environ.get('INGESTION_QUEUE_URL')
    if not queue_url:
        print("❌ INGESTION_QUEUE_URL environment variable not set")
        print("   Set it to your SQS queue URL for Lambda processing")
        sys.exit(1)
    
    repositories = config.get('repositories', [])
    processing_config = config.get('processing', {})
    default_namespace = processing_config.get('default_namespace', DEFAULT_NAMESPACE)
    
    # Initialize SQS client
    sqs = boto3.client('sqs')
    
    print("🚀 Starting Lambda bulk ingestion via SQS...")
    print("🏷️  Using individual namespaces per repository")
    
    for repo_entry in repositories:
        repo_config = normalize_repository_entry(repo_entry)
        repo_url = repo_config['url']
        repo_name = repo_config['name']
        repo_namespace = repo_config['namespace'] or default_namespace
        
        print(f"\n📁 Queuing repository: {repo_name}")
        print(f"   Namespace: {repo_namespace}")
        
        try:
            # Create SQS message (same format as ingestion_webhook)
            # Include namespace in the message for Lambda processing
            message_body = json.dumps({
                'repository': repo_name,
                'commit_sha': 'main',  # Use latest commit
                'pusher': 'bulk-ingestion-script',
                'namespace': repo_namespace  # Add namespace to message
            })
            
            # Send to SQS
            response = sqs.send_message(
                QueueUrl=queue_url,
                MessageBody=message_body
            )
            
            print(f"   ✅ Queued successfully (Message ID: {response['MessageId']})")
            
        except Exception as e:
            print(f"   ❌ Error queuing {repo_name}: {e}")
            continue
    
    print(f"\n🎉 Queued {len(repositories)} repositories for processing!")
    print("   Monitor AWS CloudWatch logs to track processing progress.")

def main():
    """Main function - runs bulk ingestion with default configuration."""
    
    print("🚀 CodeChat Bulk Repository Ingestion")
    print("=" * 50)
    print("📚 Processing repositories using comprehensive language-specific chunkers")
    print(f"⚙️  Mode: {PROCESSING_MODE} | Batch size: {BATCH_SIZE} | Workers: {MAX_WORKERS}")
    print("")
    
    # Load configuration
    config_path = Path(DEFAULT_CONFIG_FILE)
    if not config_path.exists():
        print(f"❌ Configuration file not found: {config_path}")
        print("   Available configurations:")
        config_dir = Path("config")
        if config_dir.exists():
            for config_file in config_dir.glob("*.yml"):
                print(f"   • {config_file}")
        else:
            print("   • No config directory found")
        sys.exit(1)
    
    print(f"📋 Loading configuration from: {config_path}")
    config = load_repository_config(str(config_path))
    
    repositories = config.get('repositories', [])
    if not repositories:
        print("❌ No repositories found in configuration file")
        sys.exit(1)
    
    print(f"📊 Found {len(repositories)} repositories to process")
    print("🏷️  Using individual namespaces per repository for better organization")
    print("")
    
    # Process repositories based on mode
    if PROCESSING_MODE == "local":
        process_local_ingestion(config)
    elif PROCESSING_MODE == "lambda":
        process_lambda_ingestion(config)
    else:
        print(f"❌ Invalid processing mode: {PROCESSING_MODE}")
        print("   Supported modes: 'local', 'lambda'")
        sys.exit(1)

if __name__ == "__main__":
    main()