# CodeChat Setup & Operations Guide

This document contains all the important setup instructions, environment variables, script usage, and operational procedures for CodeChat.

## 🚀 Quick Start

### Prerequisites
- **Python 3.13+** installed
- **AWS CLI** configured with appropriate permissions
- **Git** installed
- **Terraform** (for infrastructure deployment)

### Environment Setup

```bash
# Clone the repository
git clone https://github.com/sagar8080/codechat.git
cd codechat

# Set up Python environment (for local development)
python3 -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt
```

## 🔑 Environment Variables

### Required API Keys (Environment Variables)

These are the **only** environment variables you need to set:

```bash
# Required API Keys
export PINECONE_API_KEY="your-pinecone-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"

# Optional API Keys (for enhanced functionality)
export GOOGLE_API_KEY="your-google-gemini-api-key"  # For Gemini responses
```

### AWS Infrastructure Variables (Only for Lambda/SQS mode)

Only set these if using Lambda processing or SQS queuing:

```bash
# AWS Configuration (only for Lambda mode)
export AWS_REGION="us-east-1"               # Default: us-east-1
export INGESTION_QUEUE_URL="https://sqs.us-east-1.amazonaws.com/account/queue-name"
export S3_ARCHIVE_BUCKET="codechat-vector-archives-your-account"
```

### Configuration Files (Not Environment Variables)

All other settings should be configured in `config/` files, not as environment variables:

**`config/config.toml`** (Application Configuration):
```toml
[pinecone]
environment = "us-east-1-aws"
index = "model-earth-jam-stack"
namespace = "codechat-main"

[openai]
model = "text-embedding-3-small"
dimensions = 1536

[chunking]
max_chunk_size = 1000
overlap_size = 100
max_workers = 4
batch_size = 100
```

**`ingestion.py`** (Script Configuration):
```python
# Configuration constants at top of file
DEFAULT_CONFIG_FILE = "config/modelearth_repos.yml"
PROCESSING_MODE = "local"  # "local" or "lambda"
BATCH_SIZE = 100          # Vectors per batch
MAX_WORKERS = 4           # Parallel threads
VERBOSE = True            # Show detailed progress
```

### Environment Files

Create a minimal `.env` file with **only API keys**:

```bash
# Copy the example file
cp config/.env.example .env

# Edit with your actual API keys only
nano .env
```

**Minimal `.env` file**:
```bash
# API Keys Only
PINECONE_API_KEY=pc-xyz123...
OPENAI_API_KEY=sk-xyz123...
GOOGLE_API_KEY=AIza...
```

## 🛠️ Scripts Usage

All utility scripts are located in the `scripts/` directory at the project root.

### 1. Local Development (`scripts/run_local.sh`)

**Purpose**: Start local development environment for testing

```bash
# Make executable (first time only)
chmod +x scripts/run_local.sh

# Start local server
./scripts/run_local.sh
```

**What it does**:
- Creates Python virtual environment if needed
- Installs all dependencies
- Starts Flask development server on `http://localhost:8000`
- Enables hot reload for development

**Testing Modes**:
- **Local Simulation** (default): No API keys needed, simulated responses
- **Lambda Proxy**: Set `USE_LOCAL_LAMBDA=false` to proxy to real Lambda

### 2. Infrastructure Setup (`scripts/setup_terraform.sh`)

**Purpose**: Install Terraform on macOS systems

```bash
chmod +x scripts/setup_terraform.sh
./scripts/setup_terraform.sh
```

**Features**:
- Detects macOS architecture (Intel/ARM)
- Downloads correct Terraform version (1.2.0)
- Installs to `/usr/local/bin`
- Verifies installation

### 3. Lambda Deployment (`scripts/deploy_lambda.sh`)

**Purpose**: Deploy Lambda functions to AWS

```bash
# Set environment variables first
export PINECONE_API_KEY="your-key"
export OPENAI_API_KEY="your-key"

# Make executable
chmod +x scripts/deploy_lambda.sh

# Deploy
./scripts/deploy_lambda.sh
```

**Configuration Options** (edit script for customization):
```bash
LAMBDA_FUNCTION_NAME="codechat-api"
LAMBDA_LAYER_NAME="codechat-dependencies-v1"
REGION="us-east-1"
RUNTIME="python3.13"
```

**What it does**:
- Validates prerequisites and AWS credentials
- Creates Lambda layer from dependencies
- Packages source code excluding dependencies
- Deploys/updates Lambda function
- Configures function URL if supported
- Provides endpoint URL for frontend integration

### 4. Vector Restoration (`scripts/restore.py`)

**Purpose**: Restore vectors from S3 archives

```bash
python scripts/restore.py --help

# Examples:
python scripts/restore.py --repo modelearth/webroot --commit abc123
python scripts/restore.py --list-archives
python scripts/restore.py --restore-latest --repo modelearth/localsite
```

## 📊 Bulk Ingestion

### Initial Repository Processing (`ingestion.py`)

**Purpose**: Process all repositories for initial setup

```bash
# From project root (ensure API keys are set as environment variables)
python ingestion.py
```

**Configuration**: Edit constants at top of `ingestion.py` file:
```python
DEFAULT_CONFIG_FILE = "config/modelearth_repos.yml"
PROCESSING_MODE = "local"  # "local" or "lambda"
BATCH_SIZE = 100          # Vectors per batch
MAX_WORKERS = 4           # Parallel threads
VERBOSE = True            # Show detailed progress
```

**Modes**:
- **Local Mode**: Processes on your machine, requires only API keys as environment variables
- **Lambda Mode**: Uses SQS to trigger Lambda workers, requires additional AWS configuration

