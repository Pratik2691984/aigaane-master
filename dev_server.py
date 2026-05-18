from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen
import os


API_ORIGIN = os.environ.get("AIGAANE_API_ORIGIN", "http://127.0.0.1:8000")
PORT = int(os.environ.get("AIGAANE_FRONTEND_PORT", "5500"))


class AigaaneDevHandler(SimpleHTTPRequestHandler):
    def end_cors_headers(self):
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")

    def do_OPTIONS(self):
        if self.path.startswith("/api/"):
            self.send_response(204)
            self.end_cors_headers()
            self.end_headers()
            return
        super().do_OPTIONS()

    def do_POST(self):
        if self.path.startswith("/api/"):
            self.proxy_api_request()
            return
        self.send_error(405, "Method Not Allowed")

    def proxy_api_request(self):
        content_length = int(self.headers.get("Content-Length", "0") or "0")
        body = self.rfile.read(content_length) if content_length else b""
        upstream = Request(
            f"{API_ORIGIN}{self.path}",
            data=body,
            method="POST",
            headers={"Content-Type": self.headers.get("Content-Type", "application/json")},
        )

        try:
            with urlopen(upstream, timeout=10) as response:
                payload = response.read()
                self.send_response(response.status)
                self.end_cors_headers()
                self.send_header("Content-Type", response.headers.get("Content-Type", "application/json"))
                self.send_header("Content-Length", str(len(payload)))
                self.end_headers()
                self.wfile.write(payload)
        except HTTPError as error:
            payload = error.read()
            self.send_response(error.code)
            self.end_cors_headers()
            self.send_header("Content-Type", error.headers.get("Content-Type", "application/json"))
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
        except URLError as error:
            payload = f'{{"detail":"API proxy failed: {error.reason}"}}'.encode("utf-8")
            self.send_response(502)
            self.end_cors_headers()
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)


if __name__ == "__main__":
    server = ThreadingHTTPServer(("0.0.0.0", PORT), AigaaneDevHandler)
    print(f"Frontend/proxy server: http://localhost:{PORT}")
    print(f"Proxying /api/* to {API_ORIGIN}")
    server.serve_forever()
