import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from petri.config import WORKSPACE_ROOT
from petri.sandbox import Sandbox, SandboxStatus

DB_PATH = WORKSPACE_ROOT / "registry.db"

CREATE_TABLE = """
CREATE TABLE IF NOT EXISTS sandboxes (
    id TEXT PRIMARY KEY,
    language TEXT NOT NULL,
    container_id TEXT,
    workspace_path TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL
)
"""


class SandboxNotFound(Exception):
    pass


class Registry:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(CREATE_TABLE)
        self._conn.commit()

    def add(self, sandbox: Sandbox) -> None:
        self._conn.execute(
            "INSERT INTO sandboxes VALUES (?, ?, ?, ?, ?, ?)",
            (
                sandbox.id,
                sandbox.language,
                sandbox.container_id,
                str(sandbox.workspace_path) if sandbox.workspace_path else None,
                sandbox.status.value,
                sandbox.created_at.isoformat(),
            ),
        )
        self._conn.commit()

    def get(self, sandbox_id: str) -> Sandbox:
        row = self._conn.execute(
            "SELECT * FROM sandboxes WHERE id = ?", (sandbox_id,)
        ).fetchone()
        if row is None:
            raise SandboxNotFound(sandbox_id)
        return self._row_to_sandbox(row)

    def remove(self, sandbox_id: str) -> None:
        if self._conn.execute(
            "SELECT id FROM sandboxes WHERE id = ?", (sandbox_id,)
        ).fetchone() is None:
            raise SandboxNotFound(sandbox_id)
        self._conn.execute("DELETE FROM sandboxes WHERE id = ?", (sandbox_id,))
        self._conn.commit()

    def _row_to_sandbox(self, row: tuple) -> Sandbox:  # type: ignore[type-arg]
        return Sandbox(
            id=row[0],
            language=row[1],
            container_id=row[2],
            workspace_path=Path(row[3]) if row[3] else None,
            status=SandboxStatus(row[4]),
            created_at=datetime.fromisoformat(row[5]),
        )
