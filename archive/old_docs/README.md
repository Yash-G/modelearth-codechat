# CodeChat Documentation# CodeChat Documentation



Welcome to CodeChat - an intelligent code querying system using RAG (Retrieval-Augmented Generation)!Welcome to the CodeChat documentation! This directory contains comprehensive guides for understanding, deploying, and working with the CodeChat system.



## 📖 Main Documentation## 📖 Documentation Overview



This documentation has been consolidated into two comprehensive guides:### 🏗️ System Design & Architecture

- **[System Design Document](SYSTEM_DESIGN.md)** - Complete system design with S3 archival integration

### 🏗️ [Module Overview](MODULES_OVERVIEW.md)- **[Architecture Overview](architecture.md)** - Technical architecture, current status, and future roadmap

**Complete guide to CodeChat architecture and components**

- System architecture and data flow### 🚀 Deployment & Operations

- Lambda functions and their responsibilities  - **[Lambda Deployment Guide](LAMBDA_README.md)** - AWS Lambda function deployment and configuration

- Core intelligence modules (SmartChunker, embeddings, etc.)- **[Local Development Setup](LOCAL_TESTING_README.md)** - Running CodeChat locally for development

- 40+ language-specific code chunkers

- Infrastructure and deployment components### 📊 Visual Resources

- **[img/](img/)** - Diagrams, flowcharts, and system visualizations

### 🛠️ [Setup & Operations](SETUP_OPERATIONS.md) - **[notebooks/](notebooks/)** - Jupyter notebooks for analysis and experimentation

**Everything you need to run and maintain CodeChat**

- Environment variables and configuration## 🎯 Quick Start Guide

- Script usage and deployment procedures

- Infrastructure setup with Terraform### For Developers

- Testing, monitoring, and troubleshooting1. Start with **[Local Development Setup](LOCAL_TESTING_README.md)** to get CodeChat running locally

- Daily operations and maintenance tasks2. Review **[Architecture Overview](architecture.md)** to understand the system design

3. Check **[System Design Document](SYSTEM_DESIGN.md)** for detailed implementation patterns

## 🚀 Quick Start

### For DevOps/Deployment

1. **First Time Setup**: Read [Setup & Operations](SETUP_OPERATIONS.md) for environment setup1. Review **[Lambda Deployment Guide](LAMBDA_README.md)** for AWS setup

2. **Understanding the System**: Review [Module Overview](MODULES_OVERVIEW.md) for architecture2. Follow **[Architecture Overview](architecture.md)** for infrastructure planning

3. **Start Developing**: Use `./scripts/run_local.sh` for local development3. Use **[System Design Document](SYSTEM_DESIGN.md)** for understanding data flow and integrations

4. **Deploy**: Follow Terraform and Lambda deployment procedures

## 🏛️ System Architecture Summary

## 📂 Document Structure

CodeChat is a serverless RAG (Retrieval Augmented Generation) system built on AWS:

```

docs/- **Frontend**: Simple HTML/JS chat interface

├── README.md                    # This overview (you are here)- **API**: AWS API Gateway + Lambda functions (Python 3.13)

├── MODULES_OVERVIEW.md          # Complete system architecture guide  - **Processing**: SQS queues for async repository ingestion  

├── SETUP_OPERATIONS.md          # Setup, deployment, and operations- **Storage**: Pinecone vector database for code embeddings

├── img/                         # Visual diagrams and flowcharts- **AI**: Google Gemini (primary) + OpenAI (fallback) for responses

└── archive/                     # Legacy/archived documentation- **Archival**: S3 buckets for data persistence and rollback

    ├── SYSTEM_DESIGN.md         # Original system design document

    ├── LAMBDA_README.md         # Original Lambda deployment guide## 🔧 Key Components

    ├── LOCAL_TESTING_README.md  # Original local testing guide

    └── architecture.md          # Original architecture document### Lambda Functions

```- **Query Handler** - Processes user questions via RAG pipeline

