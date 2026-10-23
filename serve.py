#!/usr/bin/env python3
"""Local preview server for dist/.

Open the site through this server, not by double-clicking dist/index.html:
links and CSS use root paths (/assets/…, /menu/), which file:// resolves to
the root of your disk.

    python3 serve.py          # http://localhost:4174
"""
import os, sys, http.server, socketserver, socket

PORT = int(sys.argv[1]) if len(sys.argv) > 1 else 4174
ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "dist")

class H(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *a, **kw):
        super().__init__(*a, directory=ROOT, **kw)
    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()
    def send_error(self, code, message=None, explain=None):
        f404 = os.path.join(ROOT, "404.html")       # behave like GitHub Pages
        if code == 404 and os.path.isfile(f404):
            body = open(f404, "rb").read()
            self.send_response(404); self.send_header("Content-Type", "text/html; charset=utf-8")
            self.send_header("Content-Length", str(len(body))); self.end_headers(); self.wfile.write(body); return
        super().send_error(code, message, explain)
    def log_message(self, fmt, *a):
        sys.stderr.write("  %s\n" % (fmt % a))

def lan_ip():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80)); return s.getsockname()[0]
    except Exception:
        return None
    finally:
        s.close()

socketserver.TCPServer.allow_reuse_address = True
with socketserver.TCPServer(("0.0.0.0", PORT), H) as httpd:
    ip = lan_ip()
    print("=" * 52)
    print(f"  This computer:  http://localhost:{PORT}/")
    if ip: print(f"  Phone (same Wi-Fi): http://{ip}:{PORT}/")
    print(f"  Pending review: http://localhost:{PORT}/_pending/")
    print("=" * 52 + "\n  Stop: Control + C\n")
    httpd.serve_forever()
