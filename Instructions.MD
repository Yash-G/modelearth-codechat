# CodeChat Setup Instructions

This document provides complete step-by-step instructions to set up CodeChat on a new machine, including all prerequisites, dependencies, and deployment steps.

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [System Setup](#system-setup)
3. [Project Setup](#project-setup)
4. [AWS Configuration](#aws-configuration)
5. [API Keys Setup](#api-keys-setup)
6. [Lambda Layer Build](#lambda-layer-build)
7. [Infrastructure Deployment](#infrastructure-deployment)
8. [Frontend Configuration](#frontend-configuration)
9. [Testing & Verification](#testing--verification)
10. [Troubleshooting](#troubleshooting)

---

## 🔧 Prerequisites

### Required Software
- **macOS/Linux/Windows** with terminal access
- **Git** (latest version)
- **Python 3.13** (to match Lambda runtime)
- **Node.js** (for frontend development - optional)
- **AWS CLI v2**
- **Terraform** (≥ 1.0)

### Required Accounts & API Keys
- **AWS Account** with programmatic access
- **OpenAI API Key** (for AI responses)
- **Pinecone API Key** (for vector database)

---

## 🖥️ System Setup

### 1. Install Python 3.13

#### macOS (using Homebrew)
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install Python 3.13
brew install python@3.13

# Verify installation
python3.13 --version
```

#### Linux (Ubuntu/Debian)
```bash
# Update package list
sudo apt update

# Install Python 3.13
sudo apt install python3.13 python3.13-pip python3.13-venv

# Verify installation
python3.13 --version
```

### 2. Install AWS CLI v2

#### macOS
```bash
# Download and install AWS CLI v2
curl "https://awscli.amazonaws.com/AWSCLIV2.pkg" -o "AWSCLIV2.pkg"
sudo installer -pkg AWSCLIV2.pkg -target /

# Verify installation
aws --version
```

#### Linux
```bash
# Download and install AWS CLI v2
curl "https://awscli.amazonaws.com/awscli-exe-linux-x86_64.zip" -o "awscliv2.zip"
unzip awscliv2.zip
sudo ./aws/install

# Verify installation
aws --version
```

### 3. Install Terraform

#### Option A: Use the provided script (macOS only)
```bash
# This will be available after cloning the repository
./scripts/setup_terraform.sh
```

#### Option B: Manual installation
```bash
# macOS with Homebrew
brew tap hashicorp/tap
brew install hashicorp/tap/terraform

# Linux
wget -O- https://apt.releases.hashicorp.com/gpg | sudo gpg --dearmor -o /usr/share/keyrings/hashicorp-archive-keyring.gpg
echo "deb [signed-by=/usr/share/keyrings/hashicorp-archive-keyring.gpg] https://apt.releases.hashicorp.com $(lsb_release -cs) main" | sudo tee /etc/apt/sources.list.d/hashicorp.list
sudo apt update && sudo apt install terraform

# Verify installation
terraform --version
```

---

## 📁 Project Setup

### 1. Clone the Repository
```bash
# Clone the repository
git clone https://github.com/sagar8080/codechat.git
cd codechat

# Switch to the feature branch (if not already merged)
git checkout feature_lambda_backend
```

### 2. Create Python Virtual Environment
```bash
# Create virtual environment using Python 3.13
python3.13 -m venv venv

# Activate virtual environment
# macOS/Linux:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# Upgrade pip
python -m pip install --upgrade pip

# Install project dependencies
pip install -r requirements.txt
pip install -r backend/requirements.txt
```

---

## ☁️ AWS Configuration

### 1. Configure AWS Credentials
```bash
# Configure AWS CLI with your credentials
aws configure

# Enter the following when prompted:
# AWS Access Key ID: [Your Access Key]
# AWS Secret Access Key: [Your Secret Key]
# Default region name: us-east-1
# Default output format: json
```

### 2. Verify AWS Access
```bash
# Test AWS configuration
aws sts get-caller-identity

# This should return your AWS account information
```

### 3. Set Required AWS Permissions
Ensure your AWS user/role has the following permissions:
- `AmazonS3FullAccess`
- `AWSLambdaFullAccess`
- `IAMFullAccess`
- `AmazonAPIGatewayAdministrator`
- `CloudWatchLogsFullAccess`

---

## 🔑 API Keys Setup

### 1. OpenAI API Key
1. Visit [OpenAI Platform](https://platform.openai.com/api-keys)
2. Create a new API key
3. Save the key securely (you'll need it for deployment)

### 2. Pinecone API Key
1. Visit [Pinecone Console](https://app.pinecone.io/)
2. Create a new project or use existing
3. Navigate to API Keys section
4. Create a new API key
5. Note your environment (e.g., `us-east-1-aws`)
6. Create an index named `model-earth-jam-stack` with:
   - **Dimensions**: 1536 (for OpenAI embeddings)
   - **Metric**: cosine
   - **Pod Type**: p1.x1 (or starter for free tier)

---

## 🏗️ Lambda Layer Build

### 1. Build Lambda Layers
```bash
# Navigate to lambda layers directory
cd backend/lambda_layers

# Make build script executable
chmod +x build_layers.sh

# Build the layers locally
./build_layers.sh

# Verify the layer was created
ls -la lambda-layer-query-handler.zip
```

### 2. Optional: Publish Layers to AWS
```bash
# Publish layers to AWS (optional, Terraform will handle this)
./build_layers.sh --publish
```

---

## 🚀 Infrastructure Deployment

### 1. Initialize Terraform
```bash
# Navigate to infrastructure directory
cd backend/infra

# Initialize Terraform
terraform init
```

### 2. Create Terraform Variables File
```bash
# Create terraform.tfvars file
cat > terraform.tfvars << EOF
project_name = "codechat"
aws_region = "us-east-1"
openai_api_key = "your-openai-api-key-here"
pinecone_api_key = "your-pinecone-api-key-here"
pinecone_environment = "us-east-1-aws"
pinecone_index = "model-earth-jam-stack"
EOF

# ⚠️ IMPORTANT: Replace the placeholder values with your actual API keys
```

### 3. Plan and Apply Infrastructure
```bash
# Review the deployment plan
terraform plan

# Deploy the infrastructure
terraform apply

# When prompted, type 'yes' to confirm deployment
```

### 4. Note the Outputs
After successful deployment, note the output values:
```bash
# View outputs
terraform output

# You should see:
# api_gateway_url = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod"
# query_endpoint = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/query"
# repositories_endpoint = "https://xxxxxxxxxx.execute-api.us-east-1.amazonaws.com/prod/repositories"
```

---

## 🌐 Frontend Configuration

### 1. Update Frontend Configuration
```bash
# Navigate to chat directory
cd ../../chat

# Edit config.js file
nano config.js

# Update the API_ENDPOINT with your API Gateway URL:
# const API_ENDPOINT = 'https://your-api-id.execute-api.us-east-1.amazonaws.com/prod';
```

### 2. Test Frontend Locally
```bash
# Start a local web server
python3 -m http.server 3000

# Or alternatively:
# npx serve -s . -p 3000

# Open browser to: http://localhost:3000
```

---

## ✅ Testing & Verification

### 1. Test API Endpoints
```bash
# Test repositories endpoint
curl "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/repositories"

# Test query endpoint
curl -X POST "https://your-api-id.execute-api.us-east-1.amazonaws.com/prod/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "Hello, tell me about the codebase"}'
```

### 2. Test Frontend
1. Open browser to `http://localhost:3000`
2. Verify repositories load in the dropdown
3. Select a repository
4. Send a test message
5. Verify you receive an AI response

### 3. Verify Lambda Functions
```bash
# Check Lambda functions in AWS Console
aws lambda list-functions --query 'Functions[?contains(FunctionName, `codechat`)]'

# Check API Gateway
aws apigateway get-rest-apis --query 'items[?contains(name, `codechat`)]'
```

---

## 🔧 Troubleshooting

### Common Issues

#### 1. Lambda Layer Build Fails
```bash
# Ensure Python 3.13 is installed and accessible
python3.13 --version

# Check if pip is working
python3.13 -m pip --version

# Clean and rebuild
rm -f lambda-layer-query-handler.zip
./build_layers.sh
```

#### 2. Terraform Apply Fails
```bash
# Check AWS credentials
aws sts get-caller-identity

# Validate Terraform configuration
terraform validate

# Check for resource conflicts
terraform plan

# If resources already exist, import or destroy them
terraform destroy  # (only if safe to do so)
```

#### 3. CORS Issues in Frontend
- Verify API Gateway CORS configuration
- Check browser console for specific errors
- Ensure frontend config.js has correct API endpoint

#### 4. API Keys Not Working
- Verify OpenAI API key has sufficient credits
- Check Pinecone index exists and has correct dimensions
- Ensure API keys are correctly set in terraform.tfvars

#### 5. Frontend Not Loading Repositories
- Check API Gateway URLs in browser network tab
- Verify Lambda function logs in CloudWatch
- Test repositories endpoint directly with curl

### Getting Help

1. **Check Logs**: View Lambda function logs in AWS CloudWatch
2. **Terraform State**: Use `terraform show` to inspect current state
3. **AWS Console**: Check resources in AWS Console for status
4. **Network Tab**: Use browser developer tools to inspect API calls

### Clean Restart
If you need to start fresh:
```bash
# Destroy infrastructure
cd backend/infra
terraform destroy

# Clean local files
rm -rf .terraform/
rm terraform.tfstate*
rm lambda-layer-query-handler.zip

# Start over from Lambda Layer Build section
```

---

## 📚 Additional Resources

- [AWS CLI Documentation](https://docs.aws.amazon.com/cli/)
- [Terraform Documentation](https://www.terraform.io/docs)
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Pinecone Documentation](https://docs.pinecone.io/)
- [AWS Lambda Documentation](https://docs.aws.amazon.com/lambda/)