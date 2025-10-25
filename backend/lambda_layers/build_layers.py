#!/usr/bin/env python3
"""
Cross-platform Lambda layer builder for CodeChat.

Replaces backend/lambda_layers/build_layers.sh

Builds the query-handler layer zip at:
  backend/lambda_layers/lambda-layer-query-handler.zip

Optional: --publish will publish the layer using AWS CLI, if available.
"""
from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from zipfile import ZipFile


HERE = Path(__file__).resolve().parent
REQ_FILE = HERE / "lambda_layer_query_handler_requirements.txt"
OUT_ZIP = HERE / "lambda-layer-query-handler.zip"


def run(cmd: list[str], cwd: Path | None = None, check: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(cmd, cwd=str(cwd) if cwd else None, check=check)


def zipdir(source_dir: Path, zip_path: Path) -> None:
    with ZipFile(zip_path, "w") as zf:
        for root, _, files in os.walk(source_dir):
            for f in files:
                p = Path(root) / f
                zf.write(p, p.relative_to(source_dir))


def build_layer(python_exe: Path, publish: bool) -> None:
    if not REQ_FILE.is_file():
        raise FileNotFoundError(f"Requirements file not found: {REQ_FILE}")

    tmpdir = Path(tempfile.mkdtemp(prefix="codechat_layer_", dir=str(HERE)))
    try:
        target = tmpdir / "python"
        target.mkdir(parents=True, exist_ok=True)

        run([str(python_exe), "-m", "pip", "--version"])  # sanity
        run([str(python_exe), "-m", "pip", "install", "--upgrade", "pip"])  # ensure recent pip
        run([str(python_exe), "-m", "pip", "install", "-r", str(REQ_FILE), "--no-cache-dir", "--target", str(target)])

        if OUT_ZIP.exists():
            OUT_ZIP.unlink()
        zipdir(tmpdir, OUT_ZIP)

        print(f"Built layer: {OUT_ZIP} ({OUT_ZIP.stat().st_size // 1024} KiB)")

        if publish:
            aws = shutil.which("aws")
            if not aws:
                raise RuntimeError("AWS CLI not found in PATH; install it or omit --publish")
            layer_name = os.environ.get("LAYER_NAME", "codechat-query-handler-dependencies")
            run([
                aws,
                "lambda",
                "publish-layer-version",
                "--layer-name",
                layer_name,
                "--compatible-runtimes",
                "python3.13",
                "--zip-file",
                f"fileb://{OUT_ZIP}",
            ])
            print("Published layer via AWS CLI.")
    finally:
        shutil.rmtree(tmpdir, ignore_errors=True)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Build CodeChat Lambda layers (cross-platform)")
    parser.add_argument("--python", default=sys.executable, help="Python interpreter to use (default: current Python)")
    parser.add_argument("--publish", action="store_true", help="Publish layer to AWS via AWS CLI")
    args = parser.parse_args(argv)

    py = Path(args.python)
    build_layer(py, args.publish)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
