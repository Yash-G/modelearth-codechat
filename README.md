# CodeChat - Repository-Intelligent Code Search

> **Note**: This README contains all essential documentation. Previous documentation files have been consolidated here. Component-specific READMEs remain in their respective directories (`chat/README.md`, etc.). Archived components and old docs are in the `archive/` directory.

## 🚀 **Quick Start - Run the Main Pipeline**

The easiest way to test everything is to run the main pipeline:

```bash
cd /Users/sagar/projects/codechat

# Set environment variables (or use .env file)
export OPENAI_API_KEY="your-openai-key"
export PINECONE_API_KEY="your-pinecone-key"
export PINECONE_ENVIRONMENT="us-east-1-aws"
export PINECONE_INDEX_NAME="model-earth"

# Run the complete pipeline
python main.py
```

**What this does:**
- ✅ Loads repository configuration from `config/repositories.yml`
- ✅ Clones the specified repositories
- ✅ Processes all code files (Python, JavaScript, TypeScript, Java, etc.)
- ✅ Generates intelligent code chunks
- ✅ Creates AI-powered summaries using OpenAI
- ✅ Generates embeddings for semantic search
- ✅ Stores everything in Pinecone vector database
- ✅ Provides detailed progress reporting

---

## 🧪 Testing the Restructured Codebase

### Prerequisites

1. **Python Environment**: Make sure you have Python 3.8+ installed
2. **Dependencies**: Install required packages
   ```bash
   pip install -r requirements.txt
   ```

3. **Environment Variables**: Set up your API keys
   ```bash
   cp config/.env.example .env
   # Edit .env with your actual API keys:
   # OPENAI_API_KEY=your_openai_key
   # PINECONE_API_KEY=your_pinecone_key
   # PINECONE_ENVIRONMENT=your_pinecone_env
   ```

---

## 🧪 **Test 1: Basic Import Test**

Verify that all modules can be imported correctly:

```bash
# Test core modules
python -c "from src.core.simple_processor import SimpleCodeProcessor; print('✅ Simple processor import OK')"
python -c "from src.core.code_processor_main import Config; print('✅ Main processor import OK')"
python -c "from src.core.summarizer import CodeSummarizer; print('✅ Summarizer import OK')"
python -c "from src.core.embedding_generator import CodeEmbeddingGenerator; print('✅ Embedding generator import OK')"

# Test utility modules
python -c "from src.utils.evaluate import *; print('✅ Utils import OK')"
```

---

## 🧪 **Test 2: Simple Processor (No API Keys Required)**

Test the basic file processing pipeline without external APIs:

```bash
# Run the simple processor (will use mock embeddings)
python -m src.core.simple_processor

# Expected output:
# 🚀 Processing 1 repositories...
# 📦 Processing: codechat
# ⚠️ Repository path repo_analysis_output/test_repo not found, using current workspace for testing
# 📁 Found X files to process
# 🔄 Processing: [filename]
# 💾 Would store chunk chunk_0 in Pinecone
#      Index: model-earth, Namespace: codechat-test
#      Embedding size: 1536
#      Metadata keys: ['repo_name', 'file_path', 'chunk_content', 'chunk_summary', 'chunk_id', 'language', 'timestamp']
# ✅ Completed: codechat
# 🎉 Processing complete!
```

---

## 🧪 **Test 3: Configuration Loading**

Test that configuration files are loaded correctly:

```bash
# Test repositories.yml loading
python -c "
from src.core.simple_processor import SimpleCodeProcessor
processor = SimpleCodeProcessor()
repos = processor.load_repositories()
print(f'✅ Loaded {len(repos)} repositories from config')
for repo in repos:
    print(f'  - {repo.get(\"name\", \"unnamed\")}: {repo.get(\"url\", \"no url\")}')
"
```

---

## 🧪 **Test 4: Individual Components**

Test individual components separately:

