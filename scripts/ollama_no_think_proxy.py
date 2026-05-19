#!/usr/bin/env python3
"""Thin streaming HTTP proxy: Hermes ⇄ Ollama with thinking disabled.

Why: Ollama 0.23.0's OpenAI-compat `/v1/chat/completions` streaming hangs
when the model (e.g. gemma4:31b) emits 'thinking' tokens before content.
Hermes's `_interruptible_streaming_api_call` waits for content forever.

Fix: inject `reasoning: {effort: "none"}` into every chat-completions request,
which Ollama translates to native `think: false` → model streams content
directly.

Usage:
  python3 scripts/ollama_no_think_proxy.py [LISTEN_PORT=11435] [UPSTREAM=http://localhost:11434]

Then point Hermes profile base_url at http://localhost:11435/v1.
"""

from __future__ import annotations

import json
import sys
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

try:
    import httpx
except ImportError:
    print("Missing httpx. Install: pip install httpx", file=sys.stderr)
    sys.exit(1)


LISTEN_PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 11435
UPSTREAM = sys.argv[2] if len(sys.argv) > 2 else "http://localhost:11434"

# Per-thread reused client for connection pooling
_client = httpx.Client(timeout=httpx.Timeout(600.0, connect=10.0))


def _strip_hop_by_hop(headers: dict) -> dict:
    drop = {
        "content-length", "transfer-encoding", "connection",
        "keep-alive", "proxy-authenticate", "proxy-authorization",
        "te", "trailers", "upgrade", "host",
    }
    return {k: v for k, v in headers.items() if k.lower() not in drop}


def _maybe_inject(path: str, body: bytes) -> bytes:
    """Inject reasoning.effort=none into chat-completions payloads."""
    if not path.endswith("/chat/completions"):
        return body
    try:
        payload = json.loads(body)
    except Exception:
        return body
    reasoning = payload.get("reasoning")
    if not isinstance(reasoning, dict):
        reasoning = {}
    reasoning.setdefault("effort", "none")
    payload["reasoning"] = reasoning
    return json.dumps(payload).encode("utf-8")


class Handler(BaseHTTPRequestHandler):
    # Silence default access logs (we'll log when injecting only)
    def log_message(self, fmt, *args):
        return

    def _proxy(self, method: str) -> None:
        length = int(self.headers.get("Content-Length", 0) or 0)
        raw_body = self.rfile.read(length) if length else b""
        body = _maybe_inject(self.path, raw_body) if raw_body else raw_body
        # debug
        injected = body != raw_body
        print(f"[proxy] {method} {self.path} body={len(raw_body)}B inject={injected}", flush=True)

        fwd_headers = _strip_hop_by_hop(dict(self.headers))
        upstream_url = UPSTREAM + self.path

        try:
            with _client.stream(
                method, upstream_url, content=body, headers=fwd_headers
            ) as resp:
                self.send_response(resp.status_code)
                out_headers = _strip_hop_by_hop(dict(resp.headers))
                for k, v in out_headers.items():
                    self.send_header(k, v)
                self.end_headers()
                try:
                    for chunk in resp.iter_raw():
                        if not chunk:
                            continue
                        self.wfile.write(chunk)
                        self.wfile.flush()
                except (BrokenPipeError, ConnectionResetError):
                    pass
        except Exception as e:
            try:
                self.send_response(502)
                self.send_header("Content-Type", "text/plain; charset=utf-8")
                self.end_headers()
                self.wfile.write(f"proxy upstream error: {e}".encode("utf-8"))
            except Exception:
                pass

    def do_GET(self):
        self._proxy("GET")

    def do_POST(self):
        self._proxy("POST")

    def do_PUT(self):
        self._proxy("PUT")

    def do_DELETE(self):
        self._proxy("DELETE")


def main() -> None:
    addr = ("127.0.0.1", LISTEN_PORT)
    print(f"▶︎ ollama-no-think-proxy listening on http://{addr[0]}:{addr[1]}")
    print(f"   upstream: {UPSTREAM}")
    print(f"   injecting reasoning.effort=none for /chat/completions")
    server = ThreadingHTTPServer(addr, Handler)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nstopping…")
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
