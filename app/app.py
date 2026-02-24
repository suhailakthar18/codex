import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from app.api.routes import handle_api_request
from app.data.repository import create_repository
from app.services.admin_catalog_service import AdminCatalogService
from app.services.catalog_service import CatalogService

BASE_DIR = Path(__file__).resolve().parent


def create_services(db_path: str = "data/store.db"):
    repository = create_repository(db_path)
    return CatalogService(repository), AdminCatalogService(repository)


def create_handler(service, admin_service, admin_token):
    class StoreHandler(BaseHTTPRequestHandler):
        def _send(self, status: int, headers: dict[str, str], body: bytes):
            self.send_response(status)
            for key, value in headers.items():
                self.send_header(key, value)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def _serve_file(self, file_path: Path, content_type: str):
            if not file_path.exists():
                self._send(404, {"Content-Type": "text/plain"}, b"Not found")
                return
            self._send(200, {"Content-Type": content_type}, file_path.read_bytes())

        def do_GET(self):
            if self.path == "/":
                return self._serve_file(BASE_DIR / "templates" / "index.html", "text/html; charset=utf-8")
            if self.path == "/admin":
                return self._serve_file(BASE_DIR / "templates" / "admin.html", "text/html; charset=utf-8")
            if self.path == "/static/styles.css":
                return self._serve_file(BASE_DIR / "static" / "styles.css", "text/css; charset=utf-8")
            if self.path == "/static/app.js":
                return self._serve_file(BASE_DIR / "static" / "app.js", "application/javascript; charset=utf-8")
            if self.path == "/static/admin.js":
                return self._serve_file(BASE_DIR / "static" / "admin.js", "application/javascript; charset=utf-8")
            if self.path.startswith("/api/"):
                status, headers, body = handle_api_request(
                    "GET", self.path, b"", service, admin_service, dict(self.headers), admin_token
                )
                return self._send(status, headers, body)
            self._send(404, {"Content-Type": "text/plain"}, b"Not found")

        def do_POST(self):
            length = int(self.headers.get("Content-Length", 0))
            body = self.rfile.read(length) if length else b""
            if self.path.startswith("/api/"):
                status, headers, body_bytes = handle_api_request(
                    "POST", self.path, body, service, admin_service, dict(self.headers), admin_token
                )
                return self._send(status, headers, body_bytes)
            self._send(404, {"Content-Type": "text/plain"}, b"Not found")

    return StoreHandler


def run(host="0.0.0.0", port=5000, db_path="data/store.db"):
    service, admin_service = create_services(db_path)
    admin_token = os.environ.get("ADMIN_TOKEN", "admin123")
    server = ThreadingHTTPServer((host, port), create_handler(service, admin_service, admin_token))
    print(f"Server running at http://{host}:{port}")
    print("Admin UI: /admin")
    server.serve_forever()


if __name__ == "__main__":
    run()
