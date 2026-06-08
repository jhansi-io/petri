import subprocess
import time

from petri.sandbox import Sandbox

IMAGES: dict[str, str] = {
    "python": "python:3.12-slim",
    "node": "node:20-slim",
    "go": "golang:1.22",
    "java": "maven:3.9-amazoncorretto-21",
}

TEST_RUNNERS: dict[str, str] = {
    "python": "PYTHONPATH=/sandbox/deps python -m pytest /sandbox/tests -v",
    "node": "cd /sandbox && npx jest",
    "go": "cd /sandbox && go test ./...",
    "java": "cd /sandbox && mvn test",
}


def build_deps_command(language: str) -> str:
    if language == "python":
        return (
            "if [ -f /sandbox/pyproject.toml ]; then "
            "pip install --target /sandbox/deps -q /sandbox; "
            "elif [ -f /sandbox/requirements.txt ]; then "
            "pip install --target /sandbox/deps -q -r /sandbox/requirements.txt; "
            "else "
            "pip install pipreqs -q && pipreqs --print /sandbox | "
            "pip install --target /sandbox/deps -q -r /dev/stdin; "
            "fi"
        )
    if language == "node":
        return "if [ -f /sandbox/package.json ]; then cd /sandbox && npm install -q; fi"
    if language == "go":
        return (
            "if [ -f /sandbox/go.mod ]; then "
            "cd /sandbox && go mod download; "
            "else "
            "cd /sandbox && go mod init sandbox && go mod tidy; "
            "fi"
        )
    if language == "java":
        return (
            "if [ -f /sandbox/pom.xml ]; then "
            "cd /sandbox && mvn dependency:resolve -q; "
            "elif [ -f /sandbox/build.gradle ]; then "
            "cd /sandbox && gradle dependencies -q; "
            "fi"
        )
    return ""


def build_run_command(language: str, command: str) -> str:
    if language == "python":
        return f"PYTHONPATH=/sandbox/deps {command} 2>&1"
    return f"{command} 2>&1"


def build_install_command(language: str, command: str) -> str:
    deps = build_deps_command(language)
    run_cmd = build_run_command(language, command)
    if deps:
        return f"{deps} && {run_cmd}"
    return run_cmd


def run(sandbox: Sandbox, command: str, test: bool = False) -> str:
    image = IMAGES[sandbox.language]
    install_cmd = build_install_command(sandbox.language, command)

    if not test:
        result = subprocess.run(
            [
                "docker",
                "run",
                "--rm",
                "-w",
                "/sandbox",
                "-v",
                f"{sandbox.workspace_path}:/sandbox",
                image,
                "sh",
                "-c",
                install_cmd,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=30,
        )

        return result.stdout

    if test:
        # Step 1 — install deps (blocking)
        deps_cmd = build_deps_command(sandbox.language)
        if deps_cmd:
            subprocess.run(
                [
                    "docker",
                    "run",
                    "--rm",
                    "-w",
                    "/sandbox",
                    "-v",
                    f"{sandbox.workspace_path}:/sandbox",
                    image,
                    "sh",
                    "-c",
                    deps_cmd,
                ],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                timeout=120,
            )

        # Step 2 — start app (detached)
        run_cmd = build_run_command(sandbox.language, command)
        container = subprocess.run(
            [
                "docker",
                "run",
                "-d",
                "-w",
                "/sandbox",
                "-v",
                f"{sandbox.workspace_path}:/sandbox",
                image,
                "sh",
                "-c",
                run_cmd,
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        sandbox.container_id = container.stdout.strip()

        # Step 3 — wait for app to start
        time.sleep(2)

        # Step 4 — run tests
        test_result = subprocess.run(
            [
                "docker",
                "exec",
                sandbox.container_id,
                "sh",
                "-c",
                TEST_RUNNERS[sandbox.language],
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=60,
        )

        subprocess.run(
            ["docker", "stop", sandbox.container_id],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )

        return test_result.stdout