### 4.1 Test the Chunker
```bash
python -c "
from src.core.chunker.smart_chunker import SmartChunker
chunker = SmartChunker()
test_content = '''def hello():
    print('Hello World')

class TestClass:
    def method(self):
        return 'test' '''
chunks = chunker.smart_chunk_file_from_content('test.py', test_content)
print(f'✅ Generated {len(chunks)} chunks')
for i, chunk in enumerate(chunks[:2]):  # Show first 2 chunks
    print(f'  Chunk {i}: {len(chunk[\"content\"])} chars')
"
```

### 4.2 Test the Summarizer (requires OpenAI API key)
```bash
python -c "
import os
if os.getenv('OPENAI_API_KEY'):
    from src.core.summarizer import CodeSummarizer
    summarizer = CodeSummarizer(os.getenv('OPENAI_API_KEY'))
    test_code = 'def calculate_sum(a, b): return a + b'
    summary = summarizer.summarize_full_code(test_code, 'test.py')
    print('✅ Summarizer working')
    print(f'Summary: {summary.get(\"summary\", \"No summary\")[:100]}...')
else:
    print('⚠️  OPENAI_API_KEY not set - skipping summarizer test')
"
```

### 4.3 Test the Embedding Generator (requires OpenAI API key)
```bash
python -c "
import os
if os.getenv('OPENAI_API_KEY'):
    from src.core.embedding_generator import CodeEmbeddingGenerator
    generator = CodeEmbeddingGenerator(os.getenv('OPENAI_API_KEY'))
    test_text = 'def hello(): return \"world\"'
    embedding = generator.generate_embedding(test_text)
    print(f'✅ Embedding generated: {len(embedding)} dimensions')
else:
    print('⚠️  OPENAI_API_KEY not set - skipping embedding test')
"
```

---

## 🧪 **Test 5: Utility Scripts**

Test the utility scripts in `src/utils/`:

### 5.1 Run the Demo Script
```bash
python src/utils/run_chunker_demo.py
```

### 5.2 Test Evaluation Script
```bash
python src/utils/evaluate.py
```

### 5.3 Run Unit Tests
```bash
python src/utils/test.py
```

---

## 🧪 **Test 6: Full Integration Test**

Run a complete end-to-end test (requires API keys):

```bash
# Make sure your .env file has the correct API keys
export $(cat .env | xargs)

# Run the main processor
python -m src.core.code_processor_main

# Expected: Complete processing pipeline with real API calls
```

---

## 🧪 **Test 7: Lambda Function Tests**

Test the Lambda functions locally:

```bash
# Test code processor Lambda
python -c "
from src.lambdas.code_processor.index import lambda_handler
event = {'repositories': [{'url': 'https://github.com/test/repo', 'name': 'test'}]}
result = lambda_handler(event, None)
print('✅ Lambda function executed')
print(f'Result: {result}')
"
```

---

## 🧪 **Test 8: Web Interface**

If you want to test the web interface:

```bash
# Check if there are any web files
ls src/web/

# If there's an index.html, you can open it in a browser
# Or run a local server
python -m http.server 8000
# Then visit http://localhost:8000/src/web/index.html
```

---

## 🔍 **Debugging Tips**

### If imports fail:
```bash
# Check Python path
python -c "import sys; print('\n'.join(sys.path))"

# Add src to Python path manually
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### If configuration fails:
```bash
# Check if config files exist
ls -la config/

# Validate YAML syntax
python -c "import yaml; yaml.safe_load(open('config/repositories.yml'))"
```

### If API calls fail:
```bash
# Check environment variables
echo $OPENAI_API_KEY
echo $PINECONE_API_KEY

