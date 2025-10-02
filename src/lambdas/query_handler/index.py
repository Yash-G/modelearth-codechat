import json
import os
import re
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
from pinecone import Pinecone
from openai import OpenAI
import boto3

from agentic_components import QueryAnalysisAgent, RepositoryIntelligentSearchAgent, QueryAnalysis, QueryType

# Try to import yaml, fall back gracefully if not available
try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False
    print("Warning: PyYAML not available, using static mapping fallback")

def lambda_handler(event, context):
    """
    Enhanced Lambda handler with agentic search capabilities
    """
    # Handle CORS preflight request
    if event.get('httpMethod') == 'OPTIONS':
        return {
            'statusCode': 200,
            'headers': {
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': ''
        }
    
    try:
        # Initialize clients with environment variables
        OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY')
        PINECONE_API_KEY = os.environ.get('PINECONE_API_KEY')
        
        if not OPENAI_API_KEY or not PINECONE_API_KEY:
            # Fallback to temp response if keys not available
            return temp_response(event)
        
        openai_client = OpenAI(api_key=OPENAI_API_KEY)
        pinecone_client = Pinecone(api_key=PINECONE_API_KEY)
        bedrock_client = boto3.client('bedrock-runtime', region_name='us-east-1')
        
        # Pinecone index config
        INDEX_NAME = os.environ.get('PINECONE_INDEX', 'model-earth-jam-stack')
        index = pinecone_client.Index(INDEX_NAME)
        
        # Initialize agentic components with proper dependencies
        query_analyzer = QueryAnalysisAgent(bedrock_client)
        repo_namespace_map = {
            "modelearth/webroot": "webroot",
            "modelearth/localsite": "localsite", 
            "modelearth/io": "io",
            "modelearth/codechat": "codechat"
        }
        intelligent_agent = RepositoryIntelligentSearchAgent(index, repo_namespace_map, bedrock_client, openai_client)
        
        # Parse request body
        body = event.get('body', '{}')
        if isinstance(body, str):
            request_data = json.loads(body)
        else:
            request_data = body
        
        query = request_data.get('query', '')
        repositories = request_data.get('repositories', None)
        if not repositories:
            repo = request_data.get('repo', None)
            if repo:
                repositories = [repo]
        
        if not query:
            return {
                'statusCode': 400,
                'headers': {
                    'Content-Type': 'application/json',
                    'Access-Control-Allow-Origin': '*',
                    'Access-Control-Allow-Headers': 'Content-Type',
                    'Access-Control-Allow-Methods': 'POST,OPTIONS'
                },
                'body': json.dumps({'error': 'Query parameter is required'})
            }
        
        # Step 1: Analyze the query with safety checks
        try:
            query_analysis = query_analyzer.analyze_query(query)
            if not query_analysis:
                print("Warning: Query analysis returned None, using fallback")
                query_analysis = None
        except Exception as e:
            print(f"Query analysis error: {e}")
            query_analysis = None
        
        if query_analysis:
            print(f"🧠 Query Analysis: {query_analysis.query_type.value}, Entities: {query_analysis.entities}")
        else:
            print("🧠 Query Analysis: Using fallback mode")
        
        # Step 2: Perform agentic search
        response_content = agentic_search(
            query, query_analysis, openai_client, index, bedrock_client, 
            intelligent_agent, repositories
        )
        
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'content': response_content})
        }
        
    except Exception as e:
        print(f"Error during processing: {e}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({"error": f"An error occurred while processing your request: {str(e)}"})
        }

