import json
import os
import boto3
import tempfile
from git import Repo
from pathlib import Path
import sys

# Add the src directory to the Python path to import core modules
sys.path.append(str(Path(__file__).parent.parent.parent))

from core.pine import PineconeClient
from core.smart_chunker import SmartChunker
from core.embedding_generator import EmbeddingGenerator

# Environment variables
S3_ARCHIVE_BUCKET = os.environ.get('S3_ARCHIVE_BUCKET', '')
PINECONE_NAMESPACE = os.environ.get('PINECONE_NAMESPACE', 'codechat-main')
IS_LOCAL = os.environ.get('LOCAL_DEVELOPMENT') == 'true'

# AWS Clients
if IS_LOCAL:
    localstack_endpoint = os.environ.get('LOCALSTACK_ENDPOINT', 'http://localhost:4566')
    s3 = boto3.client('s3', endpoint_url=localstack_endpoint, region_name='us-east-1')
else:
    s3 = boto3.client('s3')

def process_repository(repo_url, commit_sha, namespace):
    """Clone repo, process files, generate embeddings, and return vectors using the advanced data model."""
    # Get OpenAI API key from environment
    openai_api_key = os.environ.get('OPENAI_API_KEY')
    if not openai_api_key:
        raise ValueError("OPENAI_API_KEY environment variable not set for Lambda.")

    with tempfile.TemporaryDirectory() as temp_dir:
        repo_path = Path(temp_dir) / "repo"
        print(f"Cloning {repo_url} to {repo_path}...")
        repo = Repo.clone_from(f"https://github.com/{repo_url}.git", str(repo_path))
        repo.git.checkout(commit_sha)
        print(f"Checked out commit {commit_sha}.")

        chunker = SmartChunker()
        embed_generator = EmbeddingGenerator(api_key=openai_api_key)
        
        all_vectors = []

        for file_path in repo_path.rglob('*'):
            if file_path.is_file() and not any(part.startswith('.') for part in file_path.parts):
                # Skip binary files
                binary_extensions = {'.png', '.jpg', '.jpeg', '.gif', '.bmp', '.ico', '.svg', '.webp', 
                                   '.pdf', '.zip', '.tar', '.gz', '.so', '.dll', '.exe', '.bin', '.dat'}
                if file_path.suffix.lower() in binary_extensions:
                    continue
                    
                try:
                    relative_path = file_path.relative_to(repo_path)
                    print(f"Processing file: {relative_path}")
                    
                    chunks = chunker.chunk(str(file_path))
                    if not chunks:
                        continue

                    # Filter out empty chunks
                    valid_chunks = [chunk for chunk in chunks if chunk.get('content', '').strip()]
                    if not valid_chunks:
                        continue

                    chunk_contents = [chunk['content'].strip() for chunk in valid_chunks]
                    embeddings = embed_generator.generate_embeddings_batch(chunk_contents)
                    
                    for i, chunk in enumerate(valid_chunks):
                        if embeddings[i] is not None:  # Only process if embedding was successful
                            vector_id = f"{repo_url}:{relative_path}:{chunk.get('type', 'code')}:{chunk.get('start_line', 0)}-{chunk.get('end_line', 0)}"
                            vector = {
                                'id': vector_id,
                                'values': embeddings[i],
                                'metadata': {
                                    # 1. Identity & Location (Who and Where)
                                    'repo_name': repo_url,
                                    'file_path': str(relative_path),
                                    'namespace': namespace,
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
                                    'tracked': True,
                                    'live': True
                                }
                            }
                            all_vectors.append(vector)
                except Exception as e:
                    print(f"Could not process file {file_path}: {e}")
        
        return all_vectors

def archive_to_s3(vectors, repo_name, commit_sha):
    """Archive the generated vectors to S3."""
    if not S3_ARCHIVE_BUCKET:
        print("S3_ARCHIVE_BUCKET not set. Skipping archival.")
        return False
    
    archive_key = f"archives/{repo_name}/{commit_sha}.json"
    try:
        s3.put_object(
            Bucket=S3_ARCHIVE_BUCKET,
            Key=archive_key,
            Body=json.dumps(vectors)
        )
        print(f"Successfully archived vectors to s3://{S3_ARCHIVE_BUCKET}/{archive_key}")
        return True
    except Exception as e:
        print(f"Failed to archive vectors to S3: {e}")
        return False

def activate_new_vectors(pinecone_client, vectors, repo_name, commit_sha, namespace):
    """Upsert vectors and perform atomic switch in Pinecone."""
    print(f"Upserting new vectors to Pinecone namespace '{namespace}'...")
    
    # Clean up chunk_content to remove escape characters before uploading
    for vector in vectors:
        if 'chunk_content' in vector['metadata']:
            content = vector['metadata']['chunk_content']
            if isinstance(content, str):
                # Remove any JSON-style escaping that may have been added
                content = content.replace('\\n', '\n').replace('\\t', '\t').replace('\\r', '\r')
                content = content.replace('\\"', '"').replace("\\'", "'").replace('\\\\', '\\')
                vector['metadata']['chunk_content'] = content
    
    pinecone_client.index.upsert(vectors=vectors, namespace=namespace)
    print(f"Upserted {len(vectors)} vectors.")

    print("Performing atomic activation...")
    # 1. Mark new vectors as live
    pinecone_client.index.update(id=vectors[0]['id'], set_metadata={'live': True}, namespace=namespace) # Simplified for demo
    
    # 2. Mark old vectors as not live (this is a complex operation and is simplified here)
    # In a real scenario, you would query for all vectors of the repo that are not of the current commit_sha
    # and update their 'live' status to False. This requires careful handling.
    print("Activation complete.")


def lambda_handler(event, context):
    """Main handler for the ingestion worker."""
    pinecone_client = PineconeClient()

    for record in event['Records']:
        try:
            message = json.loads(record['body'])
            repo_name = message['repository']
            commit_sha = message['commit_sha']
            # Get namespace from message, fallback to repo name or default
            namespace = message.get('namespace')
            if not namespace:
                # Extract namespace from repo name (e.g., modelearth/codechat -> codechat)
                namespace = repo_name.split('/')[-1] if '/' in repo_name else repo_name
            
            print(f"Processing job for {repo_name} at commit {commit_sha}")
            print(f"Using namespace: {namespace}")

            # 1. Process repository and generate vectors
            vectors = process_repository(repo_name, commit_sha, namespace)
            if not vectors:
                print("No vectors generated. Job complete.")
                continue

            # 2. Archive vectors to S3
            archive_to_s3(vectors, repo_name, commit_sha)

            # 3. Activate new vectors in Pinecone with repository-specific namespace
            activate_new_vectors(pinecone_client, vectors, repo_name, commit_sha, namespace)

            print(f"Successfully processed and activated vectors for {repo_name} at {commit_sha} in namespace '{namespace}'.")

        except Exception as e:
            print(f"Error processing SQS record: {e}")
            # Depending on the error, you might want to re-queue the message
            # or send it to a dead-letter queue. For now, we just log it.
    
    return {
        'statusCode': 200,
        'body': json.dumps({'message': 'Ingestion run complete.'})
    }
