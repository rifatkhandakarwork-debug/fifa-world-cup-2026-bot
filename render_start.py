from __future__ import annotations

import os
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

from bot import main as run_bot


class HealthHandler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        self.send_response(200)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.end_headers()
        self.wfile.write(b"FIFA World Cup 2026 Bot is running.")

    def log_message(self, format: str, *args: object) -> None:
        return


def start_health_server() -> None:
    port = int(os.getenv("PORT", "10000"))
    server = ThreadingHTTPServer(("0.0.0.0", port), HealthHandler)
    server.serve_forever()


if __name__ == "__main__":
    threading.Thread(target=start_health_server, daemon=True).start()
    run_bot()
