from pathlib import Path

from petri.sandbox import Sandbox, SandboxStatus


def test_sandbox_has_unique_ids() -> None:
    s1 = Sandbox()
    s2 = Sandbox()
    assert s1.id != s2.id


def test_sandbox_id_has_prefix() -> None:
    s = Sandbox()
    assert s.id.startswith("sb_")


def test_sandbox_default_language() -> None:
    s = Sandbox()
    assert s.language == "python"


def test_sandbox_default_status() -> None:
    s = Sandbox()
    assert s.status == SandboxStatus.CREATED


def test_sandbox_container_id_initially_none() -> None:
    s = Sandbox()
    assert s.container_id is None


def test_sandbox_workspace_path() -> None:
    path = Path("/tmp/test_workspace")
    sandbox = Sandbox(workspace_path=path)
    assert sandbox.workspace_path == path
