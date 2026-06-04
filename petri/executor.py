import subprocess
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


def run(sandbox: Sandbox, filename: str) -> str:
    image = IMAGES[sandbox.language]
    runner = RUNNERS[sandbox.language]

    result = subprocess.run(
        [
            "docker",
            "run",
            "--rm",
            "-v",
            f"{sandbox.workspace_path}:/sandbox",
            image,
            "sh",
            "-c",
            f"{runner} /sandbox/{filename} 2>&1",
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=30,
    )

    return result.stdout
