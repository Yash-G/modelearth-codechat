#!/bin/bash

# =============================================================================
# CodeChat Clean Deployment Script
# =============================================================================
# This script deploys the essential CodeChat infrastructure components only.
# It validates prerequisites, builds Lambda layers, and deploys via Terraform.
# =============================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if we're in the correct directory
if [ ! -f "backend/infra/main-clean.tf" ]; then
    log_error "Please run this script from the codechat project root directory"
    exit 1
fi

log_info "Starting CodeChat Clean Deployment"

# =============================================================================
# PREREQUISITES CHECK
# =============================================================================

log_info "Checking prerequisites..."

# Check AWS CLI
if ! command -v aws &> /dev/null; then
    log_error "AWS CLI not found. Please install it first."
    exit 1
fi

if ! aws sts get-caller-identity &> /dev/null; then
    log_error "AWS credentials not configured. Run: aws configure"
    exit 1
fi

log_success "AWS CLI configured"

# Check Terraform
if ! command -v terraform &> /dev/null; then
    log_error "Terraform not found. Please install it first."
    exit 1
fi

log_success "Terraform available"

# Check Python
if ! command -v python3 &> /dev/null; then
    log_error "Python3 not found"
    exit 1
fi

log_success "Python3 available"

# Check environment variables
if [ -z "$TF_VAR_openai_api_key" ]; then
    log_warning "TF_VAR_openai_api_key not set"
    log_info "Set with: export TF_VAR_openai_api_key='your-key'"
fi

if [ -z "$TF_VAR_pinecone_api_key" ]; then
    log_warning "TF_VAR_pinecone_api_key not set"
    log_info "Set with: export TF_VAR_pinecone_api_key='your-key'"
fi

# =============================================================================
# LAMBDA LAYER PREPARATION
# =============================================================================

log_info "Building Lambda layers..."

cd backend/lambda_layers

# Build query handler layer if it doesn't exist or requirements changed
if [ ! -f "lambda-layer-query-handler.zip" ] || [ "lambda_layer_query_handler_requirements.txt" -nt "lambda-layer-query-handler.zip" ]; then
    log_info "Building query handler layer..."
    
    # Create temporary directory
    rm -rf temp_layer
    mkdir -p temp_layer/python
    
    # Install dependencies
    pip3 install -r lambda_layer_query_handler_requirements.txt -t temp_layer/python/ --no-cache-dir
    
    # Create zip
    cd temp_layer
    zip -r ../lambda-layer-query-handler.zip python/
    cd ..
    
    # Cleanup
    rm -rf temp_layer
    
    log_success "Query handler layer built"
else
    log_info "Query handler layer is up to date"
fi

cd ../../

# =============================================================================
# TERRAFORM DEPLOYMENT
# =============================================================================

log_info "Deploying infrastructure with Terraform..."

cd backend/infra

# Initialize Terraform
log_info "Initializing Terraform..."
terraform init

# Validate configuration
log_info "Validating Terraform configuration..."
terraform validate

# Plan deployment
log_info "Planning deployment..."
terraform plan -var-file="terraform-clean.tfvars" -input=false

# Apply deployment
log_info "Applying deployment..."
terraform apply -var-file="terraform-clean.tfvars" -auto-approve

# Get outputs
API_URL=$(terraform output -raw api_gateway_url)
QUERY_ENDPOINT=$(terraform output -raw query_endpoint)
REPOSITORIES_ENDPOINT=$(terraform output -raw repositories_endpoint)

cd ../../

# =============================================================================
# FRONTEND CONFIGURATION
# =============================================================================

log_info "Updating frontend configuration..."

# Update the frontend with the API URL
cd chat
if [ -f "script.js" ]; then
    # Create backup
    cp script.js script.js.backup
    
    # Update API endpoint in script.js
    sed -i.tmp "s|window\.CODECHAT_API_ENDPOINT.*||g" script.js
    echo "window.CODECHAT_API_ENDPOINT = '$API_URL';" >> script.js
    rm script.js.tmp
    
    log_success "Frontend updated with API endpoint"
fi

cd ..

# =============================================================================
# DEPLOYMENT SUMMARY
# =============================================================================

log_success "CodeChat deployment completed successfully!"

echo ""
echo "==============================================================================="
echo "🎉 DEPLOYMENT SUMMARY"
echo "==============================================================================="
echo "API Gateway URL: $API_URL"
echo "Query Endpoint: $QUERY_ENDPOINT"
echo "Repositories Endpoint: $REPOSITORIES_ENDPOINT"
echo ""
echo "🌐 Frontend: Open chat/index.html in a browser"
echo "📚 Documentation: See DEPLOYMENT-GUIDE.md for details"
echo "🔧 Configuration: Update terraform-clean.tfvars as needed"
echo "==============================================================================="
echo ""

# Test the endpoints
log_info "Testing endpoints..."

if curl -s -o /dev/null -w "%{http_code}" "$REPOSITORIES_ENDPOINT" | grep -q "200"; then
    log_success "Repositories endpoint is responding"
else
    log_warning "Repositories endpoint may not be ready yet (this is normal for new deployments)"
fi

log_success "Deployment complete! 🚀"