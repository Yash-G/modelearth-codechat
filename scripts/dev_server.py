#!/usr/bin/env python3
"""Simple local dev server that reuses the deployed Lambda handlers.

Exposes two routes matching the AWS API Gateway configuration:

    - POST /query         -> src.lambdas.query_handler.index.lambda_handler
    - GET  /repositories  -> src.lambdas.get_repositories.index.lambda_handler

This lets you exercise the backend locally without provisioning AWS resources.
The server relies on Flask (already listed in requirements.txt).

Usage examples:

    # Run on default port (8080) and load .env if present
    python scripts/dev_server.py

    # Force mock responses by clearing API keys
    python scripts/dev_server.py --mock

    # Bind to a different host/port and skip loading .env
    python scripts/dev_server.py --host 0.0.0.0 --port 3000 --no-dotenv
"""

from __future__ import annotations

import argparse
import json
import logging
import os
import sys
from pathlib import Path
from typing import Any, Callable, Dict

from flask import Flask, Response, jsonify, request
from flask_cors import CORS

try:  # Optional dependency; skip silently if missing
    from dotenv import load_dotenv
except ImportError:  # pragma: no cover - python-dotenv is optional
    load_dotenv = None  # type: ignore[assignment]


REPO_ROOT = Path(__file__).resolve().parents[1]
QUERY_HANDLER_DIR = REPO_ROOT / "src" / "lambdas" / "query_handler"

for path in (QUERY_HANDLER_DIR, REPO_ROOT):
    if str(path) not in sys.path:
        sys.path.insert(0, str(path))


from src.lambdas.get_repositories.index import (  # noqa: E402
    lambda_handler as repositories_handler,
)
from src.lambdas.query_handler.index import (  # noqa: E402
    lambda_handler as query_handler,
)


LOGGER = logging.getLogger("dev_server")


def _configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="[%(levelname)s] %(message)s",
    )


def _load_dotenv_if_available(use_dotenv: bool) -> None:
    if not use_dotenv:
        LOGGER.info("Skipping .env loading")
        return
    if load_dotenv is None:
        LOGGER.info("python-dotenv not installed; skipping .env loading")
        return
    env_path = REPO_ROOT / ".env"
    if env_path.exists():
        LOGGER.info("Loading environment variables from %s", env_path)
        load_dotenv(env_path, override=False)
    else:
        LOGGER.info("No .env file found at %s", env_path)


def _apply_mock_mode(mock: bool) -> None:
    if not mock:
        return
    LOGGER.info("Mock mode enabled: clearing OpenAI/Pinecone keys to trigger fallback responses")
    for key in ("OPENAI_API_KEY", "PINECONE_API_KEY"):
        os.environ.pop(key, None)
    os.environ.setdefault("DEVSERVER_MOCK_MODE", "1")


def _call_lambda(handler: Callable[[Dict[str, Any], Any], Dict[str, Any]], event: Dict[str, Any]) -> Dict[str, Any]:
    try:
        return handler(event, None)
    except Exception as exc:  # pragma: no cover - defensive logging
        LOGGER.exception("Lambda handler raised an exception")
        return {
            "statusCode": 500,
            "headers": {"Content-Type": "application/json"},
            "body": json.dumps({"error": f"Lambda error: {exc}"}),
        }


def _flask_response(lambda_response: Dict[str, Any]) -> Response:
    status = int(lambda_response.get("statusCode", 200))
    headers = lambda_response.get("headers") or {}
    body = lambda_response.get("body", "")
    if not isinstance(body, (str, bytes)):
        body = json.dumps(body)
    return Response(response=body, status=status, headers=headers)


def create_app(mock: bool = False) -> Flask:
    app = Flask(__name__)
    CORS(app)

    @app.route("/health", methods=["GET"])
    def health() -> Response:
        return jsonify({"status": "ok", "mock": mock})

    @app.route("/repositories", methods=["GET", "OPTIONS"])
    def repositories() -> Response:
        event = {
            "httpMethod": request.method,
            "headers": dict(request.headers),
            "queryStringParameters": request.args.to_dict(flat=True),
        }
        lambda_response = _call_lambda(repositories_handler, event)
        return _flask_response(lambda_response)

    @app.route("/query", methods=["POST", "OPTIONS"])
    def query() -> Response:
        if request.method == "OPTIONS":
            event_body: Any = None
        else:
            event_body = request.get_data(as_text=True)
        event = {
            "httpMethod": request.method,
            "headers": dict(request.headers),
            "body": event_body,
        }
        lambda_response = _call_lambda(query_handler, event)
        return _flask_response(lambda_response)

    return app


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the CodeChat backend locally")
    parser.add_argument("--host", default="127.0.0.1", help="Host interface to bind (default: 127.0.0.1)")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind (default: 8080)")
    parser.add_argument("--mock", action="store_true", help="Force mock responses by clearing API keys")
    parser.add_argument("--no-dotenv", action="store_true", help="Skip loading .env from the repo root")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    _configure_logging()
    args = parse_args(argv)

    _load_dotenv_if_available(use_dotenv=not args.no_dotenv)

    _apply_mock_mode(args.mock)

    app = create_app(mock=args.mock)
    LOGGER.info("Starting dev server on http://%s:%d (mock=%s)", args.host, args.port, args.mock)
    app.run(host=args.host, port=args.port, debug=False)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
