from pathlib import Path
import runpy


if __name__ == "__main__":
    frontend_server = Path(__file__).resolve().parent / "frontend" / "server.py"
    runpy.run_path(str(frontend_server), run_name="__main__")
