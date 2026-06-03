import pytest

from petri.registry import Registry, SandboxNotFound
from petri.sandbox import Sandbox

def test_add_and_get_sandbox() -> None:
    registry = Registry()
    sandbox = Sandbox()
    registry.add(sandbox)
    assert registry.get(sandbox.id) == sandbox

def test_get_unknown_sandbox_raises() -> None:
    registry = Registry()
    with pytest.raises(SandboxNotFound):
        registry.get("sb_unknown")

def test_remove_sandbox() -> None:
    registry = Registry()
    sandbox = Sandbox()
    registry.add(sandbox)
    assert registry.get(sandbox.id) == sandbox
    registry.remove(sandbox.id)
    with pytest.raises(SandboxNotFound):
        registry.get(sandbox.id)

def test_remove_unknown_sandbox_raises() -> None:
    registry = Registry()
    with pytest.raises(SandboxNotFound):
        registry.remove("sb_unknown")
