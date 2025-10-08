#!/usr/bin/env python3
"""
Deploy CodeChat backend to AWS Lambda using a container image.

Prereqs
- Python 3.9+
- Docker CLI installed and running
- AWS credentials configured (env vars, ~/.aws, or SSO); permissions for ECR, Lambda, IAM
- pip install boto3 python-dotenv (optional for .env support)

Usage
  # Zero-args (auto-detect region and secrets):
  python scripts/deploy_lambda.py

  # Explicit region + use env vars already exported in your shell:
  python scripts/deploy_lambda.py --region us-east-1 \
    --repo codechat-lambda --function codechat-lambda --role codechat-lambda-role \
    --use-env

  # Read keys from a .env file (OPENAI_API_KEY, PINECONE_API_KEY, GOOGLE_API_KEY)
  python scripts/deploy_lambda.py --region us-east-1 \
    --repo codechat-lambda --function codechat-lambda --role codechat-lambda-role \
    --env-file codechat/.env

This script is idempotent: re-running updates the Lambda code and URL CORS.
"""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import time
from typing import Dict, List, Optional

try:
    import boto3  # type: ignore
    from botocore.exceptions import ClientError  # type: ignore
except Exception as e:  # pragma: no cover
    print("boto3 is required. Install with: pip install boto3", file=sys.stderr)
    raise
from botocore.session import Session as BotoCoreSession  # for profile discovery

# Optional: dotenv
def load_env_file(path: str) -> Dict[str, str]:
    data: Dict[str, str] = {}
    try:
        from dotenv import dotenv_values  # type: ignore
        values = dotenv_values(path)
        for k, v in values.items():
            if isinstance(v, str):
                data[k] = v
    except Exception:
        # Fallback: minimal parser (KEY=VALUE lines)
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith("#"):
                        continue
                    if "=" in line:
                        k, v = line.split("=", 1)
                        data[k.strip()] = v.strip().strip('"')
    return data