- **Ingestion Worker** - Processes repositories and creates embeddings

## 🎯 CodeChat System Summary- **Ingestion Webhook** - GitHub webhook endpoint for updates

- **Get Repositories** - Returns available repository list

CodeChat enables natural language queries against code repositories using:

### Core Technologies

- **Serverless Architecture**: AWS Lambda + API Gateway + SQS- **Pinecone**: Vector database for semantic code search

- **Vector Search**: Pinecone for semantic code search- **OpenAI**: Text embeddings and backup LLM

- **Intelligent Chunking**: 40+ language-specific code chunkers- **Google Gemini**: Primary language model for responses

- **AI Integration**: Google Gemini + OpenAI for responses- **AWS Lambda**: Serverless compute for all backend operations

- **Robust Storage**: S3 archival + Pinecone for durability- **Terraform**: Infrastructure as code for AWS resources



## 🔄 Development Workflow## 📂 Document Hierarchy



1. **Local Testing**: Use `./scripts/run_local.sh` to run CodeChat locally```

2. **Code Changes**: Modify Lambda functions in `src/lambdas/`docs/

3. **Infrastructure**: Update Terraform in `backend/infra/`├── OVERVIEW.md              # This overview (you are here)

4. **Deployment**: Use `./scripts/deploy_lambda.sh` for AWS deployment├── SYSTEM_DESIGN.md         # Complete system design document

5. **Bulk Ingestion**: Run `python ingestion.py` to process repositories├── LAMBDA_README.md         # Lambda deployment guide

├── LOCAL_TESTING_README.md  # Local development setup

## 📋 Key Features├── architecture.md          # Technical architecture details

├── img/                     # Visual diagrams and charts

- **Multi-Language Support**: 40+ programming languages with specialized chunkers├── notebooks/              # Analysis notebooks  

- **Semantic Search**: Vector-based code search with context awareness└── archive/                # Archived/legacy documentation

- **Real-time Chat**: Progressive response streaming and conversation history```

- **Scalable Architecture**: Serverless design handles traffic spikes

- **Backup & Recovery**: S3 archival with point-in-time restoration## 🔄 Development Workflow

- **Security**: HMAC validation, IAM roles, encrypted secrets

1. **Local Testing**: Use `LOCAL_TESTING_README.md` to run CodeChat locally

---2. **Code Changes**: Modify Lambda functions in `../src/lambdas/`

3. **Infrastructure**: Update Terraform in `../backend/infra/`

**Get Started**: Begin with [Setup & Operations](SETUP_OPERATIONS.md) to set up your CodeChat environment!4. **Deployment**: Follow `LAMBDA_README.md` for AWS deployment
5. **Monitoring**: Check AWS CloudWatch logs for issues

## ❓ Getting Help

- **Architecture Questions**: See `architecture.md`
- **Deployment Issues**: Check `LAMBDA_README.md`  
- **Local Setup Problems**: Follow `LOCAL_TESTING_README.md`
- **System Design**: Review `SYSTEM_DESIGN.md`

## 📋 Recent Changes

- ✅ Migrated to Python 3.13 runtime for all Lambda functions
- ✅ Implemented modular Lambda layers for reduced deployment size
- ✅ Added comprehensive debugging for Pinecone vector search
- ✅ Organized documentation with clear hierarchy and archived legacy files

---

# Namespace Strategy for ModelEarth Repositories

## Overview

CodeChat now uses **individual namespaces per repository** for better organization and query isolation in Pinecone. This approach provides significant benefits over using a single shared namespace.

## Current Configuration

- **Index**: `model-earth-jam-stack`
- **Namespace Pattern**: Each repository gets its own namespace based on the repository name
- **Example**: `modelearth/community-forecasting` → namespace: `community-forecasting`

## Benefits

### 1. **Query Isolation**
- Search within specific repositories when needed
- Avoid cross-repository contamination in results
- More precise and relevant search results

