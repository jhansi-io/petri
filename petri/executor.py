import subprocess
from petri.sandbox import Sandbox

IMAGES: dict[str, str] = {
    "python": "python:3.12-slim",
    "node": "node:20-slim",
    "go": "golang:1.22",
    "java": "amazoncorretto:21",
}

RUNNERS: dict[str, str] = {
    "python": "python",
    "node": "node",
    "go": "go run",
    "java": "java",
}

EXTENSIONS: dict[str, str] = {
    "python": ".py",
    "node": ".js",
    "go": ".go",
    "java": ".java",
}

def build_install_command(language: str, filename: str) -> str:
    runner = RUNNERS[language]
    if language == "python":
        return (
            "if [ -f /sandbox/pyproject.toml ]; then "
            "pip install --target /sandbox/deps -q /sandbox; "
            "elif [ -f /sandbox/requirements.txt ]; then "
            "pip install --target /sandbox/deps -q -r /sandbox/requirements.txt; "
            "else "
            "pip install pipreqs -q && pipreqs --print /sandbox | pip install --target /sandbox/deps -q -r /dev/stdin; "
            "fi && "
            f"PYTHONPATH=/sandbox/deps python /sandbox/{filename} 2>&1"
        )
    if language == "go":
        return (
            "if [ -f /sandbox/go.mod ]; then "
            "cd /sandbox && go mod download; "
            "else "
            "cd /sandbox && go mod init sandbox && go mod tidy; "
            "fi && "
            f"go run /sandbox/{filename} 2>&1"
        )

    if language == "node":
        return (
            "if [ -f /sandbox/package.json ]; then "
            "cd /sandbox && npm install -q; "
            "fi && "
            f"cd /sandbox && node /sandbox/{filename} 2>&1"
        )

    if language == "java":
        classname = filename.replace(".java", "")
        return (
            "if [ -f /sandbox/pom.xml ]; then "
            "cd /sandbox && mvn dependency:resolve -q && mvn compile -q && "
            f"java -cp /sandbox/target/classes {classname} 2>&1; "
            "elif [ -f /sandbox/build.gradle ]; then "
            "cd /sandbox && gradle dependencies -q && gradle compileJava -q && "
            f"java -cp /sandbox/build/classes/java/main {classname} 2>&1; "
            "else "
            f"cd /sandbox && javac {filename} && java {classname} 2>&1; "
            "fi"
        )
    return f"{runner} /sandbox/{filename} 2>&1"

def run(sandbox: Sandbox, filename: str) -> str:
    image = IMAGES[sandbox.language]

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
            build_install_command(sandbox.language, filename),
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True,
        timeout=30,
    )

    return result.stdout
