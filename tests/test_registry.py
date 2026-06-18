from datetime import datetime, timezone
from pathlib import Path

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


def test_list_active_excludes_deleted(tmp_path) -> None:
    registry = Registry(db_path=tmp_path / "test.db")
    live = Sandbox()
    dead = Sandbox()
    registry.add(live)
    registry.add(dead)
    registry.remove(dead.id)

    active = registry.list_active()

    assert [s.id for s in active] == [live.id]


def test_list_all_includes_deleted(tmp_path: Path) -> None:
    registry = Registry(db_path=tmp_path / "test.db")
    a, b, c = Sandbox(), Sandbox(), Sandbox()
    for s in (a, b, c):
        registry.add(s)
    registry.remove(b.id)

    assert len(registry.list_all()) == 3


def test_list_runs_for_sandbox(tmp_path: Path) -> None:
    registry = Registry(db_path=tmp_path / "test.db")
    sandbox = Sandbox()
    registry.add(sandbox)
    now = datetime.now(timezone.utc)
    registry.add_run(
        run_id="run_1",
        sandbox_id=sandbox.id,
        started_at=now,
        completed_at=now,
        duration_ms=42,
        exit_code=0,
        error=None,
        output=None,
    )

    runs = registry.list_runs(sandbox.id)

    assert len(runs) == 1
    assert runs[0]["id"] == "run_1"
    assert runs[0]["exit_code"] == 0
