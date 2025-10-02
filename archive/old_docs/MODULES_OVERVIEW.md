# CodeChat System Modules Overview

This document provides a comprehensive overview of all CodeChat modules, their responsibilities, and how they work together to create an intelligent code querying system.

## 🏗️ System Architecture

CodeChat is a serverless RAG (Retrieval-Augmented Generation) system that enables natural language queries against code repositories. The system is built on AWS with the following key characteristics:

- **Frontend**: Simple HTML/JS chat interface
- **API**: AWS API Gateway + Lambda functions (Python 3.13)
- **Processing**: SQS queues for async repository ingestion
- **Storage**: Pinecone vector database for code embeddings + S3 for archival
- **AI**: Google Gemini (primary) + OpenAI (fallback) for responses
- **Infrastructure**: Terraform for infrastructure as code

## 📁 Core Lambda Functions

### 1. Query Handler (`src/lambdas/query_handler/`)

**Purpose**: Processes user questions using RAG pipeline

**Key Features**:
- Receives natural language queries from frontend
- Performs semantic search in Pinecone vector database
- Uses hybrid search (dense + sparse) for optimal results
- Generates contextual responses using Google Gemini or OpenAI
- Supports conversation history and repository filtering

**API Endpoints**:
- `POST /chat` - Process chat messages
- `POST /` - Alternative chat endpoint

**Dependencies**: `pinecone`, `openai`, `google-generativeai`

### 2. Ingestion Worker (`src/lambdas/ingestion_worker/`)

**Purpose**: Processes repositories and creates embeddings for search

**Key Features**:
- Clones repositories from GitHub using specific commit SHA
- Uses SmartChunker system for intelligent code segmentation
- Generates vector embeddings using OpenAI text-embedding models
- Stores vectors in Pinecone with comprehensive metadata
- Archives vectors to S3 for backup and recovery
- Processes SQS messages for batch ingestion

**Workflow**:
1. Receives repository processing job from SQS
2. Clones repository to temporary directory
3. Processes files using language-specific chunkers
4. Generates embeddings for each code chunk
5. Stores vectors in Pinecone with `live: false` initially
6. Archives to S3 for durability
7. Performs atomic activation by setting `live: true`

**Dependencies**: `GitPython`, `boto3`, `pinecone`, `openai`, `tiktoken`

### 3. Ingestion Webhook (`src/lambdas/ingestion_webhook/`)

**Purpose**: GitHub webhook endpoint for repository updates

**Key Features**:
- Receives GitHub webhook notifications (push, PR merge)
- Validates HMAC signatures for security
- Implements idempotency to prevent duplicate processing
- Queues repository processing jobs in SQS
- Handles repository authorization and validation

**Security**:
- HMAC validation using GitHub webhook secrets
- DynamoDB table for idempotency tracking
- Input validation and sanitization

**Dependencies**: `boto3`

### 4. Get Repositories (`src/lambdas/get_repositories/`)

**Purpose**: Returns list of available repositories

**Key Features**:
- Simple endpoint that lists available repositories
- Reads from Pinecone namespaces or configuration
- Used by frontend for repository dropdown
- Lightweight implementation using only Python stdlib

**API**: `GET /repositories`

## 🧠 Core Intelligence Modules

### SmartChunker System (`src/core/smart_chunker/`)

**Purpose**: Orchestrates intelligent code chunking across 40+ programming languages

**Key Components**:
- `smart_chunker.py` - Main orchestrator that coordinates language-specific chunkers
- Comprehensive chunking statistics and language detection
- Supports both Tree-sitter based parsing and pattern-based chunking
- Handles metadata extraction and context preservation

**Capabilities**:
- **Tree-sitter Languages**: 25+ languages with AST-based parsing
- **Pattern-based Languages**: 15+ languages with regex/heuristic chunking
- **Intelligent Sizing**: Respects token limits while preserving semantic boundaries
- **Context Awareness**: Maintains function/class context across chunks

### Language-Specific Chunkers (`src/core/chunking/`)

**Purpose**: Specialized chunkers for different programming languages

**Architecture**:
- Each language has dedicated chunker understanding syntax and semantics
- Base classes provide common functionality
- Tree-sitter integration for precise AST parsing
- Fallback patterns for unsupported languages

**Supported Languages Include**:
- **Web**: JavaScript, TypeScript, HTML, CSS, React/JSX
- **Backend**: Python, Java, C/C++, Go, Rust, PHP
- **Data**: SQL, JSON, YAML, Markdown
- **Mobile**: Swift, Kotlin, Dart/Flutter
- **Functional**: Haskell, Scala, Clojure
- **And 25+ more languages**

