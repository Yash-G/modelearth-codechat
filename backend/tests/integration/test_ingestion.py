import pytest
import json
import boto3
import sys
import os
from pathlib import Path
from unittest.mock import patch

# Add the src directory to path
sys.path.append(str(Path(__file__).parent.parent.parent / 'src'))

from src.lambdas.ingest_worker.index import handler

@pytest.fixture
def mock_event():
    return {
        "Records": [
            {
                "body": json.dumps({
                    "repo": "test-repo",
                    "commit_sha": "abc123",
                    "files": ["file1.py", "file2.py"]
                })
            }
        ]
    }

@pytest.fixture
def mock_s3_client():
    with patch('boto3.client') as mock:
        yield mock

@pytest.fixture
def mock_pinecone_client():
    with patch('pinecone.Client') as mock:
        yield mock

def test_ingestion_pipeline(mock_event, mock_s3_client, mock_pinecone_client):
    response = handler(mock_event, None)

    assert response['statusCode'] == 200
    assert 'Ingestion successful' in response['body']

    # Verify that the S3 client was called to archive vectors
    mock_s3_client.return_value.put_object.assert_called_once()

    # Verify that the Pinecone client was called to upsert vectors
    mock_pinecone_client.return_value.upsert.assert_called_once()