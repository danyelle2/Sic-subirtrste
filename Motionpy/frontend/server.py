import csv
import json
import socketserver
from http.server import SimpleHTTPRequestHandler
from pathlib import Path
from urllib.parse import quote, unquote, urlsplit


PORT = 8000
FRONTEND_DIR = Path(__file__).resolve().parent
PROJECT_DIR = FRONTEND_DIR.parent
DATASET_DIR = PROJECT_DIR / "backend" / "Treinamento_llm_motionpy" / "videos UFPE (V-LIBRASIL)"
ANNOTATIONS_FILE = DATASET_DIR / "annotations.csv"
VIDEO_DIR = DATASET_DIR / "data"
MODEL_DIR = PROJECT_DIR / "backend" / "modelo_js"
MODEL_FILES = {"model.json", "metadata.json", "weights.bin"}


class MotionPyRequestHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FRONTEND_DIR), **kwargs)

    def do_GET(self):
        request_path = unquote(urlsplit(self.path).path)

        if request_path == "/api/signs":
            self.serve_sign_catalog()
            return
        if request_path.startswith("/training-videos/"):
            self.serve_training_video(request_path[len("/training-videos/"):])
            return
        if request_path.startswith("/modelo_js/"):
            self.serve_model_file(request_path[len("/modelo_js/"):])
            return

        super().do_GET()

    def end_headers(self):
        self.send_header("Cache-Control", "no-store")
        super().end_headers()

    def send_json(self, status_code, payload):
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status_code)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def serve_sign_catalog(self):
        try:
            available_videos = {
                path.name for path in VIDEO_DIR.iterdir() if path.is_file()
            }
            signs = {}
            with ANNOTATIONS_FILE.open("r", encoding="utf-8-sig", newline="") as annotations:
                for row in csv.DictReader(annotations):
                    name = (row.get("class") or "").strip()
                    if not name:
                        continue

                    sign = signs.setdefault(name, set())
                    video_name = (row.get("video_name") or "").strip()
                    if video_name in available_videos:
                        sign.add(video_name)

            catalog = [
                {
                    "name": name,
                    "videos": [
                        {
                            "filename": filename,
                            "url": "/training-videos/" + quote(filename, safe=""),
                        }
                        for filename in sorted(filenames)
                    ],
                }
                for name, filenames in sorted(signs.items(), key=lambda item: item[0].casefold())
            ]
        except OSError as error:
            self.log_error("Não foi possível ler o catálogo V-LIBRASIL: %s", error)
            self.send_json(500, {"error": "Não foi possível ler o catálogo local de sinais."})
            return

        self.send_json(200, {"signs": catalog})

    def serve_training_video(self, filename):
        if (not filename or filename in {".", ".."} or "\x00" in filename or
                "/" in filename or "\\" in filename):
            self.send_error(404, "Vídeo não encontrado")
            return

        video_path = (VIDEO_DIR / filename).resolve()
        if video_path.parent != VIDEO_DIR.resolve() or not video_path.is_file():
            self.send_error(404, "Vídeo não encontrado")
            return

        self.send_file(video_path, "video/mp4", supports_ranges=True)

    def serve_model_file(self, filename):
        if filename not in MODEL_FILES:
            self.send_error(404, "Arquivo do modelo não encontrado")
            return

        model_path = MODEL_DIR / filename
        if not model_path.is_file():
            self.send_error(404, "Arquivo do modelo não encontrado")
            return

        content_type = "application/json; charset=utf-8" if filename.endswith(".json") else "application/octet-stream"
        self.send_file(model_path, content_type)

    def send_file(self, path, content_type, supports_ranges=False):
        file_size = path.stat().st_size
        start = 0
        end = file_size - 1
        status_code = 200

        range_header = self.headers.get("Range") if supports_ranges else None
        if range_header:
            try:
                unit, range_value = range_header.split("=", 1)
                if unit != "bytes" or "," in range_value:
                    raise ValueError("Unsupported byte range")

                first_byte, last_byte = range_value.split("-", 1)
                if first_byte:
                    start = int(first_byte)
                    end = min(int(last_byte), end) if last_byte else end
                else:
                    suffix_length = int(last_byte)
                    start = max(file_size - suffix_length, 0)

                if start < 0 or start >= file_size or end < start or end >= file_size:
                    raise ValueError("Byte range outside file")
            except ValueError:
                self.send_response(416)
                self.send_header("Content-Range", f"bytes */{file_size}")
                self.end_headers()
                return

            status_code = 206

        content_length = end - start + 1
        self.send_response(status_code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(content_length))
        if supports_ranges:
            self.send_header("Accept-Ranges", "bytes")
        if status_code == 206:
            self.send_header("Content-Range", f"bytes {start}-{end}/{file_size}")
        self.end_headers()
        with path.open("rb") as file_stream:
            file_stream.seek(start)
            remaining = content_length
            while remaining:
                chunk = file_stream.read(min(65536, remaining))
                if not chunk:
                    break
                self.wfile.write(chunk)
                remaining -= len(chunk)


class LocalThreadingTCPServer(socketserver.ThreadingTCPServer):
    allow_reuse_address = True


if __name__ == "__main__":
    with LocalThreadingTCPServer(("127.0.0.1", PORT), MotionPyRequestHandler) as server:
        print(f"Servidor local MotionPy em http://127.0.0.1:{PORT}")
        server.serve_forever()
