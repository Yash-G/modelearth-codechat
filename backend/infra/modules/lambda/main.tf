# Terraform Module for Generic Lambda Function

variable "function_name" {
  description = "Name of the Lambda function"
  type        = string
}

variable "handler" {
  description = "Handler for the Lambda function"
  type        = string
}

variable "runtime" {
  description = "Runtime for the Lambda function"
  type        = string
}

variable "source_path" {
  description = "Path to the Lambda function source code"
  type        = string
}

variable "role_arn" {
  description = "IAM role ARN for the Lambda function"
  type        = string
}

variable "timeout" {
  description = "Timeout for the Lambda function in seconds"
  type        = number
  default     = 30
}

variable "memory_size" {
  description = "Memory size for the Lambda function in MB"
  type        = number
  default     = 128
}

variable "environment_variables" {
  description = "Environment variables for the Lambda function"
  type        = map(string)
  default     = {}
}

variable "sqs_trigger" {
  description = "SQS queue to trigger the Lambda function"
  type = object({
    queue_arn  = string
    batch_size = number
  })
  default = null
}

variable "provisioned_concurrency" {
  description = "Number of provisioned concurrent executions for the Lambda function"
  type        = number
  default     = 0
}

variable "layers" {
  description = "List of Lambda Layer ARNs to attach to the function"
  type        = list(string)
  default     = []
}

variable "aws_region" {
  description = "AWS region"
  type        = string
}

variable "aws_account_id" {
  description = "AWS account ID"
  type        = string
}

data "archive_file" "lambda_zip" {
  type        = "zip"
  source_dir  = var.source_path
  output_path = "${path.module}/../../../.terraform/zips/${var.function_name}.zip"
}

resource "aws_lambda_function" "this" {
  function_name = var.function_name
  handler       = var.handler
  runtime       = var.runtime
  role          = var.role_arn
  publish       = var.provisioned_concurrency > 0
  layers        = var.layers
  
  filename         = data.archive_file.lambda_zip.output_path
  source_code_hash = data.archive_file.lambda_zip.output_base64sha256
  
  timeout     = var.timeout
  memory_size = var.memory_size
  
  environment {
    variables = var.environment_variables
  }
  
  tags = {
    Project = "codechat"
  }
}

resource "aws_lambda_alias" "this" {
  count = var.provisioned_concurrency > 0 ? 1 : 0

  name             = "prod"
  description      = "Production alias"
  function_name    = aws_lambda_function.this.function_name
  function_version = aws_lambda_function.this.version
}

resource "aws_lambda_event_source_mapping" "sqs_mapping" {
  count = var.sqs_trigger != null ? 1 : 0
  
  event_source_arn = var.sqs_trigger.queue_arn
  function_name    = aws_lambda_function.this.arn
  batch_size       = var.sqs_trigger.batch_size
}

resource "aws_lambda_provisioned_concurrency_config" "this" {
  count = var.provisioned_concurrency > 0 ? 1 : 0

  function_name                     = aws_lambda_function.this.function_name
  provisioned_concurrent_executions = var.provisioned_concurrency
  qualifier                         = aws_lambda_alias.this[0].name
}

output "arn" {
  value = aws_lambda_function.this.arn
}

output "invoke_arn" {
  value = aws_lambda_function.this.invoke_arn
}
