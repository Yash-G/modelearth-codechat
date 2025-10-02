# =============================================================================
# CodeChat Infrastructure - Essential Components Only
# =============================================================================
# This file deploys only the core components needed for the CodeChat application:
# - query_handler Lambda (main API)
# - get_repositories Lambda (repository listing)
# - API Gateway with proper CORS
# - S3 bucket for config storage
# - Essential Lambda layers
# =============================================================================

terraform {
  required_version = ">= 1.0"
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    archive = {
      source  = "hashicorp/archive"
      version = "~> 2.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# =============================================================================
# VARIABLES
# =============================================================================

variable "project_name" {
  description = "The name of the project"
  type        = string
  default     = "codechat"
}

variable "aws_region" {
  description = "AWS region for deployment"
  type        = string
  default     = "us-east-1"
}

variable "openai_api_key" {
  description = "API key for OpenAI"
  type        = string
  sensitive   = true
  default     = ""
}

variable "pinecone_api_key" {
  description = "API key for Pinecone"
  type        = string
  sensitive   = true
  default     = ""
}

variable "pinecone_environment" {
  description = "Pinecone environment"
  type        = string
  default     = "us-east-1-aws"
}

variable "pinecone_index" {
  description = "Pinecone index name"
  type        = string
  default     = "model-earth-jam-stack"
}

# =============================================================================
# PROVIDER & DATA SOURCES
# =============================================================================

provider "aws" {
  region = var.aws_region
}

data "aws_caller_identity" "current" {}

data "aws_region" "current" {}

# Random suffix for unique resource naming
# This prevents "EntityAlreadyExists" errors when resources already exist
# from previous deployments or other Terraform runs
resource "random_id" "suffix" {
  byte_length = 4
}

# =============================================================================
# LAMBDA LAYERS
# =============================================================================

resource "aws_lambda_layer_version" "query_handler_layer" {
  layer_name          = "${var.project_name}-query-handler-dependencies-${random_id.suffix.hex}"
  filename            = "${path.root}/../lambda_layers/lambda-layer-query-handler.zip"
  compatible_runtimes = ["python3.13"]
  source_code_hash    = filebase64sha256("${path.root}/../lambda_layers/lambda-layer-query-handler.zip")

  lifecycle {
    create_before_destroy = true
  }
}

# =============================================================================
# S3 BUCKET FOR CONFIG STORAGE
# =============================================================================

resource "aws_s3_bucket" "config_storage" {
  bucket = "${var.project_name}-config-${data.aws_caller_identity.current.account_id}-${random_id.suffix.hex}"

  tags = {
    Project     = var.project_name
    Environment = "production"
    Purpose     = "Configuration storage for CodeChat"
  }
}

resource "aws_s3_bucket_ownership_controls" "config_storage_ownership" {
  bucket = aws_s3_bucket.config_storage.id
  rule {
    object_ownership = "BucketOwnerEnforced"
  }
}

resource "aws_s3_bucket_versioning" "config_storage_versioning" {
  bucket = aws_s3_bucket.config_storage.id
  versioning_configuration {
    status = "Enabled"
  }
}

# Upload repository configuration
resource "aws_s3_object" "repos_config" {
  bucket = aws_s3_bucket.config_storage.id
  key    = "config/modelearth_repos.yml"
  source = "../../config/modelearth_repos.yml"
  etag   = filemd5("../../config/modelearth_repos.yml")

  tags = {
    Project = var.project_name
    Type    = "Configuration"
  }
}

# =============================================================================
# IAM ROLES
# =============================================================================

resource "aws_iam_role" "lambda_execution_role" {
  name = "${var.project_name}-lambda-execution-role-${random_id.suffix.hex}"

  assume_role_policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Action = "sts:AssumeRole"
        Effect = "Allow"
        Principal = {
          Service = "lambda.amazonaws.com"
        }
      }
    ]
  })

  tags = {
    Project = var.project_name
  }
}

