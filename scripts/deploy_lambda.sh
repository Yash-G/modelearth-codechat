#!/bin/bash
# CodeChat Lambda Function Deployment Script

set -e
set -o pipefail

echo "🚀 Deploying CodeChat Lambda Function..."

# -----------------------------
# Configuration (tweak as needed)
# -----------------------------
LAMBDA_FUNCTION_NAME="${LAMBDA_FUNCTION_NAME:-codechat-api}"
LAMBDA_LAYER_NAME="${LAMBDA_LAYER_NAME:-codechat-dependencies-v1}"
REGION="${AWS_REGION:-us-east-1}"
RUNTIME="${RUNTIME:-python3.13}"          # Keep layer & function in sync
ZIP_FILE="lambda-function.zip"
LAYER_ZIP_FILE="${LAYER_ZIP_FILE:-lambda-layer.zip}"
DEBUG="${DEBUG:-false}"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# -----------------------------
# Prerequisites
# -----------------------------
echo "📋 Checking prerequisites..."

if ! command -v aws &> /dev/null; then
    echo -e "${RED}❌ AWS CLI is not installed. Please install it first.${NC}"
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}❌ Python 3 is not installed.${NC}"
    exit 1
fi

if ! command -v pip3 &> /dev/null; then
    echo -e "${RED}❌ pip3 is not installed.${NC}"
    exit 1
fi

# Check AWS credentials
if ! aws sts get-caller-identity &> /dev/null; then
    echo -e "${RED}❌ AWS credentials not configured. Please run 'aws configure'.${NC}"
    exit 1
fi

# Check for layer zip file
if [[ ! -f "$LAYER_ZIP_FILE" ]]; then
    echo -e "${RED}❌ Lambda layer file not found: $LAYER_ZIP_FILE${NC}"
    echo -e "${YELLOW}Please ensure ${LAYER_ZIP_FILE} exists in the current directory.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Prerequisites check passed${NC}"

# -----------------------------
# Create or reuse Lambda layer
# -----------------------------
echo "📦 Creating or locating Lambda layer..."

# Map runtime to compatible list for the layer (expand as needed)
COMPATIBLE_RUNTIMES="python3.9 python3.10 python3.11 python3.12"
if [[ "$RUNTIME" =~ ^python3\.[0-9]+$ ]]; then
  if [[ ! " $COMPATIBLE_RUNTIMES " =~ " $RUNTIME " ]]; then
    COMPATIBLE_RUNTIMES="$RUNTIME $COMPATIBLE_RUNTIMES"
  fi
fi

# Try to find the latest existing layer version ARN (LayerVersionArn)
LAYER_VERSION_ARN=$(aws lambda list-layer-versions \
    --layer-name "$LAMBDA_LAYER_NAME" \
    --region "$REGION" \
    --query 'sort_by(LayerVersions, &Version)[-1].LayerVersionArn' \
    --output text 2>/dev/null || echo "")

if [ -n "$LAYER_VERSION_ARN" ] && [ "$LAYER_VERSION_ARN" != "None" ] && [[ "$LAYER_VERSION_ARN" == arn:aws:lambda:* ]]; then
    echo -e "${YELLOW}ℹ️  Using existing Lambda layer: $LAYER_VERSION_ARN${NC}"