### 2. **Repository-Specific Operations**
- Update individual repositories without affecting others
- Rollback specific repositories independently
- Track repository-specific metrics and statistics

### 3. **Better Organization**
- Clear separation of concerns
- Easier debugging and maintenance
- Logical grouping of related code chunks

### 4. **Flexible Querying**
- Query all repositories (current default behavior)
- Query specific repositories by namespace
- Support for multi-repository queries with namespace filtering

## Implementation Details

### Configuration File Structure
```yaml
repositories:
  - name: modelearth/community-forecasting
    url: https://github.com/modelearth/community-forecasting.git
    description: Community-driven forecasting tools and models
    namespace: community-forecasting  # Individual namespace
    
processing:
  default_namespace: codechat-main  # Fallback if namespace not specified
  max_files_per_repo: 100
  chunk_size: 1000
  overlap: 200
  batch_size: 100
```

### Current Repository Namespaces

| Repository | Namespace |
|------------|-----------|
| modelearth/webroot | webroot |
| modelearth/localsite | localsite |
| modelearth/io | io |
| modelearth/cloud | cloud |
| modelearth/codechat | codechat |
| modelearth/community-forecasting | community-forecasting |
| modelearth/comparison | comparison |
| modelearth/exiobase | exiobase |
| modelearth/feed | feed |
| modelearth/home | home |
| modelearth/products | products |
| modelearth/profile | profile |
| modelearth/projects | projects |
| modelearth/realitystream | realitystream |
| modelearth/reports | reports |
| modelearth/swiper | swiper |
| modelearth/team | team |
| modelearth/apps | apps |
| modelearth/data-commons | data-commons |
| modelearth/machine-learning | machine-learning |
| modelearth/earthscape | earthscape |

**Total**: 21 unique namespaces (within Pinecone's 100 namespace limit per index)

## Query Behavior

### Default (All Repositories)
The query handler automatically searches across all namespaces and returns the best results regardless of repository. This maintains backward compatibility.

### Repository-Specific Queries
Future enhancement: Support query parameters to filter by specific repositories:
```javascript
{
  "question": "How does data processing work?",
  "repositories": ["io", "data-commons"]  // Only search these namespaces
}
```

## Migration Impact

### ✅ Backward Compatible
- Existing functionality unchanged
- Query handler still searches all namespaces
- No breaking changes to API

### 🔄 Enhanced Capabilities
- Better organization for future features
- Repository-specific analytics possible
- Easier maintenance and debugging

### 📊 Operational Benefits
- Clear separation of repository data
- Independent repository lifecycle management
- Better troubleshooting and monitoring

## Scaling Considerations

- **Current**: 21 namespaces (well within limits)
- **Capacity**: Up to 100 namespaces per Pinecone index
- **Future**: Can add ~79 more repositories before hitting limits
- **Growth Path**: Multiple indexes if needed for larger organizations

## Best Practices

1. **Namespace Naming**: Use simple, descriptive names (repository name without org prefix)
2. **Consistency**: All repositories in the same organization should follow the same pattern
3. **Documentation**: Keep this document updated as repositories are added/removed
4. **Monitoring**: Track namespace usage and performance metrics
5. **Testing**: Verify both all-namespace and single-namespace queries work correctly

## Usage Examples

### Bulk Ingestion
```bash
# Processes all repositories with their individual namespaces
python ingestion.py
```

### Lambda Processing
```bash
# Each repository message includes its target namespace
aws sqs send-message --queue-url $QUEUE_URL --message-body '{
  "repository": "modelearth/community-forecasting",
  "commit_sha": "main",
  "namespace": "community-forecasting"
}'
```

This namespace strategy provides a solid foundation for scaling CodeChat across the entire ModelEarth ecosystem while maintaining organization and performance.

**Next Steps**: Start with the [Local Development Setup](LOCAL_TESTING_README.md) if you're new to CodeChat!