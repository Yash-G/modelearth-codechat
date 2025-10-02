import json
import os
import boto3
import hashlib
import hmac
from datetime import datetime, timedelta

# Environment variables
GITHUB_WEBHOOK_SECRET = os.environ.get('GITHUB_WEBHOOK_SECRET', '')
INGESTION_QUEUE_URL = os.environ.get('INGESTION_QUEUE_URL', '')
IDEMPOTENCY_TABLE_NAME = os.environ.get('IDEMPOTENCY_TABLE_NAME', '')
IS_LOCAL = os.environ.get('LOCAL_DEVELOPMENT') == 'true'

# AWS Clients
if IS_LOCAL:
    localstack_endpoint = os.environ.get('LOCALSTACK_ENDPOINT', 'http://localhost:4566')
    sqs = boto3.client('sqs', endpoint_url=localstack_endpoint, region_name='us-east-1')
    dynamodb = boto3.client('dynamodb', endpoint_url=localstack_endpoint, region_name='us-east-1')
else:
    sqs = boto3.client('sqs')
    dynamodb = boto3.client('dynamodb')

DEFAULT_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type",
    "Access-Control-Allow-Methods": "OPTIONS,GET,POST"
}

def validate_github_signature(headers, body):
    """Validate the GitHub webhook signature."""
    signature = headers.get('x-hub-signature-256')
    if not signature:
        return False
    
    sha_name, signature_hash = signature.split('=', 1)
    if sha_name != 'sha256':
        return False

    mac = hmac.new(GITHUB_WEBHOOK_SECRET.encode(), msg=body.encode(), digestmod=hashlib.sha256)
    return hmac.compare_digest(mac.hexdigest(), signature_hash)

def is_duplicate_request(delivery_id):
    """Check for duplicate requests using DynamoDB for idempotency."""
    if not delivery_id:
        return False # Cannot check for duplicates without an ID

    try:
        # Time-to-live for the idempotency record (e.g., 24 hours)
        ttl = int((datetime.now() + timedelta(hours=24)).timestamp())
        
        response = dynamodb.put_item(
            TableName=IDEMPOTENCY_TABLE_NAME,
            Item={'delivery_id': {'S': delivery_id}, 'ttl': {'N': str(ttl)}},
            ConditionExpression='attribute_not_exists(delivery_id)'
        )
        return False # Not a duplicate
    except dynamodb.exceptions.ConditionalCheckFailedException:
        return True # It's a duplicate

def enqueue_ingestion_job(payload):
    """Enqueue the ingestion job to SQS."""
    try:
        message_body = json.dumps({
            'repository': payload['repository']['full_name'],
            'commit_sha': payload['after'],
            'pusher': payload['pusher']['name']
        })
        sqs.send_message(
            QueueUrl=INGESTION_QUEUE_URL,
            MessageBody=message_body
        )
        return True
    except Exception as e:
        print(f"Error enqueuing job to SQS: {e}")
        return False

def lambda_handler(event, context):
    """Main handler for the ingest webhook."""
    headers = event.get('headers', {})
    body = event.get('body', '{}')

    # 1. Validate signature
    if not IS_LOCAL and not validate_github_signature(headers, body):
        return {
            'statusCode': 403,
            'headers': DEFAULT_HEADERS,
            'body': json.dumps({'error': 'Invalid signature'})
        }

    # 2. Check for duplicate events
    delivery_id = headers.get('x-github-delivery')
    if not IS_LOCAL and is_duplicate_request(delivery_id):
        return {
            'statusCode': 202, # Accepted, but not processed
            'headers': DEFAULT_HEADERS,
            'body': json.dumps({'message': 'Duplicate event, ignoring.'})
        }

    try:
        payload = json.loads(body)
    except json.JSONDecodeError:
        return {
            'statusCode': 400,
            'headers': DEFAULT_HEADERS,
            'body': json.dumps({'error': 'Invalid JSON payload'})
        }

    # 3. Process only pushes to the main branch
    if headers.get('x-github-event') == 'push' and payload.get('ref') == 'refs/heads/main':
        # 4. Enqueue job
        if enqueue_ingestion_job(payload):
            return {
                'statusCode': 200,
                'headers': DEFAULT_HEADERS,
                'body': json.dumps({'message': 'Ingestion job enqueued successfully.'})
            }
        else:
            return {
                'statusCode': 500,
                'headers': DEFAULT_HEADERS,
                'body': json.dumps({'error': 'Failed to enqueue ingestion job.'})
            }
    
    return {
        'statusCode': 200,
        'headers': DEFAULT_HEADERS,
        'body': json.dumps({'message': 'Event received, but not a push to main. No action taken.'})
    }