resource "aws_iam_role_policy" "lambda_execution_policy" {
  name = "${var.project_name}-lambda-execution-policy-${random_id.suffix.hex}"
  role = aws_iam_role.lambda_execution_role.id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [
      {
        Effect = "Allow"
        Action = [
          "logs:CreateLogGroup",
          "logs:CreateLogStream",
          "logs:PutLogEvents"
        ]
        Resource = "arn:aws:logs:*:*:*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:GetObject",
          "s3:PutObject"
        ]
        Resource = "${aws_s3_bucket.config_storage.arn}/*"
      },
      {
        Effect = "Allow"
        Action = [
          "s3:ListBucket"
        ]
        Resource = aws_s3_bucket.config_storage.arn
      },
      {
        Effect = "Allow"
        Action = [
          "bedrock:InvokeModel"
        ]
        Resource = "*"
      }
    ]
  })
}

# =============================================================================
# LAMBDA FUNCTIONS
# =============================================================================

# Query Handler Lambda (Main API)
module "query_handler_lambda" {
  source = "./modules/lambda"

  function_name = "${var.project_name}-query-handler-${random_id.suffix.hex}"
  handler       = "index.lambda_handler"
  runtime       = "python3.13"
  source_path   = "../../src/lambdas/query_handler"
  role_arn      = aws_iam_role.lambda_execution_role.arn
  timeout       = 300
  memory_size   = 1024
  layers        = [aws_lambda_layer_version.query_handler_layer.arn]

  environment_variables = {
    OPENAI_API_KEY       = var.openai_api_key
    PINECONE_API_KEY     = var.pinecone_api_key
    PINECONE_ENVIRONMENT = var.pinecone_environment
    PINECONE_INDEX       = var.pinecone_index
    S3_CONFIG_BUCKET     = aws_s3_bucket.config_storage.id
  }

  aws_region     = data.aws_region.current.name
  aws_account_id = data.aws_caller_identity.current.account_id
}

# Repository Listing Lambda
module "get_repositories_lambda" {
  source = "./modules/lambda"

  function_name = "${var.project_name}-get-repositories-${random_id.suffix.hex}"
  handler       = "index.lambda_handler"
  runtime       = "python3.13"
  source_path   = "../../src/lambdas/get_repositories"
  role_arn      = aws_iam_role.lambda_execution_role.arn
  timeout       = 30
  memory_size   = 128
  layers        = [] # No external dependencies needed

  environment_variables = {
    S3_CONFIG_BUCKET = aws_s3_bucket.config_storage.id
  }

  aws_region     = data.aws_region.current.name
  aws_account_id = data.aws_caller_identity.current.account_id
}

# =============================================================================
# API GATEWAY
# =============================================================================

resource "aws_api_gateway_rest_api" "codechat_api" {
  name        = "${var.project_name}-api-${random_id.suffix.hex}"
  description = "CodeChat API Gateway"

  endpoint_configuration {
    types = ["REGIONAL"]
  }

  tags = {
    Project = var.project_name
  }
}

# Query endpoint
resource "aws_api_gateway_resource" "query_resource" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  parent_id   = aws_api_gateway_rest_api.codechat_api.root_resource_id
  path_part   = "query"
}

resource "aws_api_gateway_method" "query_post" {
  rest_api_id   = aws_api_gateway_rest_api.codechat_api.id
  resource_id   = aws_api_gateway_resource.query_resource.id
  http_method   = "POST"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "query_post_integration" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.query_resource.id
  http_method = aws_api_gateway_method.query_post.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.query_handler_lambda.invoke_arn
}

# Repositories endpoint
resource "aws_api_gateway_resource" "repositories_resource" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  parent_id   = aws_api_gateway_rest_api.codechat_api.root_resource_id
  path_part   = "repositories"
}

