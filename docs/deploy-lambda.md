# Deploying the CodeChat Backend to AWS Lambda

This guide uses a single, cross-platform Python script that leverages the AWS SDK (boto3) and Docker. It creates or updates the Lambda function from a container image, configures a public Function URL with CORS, and prints the HTTPS URL.

Prerequisites
- AWS account and credentials configured (env vars, ~/.aws/credentials, or SSO)
- Docker installed and running
  - Windows/macOS: Install Docker Desktop (see: https://docs.docker.com/desktop/)
  - Linux: Install Docker Engine (see: https://docs.docker.com/engine/install/)
- Python 3.9+
- Install: `pip install boto3 python-dotenv` (dotenv is only needed if you use `--env-file`)

Script
- Path: `scripts/deploy_lambda.py`
- Safe to re-run: it updates the container image, Lambda code, and CORS config.

Recommended names (defaults)
- Region: `us-east-1` (used if none detected)
- ECR repo: `codechat-lambda`
- Lambda name: `codechat-lambda`
- IAM role: `codechat-lambda-role` (created if missing; basic logs policy attached)

Secrets options
- `--use-env` reads `OPENAI_API_KEY`, `PINECONE_API_KEY`, `GOOGLE_API_KEY` from your shell environment.
- `--env-file` reads the same keys from a `.env` file (e.g., `codechat/.env`).
- With no flags, the script auto-detects secrets in this order: `codechat/.env` → `.env` → current shell env. If none found, it leaves Lambda env unchanged.

Profile detection
- Optional `--profile` to target a specific AWS profile.
- If not provided, the script resolves a profile automatically:
  - Uses `AWS_PROFILE`/`AWS_DEFAULT_PROFILE` if set.
  - Otherwise, if exactly one non-`default` profile exists, it uses that.
  - If multiple profiles exist, it tries `personal`; else it falls back to the default AWS SDK resolution chain.

Quickstart

0) No-args (auto-detect region and secrets if available)
```bash
python scripts/deploy_lambda.py
```

1) Use shell environment variables explicitly
```bash
export OPENAI_API_KEY=...
export PINECONE_API_KEY=...
export GOOGLE_API_KEY=...
python scripts/deploy_lambda.py --region us-east-1 --use-env
```

2) Use a .env file
```bash
python scripts/deploy_lambda.py --region us-east-1 --env-file codechat/.env
```

What the script does
1. Ensures an ECR repository exists (creates if needed).
2. Builds the Docker image and pushes it to ECR.
3. Ensures an IAM execution role exists (creates + attaches basic logs policy if needed).
4. Creates or updates the Lambda function from the image.
5. Creates/updates a Function URL with CORS (GET/POST, `*` origin by default).
6. Prints the Function URL.

Hook up the UI
- Open `chat/script.js` and set `this.apiEndpoint` to the printed Function URL (no trailing slash). Do not commit that URL to the repo.
- Serve the site (e.g., `python -m http.server 8887`) and open `/codechat/chat/`.

Quick test (optional)
```bash
URL=$(python scripts/deploy_lambda.py | awk '/Function URL:/ {print $3}' | tail -n1)
curl -s "$URL/repositories"
```

Notes
- CORS is handled at the Function URL layer; the Lambda handler does not add `Access-Control-Allow-*` headers.
- No secrets or account-specific URLs are committed by this process.
