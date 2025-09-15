import json
import os
from pinecone import Pinecone
from openai import OpenAI
import google.generativeai as genai

# Initialize clients (moved outside handler for better performance)
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
GOOGLE_API_KEY = os.environ.get("GOOGLE_API_KEY")
PINECONE_API_KEY = os.environ.get("PINECONE_API_KEY")

openai_client = OpenAI(api_key=OPENAI_API_KEY)
genai.configure(api_key=GOOGLE_API_KEY)
pinecone_client = Pinecone(api_key=PINECONE_API_KEY)

# Pinecone index config
INDEX_NAME = "model-earth-jam-stack"
index = pinecone_client.Index(INDEX_NAME)
gemini_model = genai.GenerativeModel("gemini-1.5-flash")

def get_all_namespaces():
    stats = index.describe_index_stats()
    return list(stats["namespaces"].keys())

def query_all_namespaces(question, top_k=10, per_ns_k=5, min_score=None):
    try:
        embed_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=question
        )
        query_vector = embed_response.data[0].embedding
    except Exception as e:
        return f"❌ Embedding error: {e}"

    # Collect results from all namespaces
    combined_matches = []
    for ns in get_all_namespaces():
        try:
            results = index.query(
                vector=query_vector,
                top_k=per_ns_k,
                include_metadata=True,
                namespace=ns
            )
            matches = results["matches"]
            if min_score:
                matches = [m for m in matches if m["score"] >= min_score]
            combined_matches.extend(matches)
        except Exception as e:
            continue  # ignore broken namespaces

    # Sort combined matches by score
    combined_matches = sorted(combined_matches, key=lambda x: x["score"], reverse=True)
    top_matches = combined_matches[:top_k]

    if not top_matches:
        return f"❌ No relevant context found for: {question}"

    # Extract context
    context = "\n\n---\n\n".join(
        f"[File: {m['metadata'].get('file_path', 'unknown')}]\n{m['metadata'].get('content', '')}"
        for m in top_matches
        if "content" in m["metadata"]
    )

    prompt = f"""
You are a helpful, professional AI assistant supporting developers in exploring a large, multi-repository codebase.

Below is a developer's question and a set of relevant content snippets retrieved from indexed files (code or documentation).
Each snippet includes optional metadata such as file paths to help you reference the source.

---

**Question:**
{question}

---

**Context:**
{context}

---

**Instructions:**

- Your response must be strictly grounded in the above context.
- DO NOT make assumptions or fabricate implementation details not present in the content.
- If the context includes partial logic, mention what's provided and what is not.
- If available, include relevant `file_path` references to help locate source files.
- Format your response with clear paragraphs or bullet points for readability.
- If the answer is not available in the context, reply exactly:
  **"The answer is not available in the indexed codebase."**

Be clear, friendly, and accurate – like an expert ChatGPT assistant who knows how to say "not enough info" when needed.
"""

    try:
        response = gemini_model.generate_content(prompt)
        return response.text
    except Exception as e:
        return f"⚠️ Gemini error: {e}"

# Lambda handler function
def lambda_handler(event, context):
    """Main Lambda handler function"""
    logger.info(f"Lambda function invoked with event: {json.dumps(event, default=str)}")
    
    try:
        # Parse the incoming request
        body = {}
        
        # Handle different event sources
        if 'body' in event:
            # API Gateway request
            if isinstance(event['body'], str):
                body = json.loads(event['body']) if event['body'] else {}
            else:
                body = event['body'] or {}
        elif 'Records' in event:
            # SQS/SNS/EventBridge - not supported in this implementation
            return {
                'statusCode': 400,
                'body': json.dumps({
                    'error': 'Event-driven invocation not supported. Use direct invocation or API Gateway.'
                })
            }
        else:
            # Direct Lambda invocation
            body = event

        # Extract parameters with defaults and validation
        question = body.get('question', '').strip()
        top_k = max(1, min(50, body.get('top_k', 10)))  # Limit between 1-50
        per_ns_k = max(1, min(20, body.get('per_ns_k', 5)))  # Limit between 1-20
        min_score = body.get('min_score')
        
        # Validate min_score if provided
        if min_score is not None:
            try:
                min_score = float(min_score)
                if not (0 <= min_score <= 1):
                    min_score = None
                    logger.warning("min_score should be between 0 and 1, ignoring")
            except (ValueError, TypeError):
                min_score = None
                logger.warning("Invalid min_score format, ignoring")
        
        logger.info(f"Parameters - question: {question[:50]}..., top_k: {top_k}, per_ns_k: {per_ns_k}, min_score: {min_score}")
        
        # Validate required parameters
        if not question:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                    'Access-Control-Allow-Headers': 'Content-Type, Authorization'
                },
                'body': json.dumps({
                    'error': 'Question is required and cannot be empty',
                    'example': {
                        'question': 'How many sub modules are in this project?',
                        'top_k': 10,
                        'per_ns_k': 5,
                        'min_score': 0.7
                    }
                })
            }
        
        # Process the question
        start_time = context.get_remaining_time_in_millis() if context else None
        answer = query_all_namespaces(question, top_k, per_ns_k, min_score)
        
        # Log execution time if context is available
        if start_time:
            execution_time = start_time - context.get_remaining_time_in_millis()
            logger.info(f"Query processed in {execution_time}ms")
        
        # Success response
        response = {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Methods': 'POST, GET, OPTIONS',
                'Access-Control-Allow-Headers': 'Content-Type, Authorization'
            },
            'body': json.dumps({
                'question': question,
                'answer': answer,
                'parameters': {
                    'top_k': top_k,
                    'per_ns_k': per_ns_k,
                    'min_score': min_score
                },
                'timestamp': context.aws_request_id if context else None
            }, ensure_ascii=False)
        }
        
        logger.info("Request processed successfully")
        return response
        
    except json.JSONDecodeError as e:
        logger.error(f"JSON parsing error: {str(e)}")
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Invalid JSON format in request body',
                'details': str(e)
            })
        }
        
    except Exception as e:
        logger.error(f"Unexpected error: {str(e)}", exc_info=True)
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'error': 'Internal server error occurred',
                'details': str(e) if os.environ.get('DEBUG') else 'Contact administrator'
            })
        }


# Health check function (optional, for monitoring)
def health_check():
    """Simple health check function"""
    try:
        # Test basic connectivity
        stats = index.describe_index_stats()
        return {
            'status': 'healthy',
            'index_name': INDEX_NAME,
            'total_vectors': stats.get('total_vector_count', 0),
            'namespaces': len(stats.get('namespaces', {}))
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


# For local testing
if __name__ == "__main__":
    # Test event
    test_event = {
        "question": "How many sub modules are in this project?",
        "top_k": 5,
        "per_ns_k": 3
    }
    
    class MockContext:
        def __init__(self):
            self.aws_request_id = "test-request-123"
            self.get_remaining_time_in_millis = lambda: 30000
    
    result = lambda_handler(test_event, MockContext())
    print(json.dumps(result, indent=2, ensure_ascii=False))