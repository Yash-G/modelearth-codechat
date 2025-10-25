#!/usr/bin/env python3
"""Download and install Terraform in a cross-platform way.

By default the binary is placed in ./bin so that no administrator privileges
are required. After running the script, add ./bin to your PATH or call
Terraform with that absolute path.

Usage examples:
  python scripts/setup_terraform.py
  python scripts/setup_terraform.py --version 1.9.5 --install-dir C:/tools
"""

from __future__ import annotations

import argparse
import os
import platform
import shutil
import sys
import tempfile
import zipfile
from pathlib import Path
from urllib.request import urlopen


DEFAULT_VERSION = "1.2.0"


def detect_os_arch() -> tuple[str, str]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system.startswith("darwin"):
        os_name = "darwin"
    elif system.startswith("linux"):
        os_name = "linux"
    elif system.startswith("windows"):
        os_name = "windows"
    else:
        raise RuntimeError(f"Unsupported operating system: {system}")

    if machine in {"x86_64", "amd64"}:
        arch = "amd64"
    elif machine in {"arm64", "aarch64"}:
        arch = "arm64"
    else:
        raise RuntimeError(f"Unsupported architecture: {machine}")

    return os_name, arch


def download(url: str, destination: Path) -> None:
    print(f"[download] {url}")
    with urlopen(url) as response, open(destination, "wb") as outfile:  # type: ignore[arg-type]
        shutil.copyfileobj(response, outfile)


def extract_zip(zip_path: Path, target: Path) -> Path:
    print(f"[extract] {zip_path} -> {target}")
    with zipfile.ZipFile(zip_path) as archive:
        archive.extractall(target)
    for name in ("terraform", "terraform.exe"):
        candidate = target / name
        if candidate.exists():
            return candidate
    raise RuntimeError("Downloaded archive did not contain terraform binary")


def install_terraform(version: str, install_dir: Path) -> Path:
    os_name, arch = detect_os_arch()
    zip_name = f"terraform_{version}_{os_name}_{arch}.zip"
    url = f"https://releases.hashicorp.com/terraform/{version}/{zip_name}"

    install_dir.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        tmpdir = Path(tmp)
        zip_path = tmpdir / zip_name
        download(url, zip_path)
        extracted = extract_zip(zip_path, tmpdir)

        destination = install_dir / extracted.name
        if destination.exists():
            destination.unlink()
        shutil.move(str(extracted), destination)
        destination.chmod(0o755)
        return destination


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    default_install = Path.cwd() / "bin"
    parser = argparse.ArgumentParser(description="Install Terraform locally")
    parser.add_argument("--version", default=DEFAULT_VERSION, help="Terraform version to install")
    parser.add_argument(
        "--install-dir",
        type=Path,
        default=default_install,
        help="Directory to place terraform (default: ./bin)",
    )
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)

    try:
        binary = install_terraform(version=args.version, install_dir=args.install_dir)
    except Exception as exc:  # noqa: BLE001 - present message to caller
        print(f"ERROR: {exc}")
        return 1

    print(f"Terraform {args.version} installed at {binary}")
    if args.install_dir not in map(Path, os.environ.get("PATH", "").split(os.pathsep)):
        print(f"Add {args.install_dir} to your PATH to use terraform globally.")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())

