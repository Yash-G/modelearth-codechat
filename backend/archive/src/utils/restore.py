# Restore Archived Vectors from S3 to Pinecone

import boto3
import json
import pinecone
import os

class VectorRestorer:
    def __init__(self, s3_bucket, pinecone_index):
        self.s3_bucket = s3_bucket
        self.pinecone_index = pinecone_index
        self.s3_client = boto3.client('s3')
        pinecone.init(api_key=os.getenv('PINECONE_API_KEY'), environment=os.getenv('PINECONE_ENV'))

    def restore_vectors(self, repo, commit_sha):
        # Construct the S3 path for the archived vectors
        s3_path = f'vectors/{repo}/{commit_sha}/vectors.json'
        
        try:
            # Download the vectors file from S3
            response = self.s3_client.get_object(Bucket=self.s3_bucket, Key=s3_path)
            vectors_data = json.loads(response['Body'].read().decode('utf-8'))
            
            # Upsert vectors to Pinecone
            self.upsert_vectors(vectors_data)
            print(f'Successfully restored vectors for {repo} at commit {commit_sha}.')
        except Exception as e:
            print(f'Error restoring vectors: {e}')

    def upsert_vectors(self, vectors_data):
        # Prepare the vectors for upsert
        upsert_data = [
            {
                'id': vector['content_sha'],
                'values': vector['embedding'],
                'metadata': {
                    'repo': vector['repo'],
                    'commit_sha': vector['commit_sha'],
                    'file_path': vector['file_path'],
                    'chunk_type': vector['chunk_type'],
                    'line_range': vector['line_range']
                }
            }
            for vector in vectors_data
        ]
        
        # Upsert to Pinecone
        with pinecone.Client(self.pinecone_index) as client:
            client.upsert(upsert_data)

if __name__ == '__main__':
    # Example usage
    s3_bucket = os.getenv('S3_BUCKET_NAME')
    pinecone_index = os.getenv('PINECONE_INDEX_NAME')
    
    restorer = VectorRestorer(s3_bucket, pinecone_index)
    restorer.restore_vectors('example_repo', 'commit_sha_example')