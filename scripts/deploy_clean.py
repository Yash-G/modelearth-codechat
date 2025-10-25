#!/usr/bin/env python3
"""Cross-platform helper to deploy the CodeChat infrastructure with Terraform.

This replaces the legacy deploy-clean.sh script. It performs these steps:

1. Verify the repository layout and required tooling (AWS CLI, Terraform).
2. Optionally rebuild the Lambda layer zip via build_layers.py.
3. Run Terraform init / validate / plan and, unless --plan-only is passed,
   terraform apply.
4. Print Terraform outputs so the caller can capture the API endpoints.

Example:
    python scripts/deploy_clean.py --auto-approve
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
INFRA_DIR = REPO_ROOT / "backend" / "infra"
LAYER_SCRIPT = REPO_ROOT / "backend" / "lambda_layers" / "build_layers.py"


class DeployError(RuntimeError):
    """Raised for expected deployment failures."""


def expect_repository_layout() -> None:
    if not INFRA_DIR.joinpath("main.tf").is_file():
        raise DeployError("backend/infra/main.tf not found. Run from the repository root.")


def ensure_command(name: str) -> None:
    if shutil.which(name) is None:
        raise DeployError(f"Required command not found in PATH: {name}")


def run(cmd: list[str], cwd: Path | None = None, env: dict[str, str] | None = None) -> None:
    pretty = " ".join(cmd)
    print(f"[cmd] {pretty}")
    subprocess.run(cmd, cwd=str(cwd) if cwd else None, env=env, check=True)


def verify_aws_credentials() -> None:
    try:
        subprocess.run(
            ["aws", "sts", "get-caller-identity"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=True,
        )
    except subprocess.CalledProcessError as exc:
        raise DeployError("AWS CLI credentials are not configured. Run 'aws configure'.") from exc


def build_layer(python_exec: Path) -> None:
    if not LAYER_SCRIPT.is_file():
        raise DeployError("Expected backend/lambda_layers/build_layers.py to exist.")
    run([str(python_exec), str(LAYER_SCRIPT)])


def run_terraform(auto_approve: bool, plan_only: bool) -> None:
    environment = os.environ.copy()
    for key in ("TF_VAR_openai_api_key", "TF_VAR_pinecone_api_key"):
        if not environment.get(key):
            print(f"[warn] {key} is not set; Terraform may prompt for it.")

    run(["terraform", "init"], cwd=INFRA_DIR)
    run(["terraform", "validate", "-no-color"], cwd=INFRA_DIR)
    run(["terraform", "plan", "-no-color"], cwd=INFRA_DIR)

    if plan_only:
        print("Plan finished. Skipping apply because --plan-only was provided.")
        return

    apply_cmd = ["terraform", "apply"]
    if auto_approve:
        apply_cmd.append("-auto-approve")
    run(apply_cmd, cwd=INFRA_DIR, env=environment)

    # Show outputs so the caller can easily find endpoints.
    run(["terraform", "output", "-json"], cwd=INFRA_DIR)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Deploy CodeChat infrastructure via Terraform")
    parser.add_argument(
        "--python",
        default=sys.executable,
        help="Python interpreter to use for building Lambda layers (default: current interpreter)",
    )
    parser.add_argument("--skip-layer", action="store_true", help="Skip rebuilding the Lambda layer zip")
    parser.add_argument("--plan-only", action="store_true", help="Run plan but skip terraform apply")
    parser.add_argument("--auto-approve", action="store_true", help="Pass -auto-approve to terraform apply")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        expect_repository_layout()

        python_path = Path(args.python)
        if not python_path.exists():
            raise DeployError(f"Python interpreter not found: {python_path}")

        ensure_command("aws")
        ensure_command("terraform")
        verify_aws_credentials()

        if args.skip_layer:
            print("Skipping Lambda layer build (per --skip-layer).")
        else:
            build_layer(python_path)

        run_terraform(auto_approve=args.auto_approve, plan_only=args.plan_only)
    except DeployError as exc:
        print(f"ERROR: {exc}")
        return 1
    except subprocess.CalledProcessError as exc:
        print(f"Command failed with exit code {exc.returncode}")
        return exc.returncode or 1

    print("Deployment steps completed successfully.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