resource "aws_api_gateway_method" "repositories_get" {
  rest_api_id   = aws_api_gateway_rest_api.codechat_api.id
  resource_id   = aws_api_gateway_resource.repositories_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "repositories_get_integration" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.repositories_resource.id
  http_method = aws_api_gateway_method.repositories_get.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = module.get_repositories_lambda.invoke_arn
}

# CORS Configuration
resource "aws_api_gateway_method" "query_options" {
  rest_api_id   = aws_api_gateway_rest_api.codechat_api.id
  resource_id   = aws_api_gateway_resource.query_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_method" "repositories_options" {
  rest_api_id   = aws_api_gateway_rest_api.codechat_api.id
  resource_id   = aws_api_gateway_resource.repositories_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_integration" "query_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.query_resource.id
  http_method = aws_api_gateway_method.query_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

resource "aws_api_gateway_integration" "repositories_options_integration" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.repositories_resource.id
  http_method = aws_api_gateway_method.repositories_options.http_method

  type = "MOCK"
  request_templates = {
    "application/json" = "{\"statusCode\": 200}"
  }
}

# Method responses and integration responses for CORS
resource "aws_api_gateway_method_response" "query_options_200" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.query_resource.id
  http_method = aws_api_gateway_method.query_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_method_response" "repositories_options_200" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.repositories_resource.id
  http_method = aws_api_gateway_method.repositories_options.http_method
  status_code = "200"

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true
    "method.response.header.Access-Control-Allow-Methods" = true
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
}

resource "aws_api_gateway_integration_response" "query_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.query_resource.id
  http_method = aws_api_gateway_method.query_options.http_method
  status_code = aws_api_gateway_method_response.query_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

resource "aws_api_gateway_integration_response" "repositories_options_integration_response" {
  rest_api_id = aws_api_gateway_rest_api.codechat_api.id
  resource_id = aws_api_gateway_resource.repositories_resource.id
  http_method = aws_api_gateway_method.repositories_options.http_method
  status_code = aws_api_gateway_method_response.repositories_options_200.status_code

  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'"
    "method.response.header.Access-Control-Allow-Methods" = "'GET,OPTIONS,POST,PUT'"
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
}

# Lambda permissions
resource "aws_lambda_permission" "api_gateway_invoke_query" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = module.query_handler_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.codechat_api.execution_arn}/*/*"
}

resource "aws_lambda_permission" "api_gateway_invoke_repositories" {
  statement_id  = "AllowExecutionFromAPIGatewayRepositories"
  action        = "lambda:InvokeFunction"
  function_name = module.get_repositories_lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.codechat_api.execution_arn}/*/*"
}

# API Gateway deployment
resource "aws_api_gateway_deployment" "api_deployment" {
  depends_on = [
    aws_api_gateway_integration.query_post_integration,
    aws_api_gateway_integration.repositories_get_integration,
    aws_api_gateway_integration.query_options_integration,
    aws_api_gateway_integration.repositories_options_integration,
  ]

  rest_api_id = aws_api_gateway_rest_api.codechat_api.id

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "api_stage" {
  deployment_id = aws_api_gateway_deployment.api_deployment.id
  rest_api_id   = aws_api_gateway_rest_api.codechat_api.id
  stage_name    = "prod"

  tags = {
    Project = var.project_name
  }
}

# =============================================================================
# OUTPUTS
# =============================================================================

output "api_gateway_url" {
  description = "The URL of the API Gateway"
  value       = aws_api_gateway_stage.api_stage.invoke_url
}

output "query_endpoint" {
  description = "The query endpoint URL"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/query"
}

output "repositories_endpoint" {
  description = "The repositories endpoint URL"
  value       = "${aws_api_gateway_stage.api_stage.invoke_url}/repositories"
}

output "config_bucket" {
  description = "S3 bucket for configuration storage"
  value       = aws_s3_bucket.config_storage.id
}

output "lambda_functions" {
  description = "Deployed Lambda functions"
  value = {
    query_handler     = module.query_handler_lambda.arn
    get_repositories = module.get_repositories_lambda.arn
  }
}
