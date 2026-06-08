from pathlib import Path

from petri.executor import run
from petri.sandbox import Sandbox


def test_python_hello_world(tmp_path: Path) -> None:
    script = tmp_path / "main.py"
    script.write_text("print('hello world!!')")
    sandbox = Sandbox(language="python", workspace_path=tmp_path)
    output = run(sandbox, "python main.py")
    assert output.strip() == "hello world!!"


def test_python_arithmetic(tmp_path: Path) -> None:
    script = tmp_path / "main.py"
    script.write_text("print(1+1)")
    sandbox = Sandbox(language="python", workspace_path=tmp_path)
    output = run(sandbox, "python main.py")
    assert output.strip() == "2"


def test_python_stderr_captured(tmp_path: Path) -> None:
    script = tmp_path / "main.py"
    script.write_text("import sys; sys.stderr.write('error')")
    sandbox = Sandbox(language="python", workspace_path=tmp_path)
    output = run(sandbox, "python main.py")
    assert "error" in output