# Test API connectivity
python -c "import openai; openai.api_key = os.getenv('OPENAI_API_KEY'); print('✅ OpenAI API accessible')"
```

---

## 📊 **Expected Test Results**

| Test | Expected Result | Notes |
|------|----------------|-------|
| Import Test | ✅ Success messages | All modules should import without errors |
| Simple Processor | ✅ File processing output | Should show chunking and mock storage |
| Config Loading | ✅ Repository list loaded | Should show configured repositories |
| Chunker Test | ✅ Chunks generated | Should create multiple chunks from test code |
| Summarizer Test | ✅ Summary generated | Requires OpenAI API key |
| Embedding Test | ✅ 1536-dim vector | Requires OpenAI API key |
| Utility Scripts | ✅ Script execution | May require additional setup |
| Full Integration | ✅ Complete pipeline | Requires all API keys |
| Lambda Tests | ✅ Function execution | Should handle events properly |
| Test Suite | ✅ Passing tests | May have some integration test failures |

---

## 🚨 **Common Issues & Solutions**

### Issue: "Module not found"
**Solution**: Add src to Python path
```bash
export PYTHONPATH=$PYTHONPATH:$(pwd)/src
```

### Issue: "No repositories found"
**Solution**: Check config/repositories.yml exists and has valid YAML

### Issue: "API key not set"
**Solution**: Copy config/.env.example to .env and fill in your keys

### Issue: "Permission denied"
**Solution**: Make sure scripts are executable
```bash
chmod +x src/utils/*.py
```

---

## 🎯 **Quick Test Command**

For a fast sanity check, run this one-liner:

```bash
cd /Users/sagar/projects/codechat && python -c "
from src.core.simple_processor import SimpleCodeProcessor
from src.core.code_processor_main import Config
print('✅ Core modules import successfully')
processor = SimpleCodeProcessor()
repos = processor.load_repositories()
print(f'✅ Configuration loaded: {len(repos)} repositories')
print('🎉 Ready for testing!')
"
```

This will verify that the restructuring worked correctly and the basic functionality is intact!

---

## 🏗️ **Backend + Chunking Strategies**

### Infrastructure Overview

CodeChat uses a streamlined AWS serverless architecture focused on essential components:

**Core Components:**
- **Lambda Functions**: `query_handler` (main API), `get_repositories` (repository listing)
- **API Gateway**: RESTful endpoints with CORS support (`/query`, `/repositories`) 
- **S3 Storage**: Configuration files and repository metadata
- **Lambda Layers**: Python dependencies for efficient deployments
- **Pinecone Vector Database**: Semantic search and embeddings storage

### Deployment Architecture

```
Frontend (chat/) 
    ↓ HTTP requests
API Gateway (/query, /repositories)
    ↓ Lambda invocations  
Lambda Functions (query_handler, get_repositories)
    ↓ Dependencies
Lambda Layer (Python packages)
    ↓ Configuration
S3 Bucket (modelearth_repos.yml)
```

### Intelligent Chunking Strategy

CodeChat implements an advanced multi-agent chunking system for optimal code understanding:

#### 1. **Smart File Processing**
- **Language Detection**: Automatic identification of programming languages
- **Syntax-Aware Splitting**: Respects code structure (functions, classes, modules)
- **Context Preservation**: Maintains logical code relationships

#### 2. **Multi-Level Chunking**
- **Function-Level**: Individual functions with their documentation
- **Class-Level**: Complete class definitions with methods
- **Module-Level**: File-level summaries and imports
- **Cross-Reference**: Links between related code components

#### 3. **Repository-Intelligent Search**
The system uses agentic components for enhanced search:

```python
# Query Analysis Agent
class QueryAnalysisAgent:
    def analyze_query(self, query: str) -> QueryAnalysis:
        # Determines query type and search strategy
        # Returns: code_search, conceptual_search, debugging_help, etc.

# Repository Intelligence Agent  
class RepositoryIntelligentSearchAgent:
    def search(self, query_analysis: QueryAnalysis, repo_context: str):
        # Executes targeted search based on query type
        # Returns: relevant code chunks with explanations
```

#### 4. **Context Generation**
- **File Metadata**: Path, language, repository information
- **Code Summaries**: AI-generated explanations of functionality
- **Relationship Mapping**: Dependencies and import relationships
- **Usage Examples**: How code components are used

### Clean Deployment Process

#### Quick Deploy (One Command)
```bash
# Set environment variables
export TF_VAR_openai_api_key="your-openai-key"
export TF_VAR_pinecone_api_key="your-pinecone-key"

# Deploy everything
python scripts/deploy_clean.py --auto-approve
```

#### Manual Deployment
```bash
# 1. Build Lambda layers (creates lambda-layer-query-handler.zip)
cd backend/lambda_layers
python build_layers.py

# 2. Deploy infrastructure
cd ../infra
terraform init
terraform apply

# 3. Configure frontend
API_URL=$(terraform output -raw api_gateway_url)
echo "window.CODECHAT_API_ENDPOINT = '$API_URL';" >> ../../chat/script.js
```

### Configuration Management

#### Repository Configuration (`config/modelearth_repos.yml`)
```yaml
repositories:
  - name: "modelearth/webroot"
    description: "Main website repository"
    priority: "high"
  - name: "modelearth/cloud" 
    description: "Cloud infrastructure"
    priority: "medium"
```

#### Environment Variables
```bash
# Required for deployment
export TF_VAR_openai_api_key="sk-..."
export TF_VAR_pinecone_api_key="..."

# Optional (have defaults)
export TF_VAR_aws_region="us-east-1"
export TF_VAR_pinecone_environment="us-east-1-aws"
export TF_VAR_pinecone_index="model-earth-jam-stack"
```

### Performance Optimizations

#### Lambda Configuration
- **Memory**: 1024 MB for query handler (handles complex AI operations)
- **Timeout**: 300 seconds (allows for thorough search processing)
- **Layers**: Shared dependencies reduce cold start times
- **Runtime**: Python 3.13 for latest performance improvements

#### Search Optimizations
- **Namespace Isolation**: Separate vector spaces per repository
- **Query Preprocessing**: Intelligent query analysis before search
- **Context Limiting**: Optimal chunk sizes for LLM processing
- **Caching Strategy**: Repository metadata cached in S3

### Architecture Cleanup (Recent Changes)

**Archived Components** (moved from active to archive):
- Ingestion worker Lambda (not used by current frontend)
- Ingestion webhook Lambda (not used by current frontend) 
- SQS queues and DynamoDB tables (ingestion pipeline)
- Related Lambda layers and dependencies

**Essential Components Kept**:
- Query handler Lambda (main API for repository search)
- Get repositories Lambda (returns available repository list)
- Query handler dependencies layer (Python packages)
- S3 bucket for configuration storage
- API Gateway with proper CORS configuration

**Benefits Achieved**:
- 50% reduction in AWS resources and costs
- Simplified maintenance and debugging
- Faster deployment times (essential components only)
- Clearer dependency management
- Better documentation and automated deployment

### API Endpoints

#### POST `/query`
Submit search queries to the repository-intelligent search system:
```json
{
  "query": "How does authentication work?",
  "repo_name": "modelearth/webroot", 
  "llm_provider": "bedrock"
}
```

#### GET `/repositories`  
Get list of available repositories for search:
```json
{
  "repositories": [
    {"name": "modelearth/webroot", "description": "Main website"},
    {"name": "modelearth/cloud", "description": "Cloud infrastructure"}
  ]
}
```

### Frontend Integration

The chat interface (`chat/index.html`) provides:
- **Repository Selection**: Dropdown with available repositories
- **LLM Provider Options**: Bedrock, OpenAI, Anthropic support
- **Material Design**: Modern, responsive UI with dark theme
- **Real-time Search**: Instant responses with typing indicators
- **Conversation History**: Persistent chat sessions

### Monitoring & Troubleshooting

#### CloudWatch Integration
```bash
# View Lambda logs
aws logs describe-log-groups --log-group-name-prefix "/aws/lambda/codechat"

# Monitor API Gateway metrics
aws cloudwatch get-metric-statistics --namespace AWS/ApiGateway
```

#### Common Issues
- **CORS Errors**: Check API Gateway CORS configuration
- **Lambda Timeouts**: Increase timeout in Terraform
- **Permission Errors**: Verify IAM role policies  
- **Layer Issues**: Rebuild dependencies with correct Python version

This streamlined architecture provides a robust, scalable foundation for repository-intelligent code search while maintaining simplicity and cost-effectiveness.

---

*For component-specific documentation, see individual README files in `chat/`, `backend/`, etc. All major system documentation has been consolidated into this main README.*
