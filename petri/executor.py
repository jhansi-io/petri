import subprocess
import tempfile
from pathlib import Path

from petri.sandbox import Sandbox

IMAGES: dict[str, str] = {
    "python": "python:3.12-slim",
    "node": "node:20-slim",
    "go": "golang:1.22",
}

RUNNERS: dict[str, str] = {
    "python": "python",
    "node": "node",
    "go": "go run",
}

EXTENSIONS: dict[str, str] = {
    "python": ".py",
    "node": ".js",
    "go": ".go",
}

def run(sandbox: Sandbox, code: str) -> str:
    image = IMAGES[sandbox.language]
    runner = RUNNERS[sandbox.language]
    ext = EXTENSIONS[sandbox.language]

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as f:
        f.write(code.encode())
        tmp_path = Path(f.name)

    result = subprocess.run([
        "docker", "run", "--rm",
        "-v", f"{tmp_path}:/code{ext}",
        image,
        "sh", "-c", f"{runner} /code{ext} 2>&1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=30,
    )

    tmp_path.unlink(missing_ok=True)
    return result.stdout
