import json
import threading
from datetime import UTC, datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any

from craik.runtime.auth.sources import LocalCLICredentialSource


def test_local_cli_oauth_source_returns_anthropic_bearer_header(tmp_path: Path) -> None:
    credentials = tmp_path / "credentials.json"
    credentials.write_text(
        json.dumps(
            {
                "claudeAiOauth": {
                    "accessToken": "local-access-token",
                    "refreshToken": "local-refresh-token",
                    "expiresAt": (datetime.now(UTC) + timedelta(hours=1)).isoformat(),
                }
            }
        ),
        encoding="utf-8",
    )

    headers = LocalCLICredentialSource(credentials_path=credentials).headers_for("anthropic")

    assert headers == {
        "Authorization": "Bearer local-access-token",
        "anthropic-version": "2023-06-01",
    }


def test_local_cli_oauth_source_refreshes_expired_token(tmp_path: Path) -> None:
    credentials = tmp_path / "credentials.json"
    credentials.write_text(
        json.dumps(
            {
                "access_token": "expired-access-token",
                "refresh_token": "refresh-token",
                "expires_at": (datetime.now(UTC) - timedelta(minutes=5)).isoformat(),
            }
        ),
        encoding="utf-8",
    )
    seen_requests: list[dict[str, Any]] = []

    class RefreshHandler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            length = int(self.headers["Content-Length"])
            body = json.loads(self.rfile.read(length).decode("utf-8"))
            seen_requests.append(body)
            response = {
                "access_token": "refreshed-access-token",
                "refresh_token": "refreshed-refresh-token",
                "expires_in": 3600,
            }
            encoded = json.dumps(response).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(encoded)))
            self.end_headers()
            self.wfile.write(encoded)

        def log_message(self, format: str, *args: object) -> None:
            return

    server = HTTPServer(("127.0.0.1", 0), RefreshHandler)
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        source = LocalCLICredentialSource(
            credentials_path=credentials,
            refresh_endpoint=f"http://127.0.0.1:{server.server_port}/oauth/token",
            client_id="claude-local-cli",
        )

        headers = source.headers_for("anthropic")
    finally:
        server.shutdown()
        thread.join(timeout=5)

    persisted = json.loads(credentials.read_text(encoding="utf-8"))
    assert headers["Authorization"] == "Bearer refreshed-access-token"
    assert seen_requests == [
        {
            "client_id": "claude-local-cli",
            "grant_type": "refresh_token",
            "refresh_token": "refresh-token",
        }
    ]
    assert persisted["access_token"] == "refreshed-access-token"
    assert persisted["refresh_token"] == "refreshed-refresh-token"
    assert "expired-access-token" not in str(source.status())
