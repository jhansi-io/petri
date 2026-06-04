from petri.executor import run
from petri.sandbox import Sandbox


def test_python_hello_world() -> None:
    sandbox = Sandbox(language="python")
    output = run(sandbox, "print('hello world!!')")
    assert output.strip() == "hello world!!"


def test_python_arithmetic() -> None:
    sandbox = Sandbox(language="python")
    output = run(sandbox, "print(1+1)")
    assert output.strip() == "2"


def test_python_stderr_captured() -> None:
    sandbox = Sandbox(language="python")
    output = run(sandbox, "import sys; sys.stderr.write('error')")
    assert "error" in output
