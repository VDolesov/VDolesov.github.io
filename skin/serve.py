import functools
import io
import mimetypes
import os
import sys
from http import HTTPStatus
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

HERE = os.path.dirname(os.path.abspath(__file__))
APP = os.path.dirname(HERE)
ORIGIN = b"https://vdolesov.github.io"
TEXT = (".html", ".js", ".css", ".json", ".xml", ".txt", ".svg", ".webmanifest")

for kind, ext in (("image/webp", ".webp"), ("image/avif", ".avif"), ("font/woff2", ".woff2"), ("font/woff", ".woff"),
                  ("text/javascript", ".js"), ("application/manifest+json", ".webmanifest")):
    mimetypes.add_type(kind, ext)


class Handler(SimpleHTTPRequestHandler):
    def send_head(self):
        path = self.translate_path(self.path)
        if os.path.isdir(path):
            if not self.path.split("?", 1)[0].endswith("/"):
                return super().send_head()
            path = os.path.join(path, "index.html")
        status = HTTPStatus.OK
        if not os.path.isfile(path):
            path, status = os.path.join(APP, "404.html"), HTTPStatus.NOT_FOUND
        with open(path, "rb") as f:
            data = f.read()
        if path.endswith(TEXT):
            data = data.replace(ORIGIN, b"http://" + self.headers.get("Host", "localhost").encode("latin-1"))
        self.send_response(status)
        self.send_header("Content-Type", mimetypes.guess_type(path)[0] or "application/octet-stream")
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()
        return io.BytesIO(data)


def main(port="4183"):
    server = ThreadingHTTPServer(("127.0.0.1", int(port)), functools.partial(Handler, directory=APP))
    print(f"http://localhost:{port}/", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    sys.exit(main(*sys.argv[1:]))