### Vector Database Client (`src/core/pine.py`)

**Purpose**: Manages all Pinecone vector database operations

**Key Features**:
- Connection management with proper authentication
- Vector upsert operations with batch processing
- Semantic search with metadata filtering
- Namespace management for repository isolation
- Error handling and retry logic
- Query optimization and result ranking

### Embedding Generator (`src/core/embedding_generator.py`)

**Purpose**: Creates vector embeddings from text content

**Key Features**:
- OpenAI text-embedding-3-small integration (1536 dimensions)
- Batch processing for efficiency
- Rate limiting and error handling
- Supports various embedding models
- Optimized for code and documentation content

## 🔄 Data Flow Architecture

### Ingestion Flow with S3 Archival

1. **Trigger**: GitHub webhook or manual ingestion script
2. **Validation**: HMAC verification and idempotency checks
3. **Queueing**: SQS message queuing for reliable processing
4. **Processing**: Repository cloning and intelligent chunking
5. **Embedding**: Vector generation using OpenAI embeddings
6. **Storage**: Pinecone upsert with comprehensive metadata
7. **Archival**: S3 backup for durability and rollback capability
8. **Activation**: Atomic switch to make vectors live for queries

### Query Flow

1. **Input**: User submits natural language query via chat interface
2. **Validation**: Query parameter validation and preprocessing
3. **Search**: Hybrid semantic and keyword search in Pinecone
4. **Context**: Result merging and context expansion
5. **Generation**: LLM response using retrieved code context
6. **Streaming**: Progressive token streaming to frontend

## 📊 Monitoring and Observability

### CloudWatch Integration
- Comprehensive logging for all Lambda functions
- Metrics tracking for ingestion and query performance
- Error monitoring with alerting
- Cost optimization insights

### S3 Archival System
- **Purpose**: Immutable backup and recovery system
- **Structure**: `s3://bucket/vectors/repo/commit_sha/`
- **Benefits**: 
  - Rollback capability to any previous commit
  - Auditability for compliance
  - Cost-effective long-term storage
  - Disaster recovery support

## 🛠️ Development Tools

### Bulk Ingestion (`ingestion.py`)

**Purpose**: Standalone script for initial repository processing

**Key Features**:
- Processes all repositories from YAML configuration
- Uses comprehensive SmartChunker system
- Supports both local and Lambda processing modes
- Batch processing with configurable concurrency
- Detailed progress reporting and statistics

### Deployment Scripts (`scripts/`)

**Purpose**: Automated deployment and management tools

**Scripts**:
- `deploy_lambda.sh` - AWS Lambda deployment automation
- `setup_terraform.sh` - Terraform installation for macOS
- `run_local.sh` - Local development environment setup
- `restore.py` - Vector restoration from S3 archives

## 🏛️ Infrastructure as Code

### Terraform Configuration (`backend/infra/`)

**Purpose**: Manages all AWS infrastructure declaratively

**Components**:
- **Lambda Functions**: All 4 Lambda functions with proper IAM roles
- **Lambda Layers**: Separate lightweight layers for each function
- **SQS Queues**: Reliable message queuing with dead letter queues
- **S3 Buckets**: Vector archives with lifecycle policies
- **DynamoDB**: Idempotency tracking tables
- **API Gateway**: RESTful API endpoints with CORS support
- **Secrets Manager**: Secure API key management

## 🔗 Integration Points

### Frontend Integration (`chat/`)
- Simple HTML/JS interface for user interaction
- Real-time chat with progressive response rendering
- Repository filtering and conversation history
- Responsive design for desktop and mobile

### CI/CD Integration (`.github/workflows/`)
- Automated testing and deployment
- Infrastructure validation
- Security scanning
- Performance monitoring

## 📈 Scalability Features

- **Serverless Architecture**: Auto-scaling Lambda functions
- **SQS Buffering**: Handles traffic spikes gracefully
- **Vector Database**: Pinecone scales to billions of vectors
- **S3 Storage**: Unlimited archival capacity
- **CDN Integration**: Fast global content delivery

## 🔒 Security Features

- **HMAC Validation**: Secure webhook authentication
- **IAM Roles**: Principle of least privilege
- **VPC Integration**: Network isolation options
- **Secrets Management**: Encrypted API key storage
- **Input Validation**: Comprehensive request sanitization

---

This modular architecture enables CodeChat to scale from small development teams to enterprise-level code repositories while maintaining high performance and reliability.