else
    echo "🆕 Creating new Lambda layer..."
    LAYER_RESPONSE=$(aws lambda publish-layer-version \
        --layer-name "$LAMBDA_LAYER_NAME" \
        --zip-file "fileb://$LAYER_ZIP_FILE" \
        --compatible-runtimes $COMPATIBLE_RUNTIMES \
        --region "$REGION" \
        --output json 2>&1)

    # Check for AWS CLI errors
    if [[ "$LAYER_RESPONSE" == *"error"* ]] || [[ "$LAYER_RESPONSE" == *"Error"* ]] || [[ "$LAYER_RESPONSE" == *"ValidationException"* ]]; then
        echo -e "${RED}❌ AWS CLI error creating layer: $LAYER_RESPONSE${NC}"
        exit 1
    fi

    # Extract the LayerVersionArn from the JSON response
    if command -v jq &> /dev/null && [[ "$LAYER_RESPONSE" == "{"* ]]; then
        LAYER_VERSION_ARN=$(echo "$LAYER_RESPONSE" | jq -r '.LayerVersionArn // empty' 2>/dev/null)
    elif [[ "$LAYER_RESPONSE" == "{"* ]]; then
        LAYER_VERSION_ARN=$(echo "$LAYER_RESPONSE" | sed -n 's/.*"LayerVersionArn"[[:space:]]*:[[:space:]]*"\([^"]*\)".*/\1/p')
    else
        # Fallback: try to grep the versioned ARN pattern
        LAYER_VERSION_ARN=$(echo "$LAYER_RESPONSE" | grep -o 'arn:aws:lambda:[^"]*:layer:[^":]*:[0-9]\+' | head -n1)
    fi

    if [ "$DEBUG" = "true" ]; then
        echo -e "${YELLOW}Debug: Full AWS response: $LAYER_RESPONSE${NC}"
        echo -e "${YELLOW}Debug: Extracted LayerVersionArn: '$LAYER_VERSION_ARN'${NC}"
        echo -e "${YELLOW}Debug: To test manually, run:${NC}"
        echo -e "${YELLOW}aws lambda publish-layer-version --layer-name $LAMBDA_LAYER_NAME --zip-file fileb://$LAYER_ZIP_FILE --compatible-runtimes $COMPATIBLE_RUNTIMES --region $REGION --output json${NC}"
    fi
fi

# Verify layer ARN was obtained successfully
if [ -z "$LAYER_VERSION_ARN" ] || [ "$LAYER_VERSION_ARN" = "None" ] || [[ "$LAYER_VERSION_ARN" != arn:aws:lambda:* ]]; then
    echo -e "${RED}❌ Failed to get Lambda layer version ARN${NC}"
    if [ "$DEBUG" = "true" ]; then
        echo -e "${YELLOW}Debug info: LAYER_VERSION_ARN='$LAYER_VERSION_ARN'${NC}"
    fi
    exit 1
fi