**Expected Output**:
```
🚀 CodeChat Bulk Repository Ingestion
📚 Processing repositories using comprehensive language-specific chunkers
⚙️  Mode: local | Batch size: 100 | Workers: 4

📋 Loading configuration from: config/modelearth_repos.yml
📊 Found 17 repositories to process

📁 Processing repository: modelearth/webroot
   Cloning to: /tmp/repo_xyz/repo
   Processing: src/main.js
   ✅ Processed 45 files, generated 234 vectors
   📤 Uploading to Pinecone...
   ✅ Successfully uploaded 234 vectors to namespace 'codechat-main'
```

## 🏗️ Infrastructure Deployment

### Terraform Infrastructure (`backend/infra/`)

**One-time Setup**:
```bash
cd backend/infra

# Initialize Terraform
terraform init

# Plan deployment (review changes)
terraform plan

# Apply infrastructure
terraform apply
```

**Variables** (create `terraform.tfvars`):
```hcl
project_name = "codechat"
openai_api_key = "sk-..."
pinecone_api_key = "pc-..."
google_api_key = "AIza..."
pinecone_environment = "us-east-1-aws"
pinecone_index = "model-earth-jam-stack"
```

**Infrastructure Components Created**:
- 4 Lambda functions with separate lightweight layers
- SQS queue for ingestion jobs
- S3 bucket for vector archives
- DynamoDB table for idempotency
- IAM roles and policies
- API Gateway endpoints

### Lambda Layer Management

The system uses separate lightweight layers for each function:

```bash
# Layer files are in backend/lambda_layers/
ls backend/lambda_layers/
# lambda-layer-query-handler.zip
# lambda-layer-ingestion-worker.zip  
# lambda-layer-ingestion-webhook.zip
```

**Updating Layers**:
1. Update requirements in `lambda_layers/lambda_layer_*_requirements.txt`
2. Rebuild layer zip files
3. Run `terraform apply` to update

## 🧪 Testing

### Local Testing

1. **Start Local Server**:
   ```bash
   ./scripts/run_local.sh
   ```

2. **Open Browser**: Navigate to `http://localhost:8000`

3. **Test Chat Interface**:
   - Ask questions about code
   - Test repository filtering
   - Check conversation history

### Integration Testing

1. **Set Lambda Endpoint**:
   ```bash
   export LAMBDA_ENDPOINT="https://your-lambda-url.amazonaws.com/prod"
   export USE_LOCAL_LAMBDA=false
   ```

2. **Test API Endpoints**:
   ```bash
   # Test query endpoint
   curl -X POST https://your-lambda-url.amazonaws.com/prod/chat \
     -H "Content-Type: application/json" \
     -d '{"question": "How do I create a function?", "repository": "modelearth/localsite"}'

   # Test repositories endpoint  
   curl https://your-lambda-url.amazonaws.com/prod/repositories
   ```

## 📁 Configuration Files

### Repository Configuration (`config/modelearth_repos.yml`)

Defines repositories to process:
```yaml
repositories:
  - name: "modelearth/webroot"
    url: "https://github.com/modelearth/webroot.git"
    description: "Main community website"
  
  - name: "modelearth/localsite"
    url: "https://github.com/modelearth/localsite.git"
    description: "Local development framework"
```

### Application Configuration (`config/config.example.toml`)

Application-level settings:
```toml
[pinecone]
index = "model-earth-jam-stack"
namespace = "codechat-main"

[openai]
model = "text-embedding-3-small"
dimensions = 1536

[chunking]
max_chunk_size = 1000
overlap_size = 100
```

## 🔍 Monitoring & Debugging

### CloudWatch Logs

View Lambda function logs:
```bash
# Query Handler logs
aws logs tail /aws/lambda/codechat-query-handler --follow

# Ingestion Worker logs  
aws logs tail /aws/lambda/codechat-ingestion-worker --follow
```

### Pinecone Debugging

Check vector storage:
```python
from core.pine import PineconeClient
client = PineconeClient()
stats = client.index.describe_index_stats()
print(f"Total vectors: {stats.total_vector_count}")
```

### Common Issues & Solutions

**1. Import Errors in Lambda**
- Ensure Lambda layers contain all dependencies
- Check Python path configuration in Lambda functions

**2. Pinecone Connection Errors**
- Verify `PINECONE_API_KEY` environment variable is set
- Check Pinecone configuration in `config/config.toml` (environment, index, namespace)
- Ensure index exists in your Pinecone account

**3. OpenAI API Errors**
- Verify `OPENAI_API_KEY` environment variable is valid
- Check rate limits and billing
- Verify model configuration in `config/config.toml`

**4. SQS Permission Errors**
- Ensure Lambda execution role has SQS permissions
- Verify queue URL is correct

## 🔄 Operations

### Daily Operations

1. **Monitor Logs**: Check CloudWatch for errors
2. **Check Metrics**: Review ingestion and query performance
3. **Verify Backups**: Ensure S3 archives are being created

### Maintenance Tasks

1. **Update Dependencies**: Regularly update Lambda layers
2. **Clean Old Archives**: Review S3 lifecycle policies
3. **Monitor Costs**: Track AWS usage and Pinecone costs
4. **Security Updates**: Keep API keys rotated

### Disaster Recovery

1. **Restore from S3**: Use `scripts/restore.py` to recover vectors
2. **Rebuild Infrastructure**: Use Terraform to recreate resources
3. **Reprocess Repositories**: Use bulk ingestion to rebuild from scratch

---

This guide provides everything needed to set up, configure, and operate CodeChat successfully. Keep this document updated as the system evolves!