def sh(cmd: List[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    print("$", " ".join(cmd))
    return subprocess.run(cmd, check=check, capture_output=capture, text=True)


def ecr_login(ecr, registry: str, region: str) -> None:
    # Use ECR authorization token; pass password via STDIN to avoid CLI warning
    auth = ecr.get_authorization_token()
    token = auth["authorizationData"][0]["authorizationToken"]
    username_password = base64.b64decode(token).decode("utf-8")  # 'AWS:password'
    _, password = username_password.split(":", 1)
    print(f"$ docker login {registry} (password via stdin)")
    subprocess.run(["docker", "login", "-u", "AWS", "--password-stdin", registry], input=password, text=True, check=True)


def ensure_ecr_repo(ecr, name: str, region: str) -> None:
    try:
        ecr.describe_repositories(repositoryNames=[name])
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "RepositoryNotFoundException":
            ecr.create_repository(repositoryName=name)
        else:
            raise


def build_and_push_image(repo_name: str, registry: str, tag: str) -> str:
    image_local = f"{repo_name}:latest"
    image_uri = f"{registry}/{repo_name}:{tag}"
    # Prefer buildx to ensure linux/amd64 single-arch image compatible with Lambda
    try:
        bx = subprocess.run(["docker", "buildx", "version"], capture_output=True, text=True)
        if bx.returncode == 0:
            sh(["docker", "buildx", "build", "--platform", "linux/amd64", "--load", "-t", image_local, "."])  # load into local docker
        else:
            # Fallback: set platform via env for classic build
            env = os.environ.copy()
            env["DOCKER_DEFAULT_PLATFORM"] = "linux/amd64"
            print("$ DOCKER_DEFAULT_PLATFORM=linux/amd64 docker build -t", image_local, ".")
            subprocess.run(["docker", "build", "-t", image_local, "."], check=True, env=env)
    except FileNotFoundError:
        env = os.environ.copy()
        env["DOCKER_DEFAULT_PLATFORM"] = "linux/amd64"
        print("$ DOCKER_DEFAULT_PLATFORM=linux/amd64 docker build -t", image_local, ".")
        subprocess.run(["docker", "build", "-t", image_local, "."], check=True, env=env)
    sh(["docker", "tag", image_local, image_uri])
    sh(["docker", "push", image_uri])
    return image_uri


def ensure_iam_role(iam, role_name: str) -> str:
    try:
        out = iam.get_role(RoleName=role_name)
        return out["Role"]["Arn"]
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") != "NoSuchEntity":
            raise
    trust = {
        "Version": "2012-10-17",
        "Statement": [
            {
                "Effect": "Allow",
                "Principal": {"Service": "lambda.amazonaws.com"},
                "Action": "sts:AssumeRole",
            }
        ],
    }
    iam.create_role(
        RoleName=role_name,
        AssumeRolePolicyDocument=json.dumps(trust),
        Description="Execution role for CodeChat Lambda",
    )
    iam.attach_role_policy(
        RoleName=role_name,
        PolicyArn="arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole",
    )
    time.sleep(5)
    out = iam.get_role(RoleName=role_name)
    return out["Role"]["Arn"]


def ensure_lambda(
    lam,
    function_name: str,
    image_uri: str,
    role_arn: str,
    region: str,
    env_vars: Optional[Dict[str, str]] = None,
) -> None:
    try:
        lam.get_function(FunctionName=function_name)
        lam.update_function_code(FunctionName=function_name, ImageUri=image_uri)
        # Wait briefly for update to settle before changing configuration
        try:
            waiter = lam.get_waiter('function_updated')
            waiter.wait(FunctionName=function_name, WaiterConfig={'Delay': 2, 'MaxAttempts': 15})
        except Exception:
            time.sleep(3)
        if env_vars:
            for attempt in range(1, 8):
                try:
                    lam.update_function_configuration(
                        FunctionName=function_name, Environment={"Variables": env_vars}
                    )
                    break
                except ClientError as ce:
                    if "ResourceConflictException" in str(ce) and attempt < 7:
                        time.sleep(2 * attempt)
                        continue
                    raise
    except ClientError as e:
        if e.response.get("Error", {}).get("Code") == "ResourceNotFoundException":
            kwargs = dict(
                FunctionName=function_name,
                PackageType="Image",
                Code={"ImageUri": image_uri},
                Role=role_arn,
                Timeout=30,
                MemorySize=1024,
            )
            if env_vars:
                kwargs["Environment"] = {"Variables": env_vars}
            # Retry create_function to allow IAM role propagation
            last_err: Optional[Exception] = None
            for attempt in range(1, 8):
                try:
                    lam.create_function(**kwargs)
                    last_err = None
                    break
                except ClientError as ce:
                    msg = str(ce)
                    if ("cannot be assumed" in msg) or ("InvalidParameterValue" in msg):
                        time.sleep(3 * attempt)
                        last_err = ce
                        continue
                    raise
            if last_err:
                raise last_err
        else:
            raise


def ensure_function_url(
    lam,
    function_name: str,
    allow_origins: List[str],
    allow_methods: List[str],
    allow_headers: List[str],
) -> str:
    try:
        lam.create_function_url_config(FunctionName=function_name, AuthType="NONE")
    except ClientError:
        pass
    cors = {
        "AllowOrigins": allow_origins,
        "AllowMethods": allow_methods,
        "AllowHeaders": allow_headers,
        "AllowCredentials": False,
    }
    lam.update_function_url_config(FunctionName=function_name, Cors=cors)
    # Ensure public invoke permission for Function URL (AuthType NONE)
    try:
        lam.add_permission(
            FunctionName=function_name,
            StatementId="allow_public_invoke",
            Action="lambda:InvokeFunctionUrl",
            Principal="*",
            FunctionUrlAuthType="NONE",
        )
    except ClientError as e:
        # Ignore if the statement already exists or similar benign conflicts
        msg = str(e)
        if "Statement already exists" not in msg and "ResourceConflictException" not in msg:
            raise
    out = lam.get_function_url_config(FunctionName=function_name)
    return out["FunctionUrl"]


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description="Deploy CodeChat Lambda (container image)")
    p.add_argument("--region")
    p.add_argument("--profile", help="AWS profile name (auto-detected if not set)")
    p.add_argument("--repo", dest="repo_name", default="codechat-lambda")
    p.add_argument("--function", dest="function_name", default="codechat-lambda")
    p.add_argument("--role", dest="role_name", default="codechat-lambda-role")
    p.add_argument("--image-tag", dest="image_tag", default="latest")
    p.add_argument("--use-env", action="store_true", help="Use OPENAI_API_KEY, PINECONE_API_KEY, GOOGLE_API_KEY from environment")
    p.add_argument("--env-file", help="Path to .env with OPENAI_API_KEY, PINECONE_API_KEY, GOOGLE_API_KEY")
    p.add_argument("--allow-origins", default="*", help="Comma-separated list (default: *)")
    p.add_argument("--allow-methods", default="GET,POST", help="Comma-separated list (default: GET,POST)")
    p.add_argument("--allow-headers", default="*", help="Comma-separated list (default: *)")
    return p.parse_args()


def main() -> None:
    args = parse_args()
    # Resolve profile first for more accurate region lookup
    resolved_profile: Optional[str] = None
    if args.profile:
        resolved_profile = args.profile
    else:
        resolved_profile = os.getenv("AWS_PROFILE") or os.getenv("AWS_DEFAULT_PROFILE")
        if not resolved_profile:
            profiles = getattr(BotoCoreSession(), "available_profiles", [])
            non_default = [p for p in profiles if p != "default"]
            if len(non_default) == 1:
                resolved_profile = non_default[0]
            elif "personal" in non_default:
                resolved_profile = "personal"

    # Resolve region: CLI arg -> env -> profile config -> boto3 default -> us-east-1
    profile_region = None
    try:
        if resolved_profile:
            profile_region = BotoCoreSession(profile=resolved_profile).get_config_variable("region")
    except Exception:
        profile_region = None
    resolved_region = (
        args.region
        or os.getenv("AWS_REGION")
        or os.getenv("AWS_DEFAULT_REGION")
        or profile_region
        or boto3.Session().region_name
        or "us-east-1"
    )

    if resolved_profile:
        print(f"Using AWS profile: {resolved_profile}")
    print(f"Using AWS region: {resolved_region}")

    session = boto3.Session(profile_name=resolved_profile, region_name=resolved_region)
    sts = session.client("sts")
    ecr = session.client("ecr")
    iam = session.client("iam")
    lam = session.client("lambda")

    account_id = sts.get_caller_identity()["Account"]
    registry = f"{account_id}.dkr.ecr.{resolved_region}.amazonaws.com"

    # Ensure ECR repository
    ensure_ecr_repo(ecr, args.repo_name, resolved_region)

    # Login to ECR and push image
    ecr_login(ecr, registry, resolved_region)
    image_uri = build_and_push_image(args.repo_name, registry, args.image_tag)

    # Ensure IAM role
    role_arn = ensure_iam_role(iam, args.role_name)

    # Env vars (auto-detect unless explicitly skipped)
    env_vars: Optional[Dict[str, str]] = None
    candidates: List[str] = []
    if args.env_file:
        candidates.append(args.env_file)
    else:
        candidates.extend(["codechat/.env", ".env"])

    detected: Dict[str, str] = {}
    for path in candidates:
        if os.path.exists(path):
            detected.update({k: v for k, v in load_env_file(path).items() if v})
            break
    for k in ("OPENAI_API_KEY", "PINECONE_API_KEY", "GOOGLE_API_KEY"):
        v = os.getenv(k)
        if v:
            detected[k] = v
    if detected:
        env_vars = detected
        missing = [k for k in ("OPENAI_API_KEY", "PINECONE_API_KEY", "GOOGLE_API_KEY") if k not in env_vars]
        if missing:
            print(f"Warning: missing vars {missing}; Lambda will keep existing values if present.")

    # Ensure Lambda
    ensure_lambda(lam, args.function_name, image_uri, role_arn, resolved_region, env_vars)

    # Function URL + CORS
    url = ensure_function_url(
        lam,
        args.function_name,
        [s.strip() for s in args.allow_origins.split(",") if s.strip()],
        [s.strip() for s in args.allow_methods.split(",") if s.strip()],
        [s.strip() for s in args.allow_headers.split(",") if s.strip()],
    )

    print("\nDeployment complete.")
    print("Function URL:", url)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as e:
            print(f"Command failed: {e}", file=sys.stderr)
            sys.exit(e.returncode)
    except ClientError as e:
        print(f"AWS error: {e}", file=sys.stderr)
        sys.exit(2)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)
