#!/usr/bin/env python3
"""Set up a virtual environment and serve the CodeChat UI locally.

Steps performed:
  1. Create a Python virtual environment in ./venv if it does not exist.
  2. Install requirements.txt into that environment.
  3. Launch a simple HTTP server (python -m http.server) pointed at the chat UI.

This replaces scripts/run_local.sh and is intended to be cross-platform.
"""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parent.parent
VENV_DIR = REPO_ROOT / "venv"


def venv_paths() -> tuple[Path, Path]:
    if sys.platform.startswith("win"):
        python_path = VENV_DIR / "Scripts" / "python.exe"
        pip_path = VENV_DIR / "Scripts" / "pip.exe"
    else:
        python_path = VENV_DIR / "bin" / "python"
        pip_path = VENV_DIR / "bin" / "pip"
    return python_path, pip_path


def ensure_virtualenv() -> None:
    if VENV_DIR.exists():
        return
    print(f"[setup] creating virtualenv at {VENV_DIR}")
    subprocess.run([sys.executable, "-m", "venv", str(VENV_DIR)], check=True)


def install_dependencies() -> None:
    python_path, pip_path = venv_paths()
    if not pip_path.exists():
        raise RuntimeError("pip was not found inside the virtual environment")

    requirements = REPO_ROOT / "requirements.txt"
    if not requirements.exists():
        print("[warn] requirements.txt not found; skipping dependency install")
        return

    print("[setup] upgrading pip and installing requirements")
    subprocess.run([str(pip_path), "install", "--upgrade", "pip"], check=True)
    subprocess.run([str(pip_path), "install", "-r", str(requirements)], check=True)


def serve_ui(port: int, directory: Path) -> None:
    python_path, _ = venv_paths()
    if not python_path.exists():
        raise RuntimeError("virtual environment python binary not found")

    print(f"[serve] starting http.server on port {port} serving {directory}")
    print("       Press Ctrl+C to stop.")
    subprocess.run([str(python_path), "-m", "http.server", str(port), "--directory", str(directory)], check=True)


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CodeChat UI locally")
    parser.add_argument("--port", type=int, default=8887, help="Port for the HTTP server (default: 8887)")
    parser.add_argument(
        "--directory",
        default=str(REPO_ROOT / "chat"),
        help="Directory to serve (default: chat/)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    ensure_virtualenv()
    install_dependencies()
    serve_ui(args.port, Path(args.directory))

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