def temp_response(event):
    """Fallback response when keys are not available"""
    body = event.get('body', '{}')
    if isinstance(body, str):
        request_data = json.loads(body)
    else:
        request_data = body
    
    query = request_data.get('query', '')
    repo = request_data.get('repo', '')
    
    if not query:
        return {
            'statusCode': 400,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*',
                'Access-Control-Allow-Headers': 'Content-Type',
                'Access-Control-Allow-Methods': 'POST,OPTIONS'
            },
            'body': json.dumps({'error': 'Query parameter is required'})
        }

    response_content = f"""🧠 **Agentic Search System Ready**

Your query: "{query}"
Repository: {repo}

The enhanced agentic search system is being deployed with:
- Query Analysis Agent (determines search strategy)  
- Multi-Modal Search (documentation, examples, structure)
- Result Fusion (intelligent ranking and combination)

Please wait while the Lambda layers are updated with the new dependencies."""

    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Headers': 'Content-Type',
            'Access-Control-Allow-Methods': 'POST,OPTIONS'
        },
        'body': json.dumps({'content': response_content})
    }

def agentic_search(query, query_analysis, openai_client, index, bedrock_client, intelligent_agent, repositories):
    """Perform enhanced repository-intelligent agentic search"""
    try:
        # Get namespaces to query with error handling
        namespaces_to_query = []
        try:
            if repositories:
                namespaces_to_query = [map_repo_to_namespace(repo) for repo in repositories if repo]
            else:
                if index:
                    stats = index.describe_index_stats()
                    if stats and "namespaces" in stats:
                        namespaces_to_query = list(stats["namespaces"].keys())
                        
            if not namespaces_to_query:
                namespaces_to_query = ["webroot", "localsite", "io", "codechat"]  # Fallback
        except Exception as e:
            print(f"Namespace discovery error: {e}")
            namespaces_to_query = ["webroot", "localsite", "io", "codechat"]  # Fallback
        
        # Use the new intelligent repository search
        if query_analysis and intelligent_agent:
            try:
                print(f"🧠 Using intelligent repository search for query type: {query_analysis.query_type.value}")
                print(f"📂 Target namespaces: {namespaces_to_query}")
                print(f"🎯 Specific targets: {query_analysis.specific_targets}")
                
                combined_matches = intelligent_agent.intelligent_repository_search(
                    query, query_analysis, namespaces_to_query
                )
                
                if not combined_matches:
                    print("⚠️ No matches from intelligent search, falling back to basic search")
                    # Fallback to basic vector search
                    combined_matches = basic_vector_search(query, openai_client, index, namespaces_to_query)
                else:
                    print(f"✅ Found {len(combined_matches)} matches using intelligent search")
                    
            except Exception as e:
                print(f"Intelligent search error: {e}, falling back to basic search")
                combined_matches = basic_vector_search(query, openai_client, index, namespaces_to_query)
        else:
            print("⚠️ Query analysis or intelligent agent not available, using basic search")
            combined_matches = basic_vector_search(query, openai_client, index, namespaces_to_query)
        
        if not combined_matches:
            return f"❌ No matches found for: '{query}'"
        
        # Sort by enhanced scores with safety
        try:
            combined_matches.sort(key=lambda x: x.get('score', 0), reverse=True)
            top_matches = combined_matches[:10]
        except Exception as e:
            print(f"Sorting error: {e}")
            top_matches = combined_matches[:10] if combined_matches else []
        
        if not top_matches:
            return f"❌ No valid matches after processing for: '{query}'"
        
        # Generate context with safety checks - clean format without search metadata
        context_parts = []
        for m in top_matches:
            try:
                metadata = m.get('metadata', {})
                file_path = metadata.get('file_path', 'N/A')
                repo_name = metadata.get('repo_name', m.get('repository', 'N/A'))
                chunk_content = metadata.get('chunk_content', 'Content not available.')
                
                # Simple, clean context without search strategy details
                context_part = f"**File:** {file_path}\n**Repository:** {repo_name}\n\n```\n{chunk_content}\n```"
                context_parts.append(context_part)
            except Exception as e:
                print(f"Context generation error for match: {e}")
                continue
        
        context = "\n\n---\n\n".join(context_parts)
        
        # Generate enhanced prompt with intelligence insights
        try:
            query_type = query_analysis.query_type.value if query_analysis and hasattr(query_analysis, 'query_type') else 'general'
            entities = query_analysis.entities if query_analysis and hasattr(query_analysis, 'entities') else []
            specific_targets = query_analysis.specific_targets if query_analysis and hasattr(query_analysis, 'specific_targets') else []
            search_strategies = query_analysis.search_strategies if query_analysis and hasattr(query_analysis, 'search_strategies') else []
            repository_context = query_analysis.repository_context if query_analysis and hasattr(query_analysis, 'repository_context') else ''
            
            prompt = f"""You are an expert AI assistant helping developers understand code repositories.

**Question:** {query}

**Relevant Code and Documentation:**
{context}

Please provide a helpful and direct answer based on the code and documentation above. Focus on:
- Direct answers to the question
- Relevant code examples and explanations
- Practical implementation details
- Clear explanations without technical search methodology

Keep your response focused and practical for developers."""
        except Exception as e:
            print(f"Prompt generation error: {e}")
            prompt = f"""You are an expert AI assistant helping developers understand code repositories.

Question: {query}

Relevant Code:
{context}

Please provide a helpful answer based on the code above."""

        # Use Bedrock for response with safety
        try:
            if not bedrock_client:
                return f"⚠️ Response generation unavailable. Found {len(top_matches)} relevant matches for: '{query}'"
                
            bedrock_request = {
                "messages": [{"role": "user", "content": [{"text": prompt}]}],
                "inferenceConfig": {"maxTokens": 2000, "temperature": 0.1}
            }
            
            response = bedrock_client.invoke_model(
                modelId="amazon.nova-micro-v1:0",
                body=json.dumps(bedrock_request)
            )
            
            if not response or 'body' not in response:
                return f"⚠️ Response generation failed. Found {len(top_matches)} relevant matches for: '{query}'"
                
            response_body = json.loads(response['body'].read())
            if not response_body or 'output' not in response_body:
                return f"⚠️ Invalid response format. Found {len(top_matches)} relevant matches for: '{query}'"
                
            ai_response = response_body['output']['message']['content'][0]['text']
            
            # Simple footer without verbose technical details
            footer_parts = []
            if len(namespaces_to_query) == 1:
                footer_parts.append(f"Repository: {namespaces_to_query[0]}")
            elif len(namespaces_to_query) > 1:
                footer_parts.append(f"Searched {len(namespaces_to_query)} repositories")
            
            if len(top_matches) > 0:
                footer_parts.append(f"{len(top_matches)} relevant results")
            
            if footer_parts:
                ai_response += f"\n\n---\n*{' • '.join(footer_parts)}*"
            
            return ai_response
            
        except Exception as e:
            print(f"Bedrock response error: {e}")
            return f"⚠️ Response generation failed: {e}. Found {len(top_matches)} relevant matches for: '{query}'"
        
    except Exception as e:
        print(f"Agentic search critical error: {e}")
        return f"⚠️ Search error: {e}"