# Validate versioned ARN format (must include :version at the end)
# First trim any whitespace
LAYER_VERSION_ARN=$(echo "$LAYER_VERSION_ARN" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')

if [ "$DEBUG" = "true" ]; then
    echo -e "${YELLOW}Debug: Validating ARN: '$LAYER_VERSION_ARN'${NC}"
    echo -e "${YELLOW}Debug: ARN length: ${#LAYER_VERSION_ARN}${NC}"
fi

# Basic validation - check it starts with arn:aws:lambda: and ends with a number
if [[ "$LAYER_VERSION_ARN" != arn:aws:lambda:* ]] || [[ ! "$LAYER_VERSION_ARN" =~ :[0-9]+$ ]]; then
    echo -e "${RED}❌ Invalid layer ARN format: $LAYER_VERSION_ARN${NC}"
    echo -e "${YELLOW}Expected: arn:aws:lambda:region:account:layer:name:version${NC}"
    echo -e "${YELLOW}The ARN must start with 'arn:aws:lambda:' and end with a version number${NC}"
    exit 1
fi

if [ "$DEBUG" = "true" ]; then
    echo -e "${YELLOW}Debug: Layer ARN validated: $LAYER_VERSION_ARN${NC}"
fi

echo -e "${GREEN}✅ Lambda layer ready: $LAYER_VERSION_ARN${NC}"

# -----------------------------
# Build function deployment zip
# -----------------------------
echo "📦 Creating function deployment package..."

rm -rf lambda_deployment/
rm -f "$ZIP_FILE"

mkdir -p lambda_deployment

# Copy Lambda entrypoint
cp lambda_function.py lambda_deployment/

# Copy source code (adjust as needed)
mkdir -p lambda_deployment/src
cp -r src/core lambda_deployment/src/

# Create ZIP file (no dependencies — they're in the layer)
(
  cd lambda_deployment
  zip -r "../$ZIP_FILE" ./*
)

echo -e "${GREEN}✅ Function deployment package created: $ZIP_FILE${NC}"

# -----------------------------
# Create or update Lambda func
# -----------------------------
if aws lambda get-function --function-name "$LAMBDA_FUNCTION_NAME" --region "$REGION" &> /dev/null; then
    echo "🔄 Updating existing Lambda function code..."
    aws lambda update-function-code \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --zip-file "fileb://$ZIP_FILE" \
        --region "$REGION" >/dev/null

    echo "🔧 Updating function configuration (layers, runtime, memory, etc.)..."
    aws lambda update-function-configuration \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --runtime "$RUNTIME" \
        --layers "$LAYER_VERSION_ARN" \
        --timeout 30 \
        --memory-size 1024 \
        --region "$REGION" >/dev/null

else
    echo "🆕 Creating new Lambda function..."

    # Create IAM role if it doesn't exist
    ROLE_NAME="codechat-lambda-role"
    ROLE_ARN=$(aws iam get-role --role-name "$ROLE_NAME" --query 'Role.Arn' --output text 2>/dev/null || echo "")

    if [ -z "$ROLE_ARN" ]; then
        echo "👤 Creating IAM role..."
        ROLE_ARN=$(aws iam create-role \
            --role-name "$ROLE_NAME" \
            --assume-role-policy-document '{
                "Version": "2012-10-17",
                "Statement": [
                    {
                        "Effect": "Allow",
                        "Principal": { "Service": "lambda.amazonaws.com" },
                        "Action": "sts:AssumeRole"
                    }
                ]
            }' \
            --query 'Role.Arn' \
            --output text)

        # Attach basic execution role
        aws iam attach-role-policy \
            --role-name "$ROLE_NAME" \
            --policy-arn arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole >/dev/null

        # Wait for role to exist (safer than sleep)
        aws iam wait role-exists --role-name "$ROLE_NAME"
        echo "⏳ IAM role is ready."
    fi

    # Create Lambda function
    aws lambda create-function \
        --function-name "$LAMBDA_FUNCTION_NAME" \
        --runtime "$RUNTIME" \
        --role "$ROLE_ARN" \
        --handler lambda_function.lambda_handler \
        --zip-file "fileb://$ZIP_FILE" \
        --layers "$LAYER_VERSION_ARN" \
        --region "$REGION" \
        --timeout 30 \
        --memory-size 1024 \
        --environment "Variables={PINECONE_API_KEY=${PINECONE_API_KEY},OPENAI_API_KEY=${OPENAI_API_KEY},PINECONE_ENVIRONMENT=${PINECONE_ENVIRONMENT:-us-east-1-aws},PINECONE_INDEX_NAME=${PINECONE_INDEX_NAME:-model-earth}}" >/dev/null
fi

# -----------------------------
# Function URL (if configured)
# -----------------------------
FUNCTION_URL=$(aws lambda get-function-url-config \
    --function-name "$LAMBDA_FUNCTION_NAME" \
    --region "$REGION" \
    --query 'FunctionUrl' \
    --output text 2>/dev/null || echo "")

if [ -n "$FUNCTION_URL" ] && [ "$FUNCTION_URL" != "None" ]; then
    echo -e "${GREEN}✅ Lambda function deployed successfully!${NC}"
    echo -e "${YELLOW}🌐 Function URL: $FUNCTION_URL${NC}"
    echo ""
    echo "📝 Update your frontend script.js with this endpoint:"
    echo "   this.apiEndpoint = '$FUNCTION_URL';"
else
    echo -e "${YELLOW}⚠️  Lambda function deployed, but no function URL configured.${NC}"
    echo "   You may need to create a function URL manually in the AWS Console or via:"
    echo "   aws lambda create-function-url-config --function-name \"$LAMBDA_FUNCTION_NAME\" --auth-type NONE --region \"$REGION\""
fi

# -----------------------------
# Cleanup
# -----------------------------
rm -rf lambda_deployment/
echo -e "${GREEN}🧹 Cleanup completed${NC}"

echo ""
echo "🎉 Deployment complete!"
echo ""
echo "Next steps:"
echo "1. Update chat/script.js with the Lambda endpoint URL"
echo "2. Test the API endpoints (if Function URL exists):"
echo "   curl -X GET  \"$FUNCTION_URL/repositories\""
echo "   curl -X POST \"$FUNCTION_URL\" -H 'Content-Type: application/json' -d '{\"question\":\"How do I create a function?\"}'"