def basic_vector_search(query, openai_client, index, namespaces_to_query):
    """Fallback basic vector search when intelligent search fails"""
    try:
        # Generate embedding with error handling
        if not openai_client:
            return []
            
        embed_response = openai_client.embeddings.create(
            model="text-embedding-3-small",
            input=query
        )
        if not embed_response or not embed_response.data or len(embed_response.data) == 0:
            return []
        query_vector = embed_response.data[0].embedding
        
        # Search across namespaces
        combined_matches = []
        for ns in namespaces_to_query:
            if not ns:  # Skip None/empty namespaces
                continue
            try:
                results = index.query(
                    vector=query_vector,
                    top_k=5,
                    include_metadata=True,
                    namespace=ns
                )
                if results and "matches" in results:
                    combined_matches.extend(results["matches"])
            except Exception as e:
                print(f"Error querying namespace {ns}: {e}")
                continue
        
        return combined_matches
        
    except Exception as e:
        print(f"Basic vector search error: {e}")
        return []

def map_repo_to_namespace(repo_name):
    """Map repository names to namespaces"""
    static_mapping = {
        "modelearth/webroot": "webroot",
        "modelearth/localsite": "localsite", 
        "modelearth/io": "io",
        "modelearth/codechat": "codechat"
    }
    return static_mapping.get(repo_name, repo_name)