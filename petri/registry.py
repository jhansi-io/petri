import sqlite3
from datetime import datetime, timezone
from pathlib import Path

from petri.config import WORKSPACE_ROOT
from petri.sandbox import Sandbox, SandboxStatus

DB_PATH = WORKSPACE_ROOT / "registry.db"

CREATE_SANDBOXES_TABLE = """
CREATE TABLE IF NOT EXISTS sandboxes (
    id TEXT PRIMARY KEY,
    language TEXT NOT NULL,
    container_id TEXT,
    workspace_path TEXT,
    status TEXT NOT NULL,
    created_at TEXT NOT NULL,
    expires_at TEXT NOT NULL,
    deleted_at TEXT,
    agent TEXT,
    created_by TEXT NOT NULL DEFAULT 'unknown'
)
"""

CREATE_SANDBOXES_INDEX = """
CREATE INDEX IF NOT EXISTS idx_sandboxes_status_created_at 
ON sandboxes(status, created_at)
"""

CREATE_RUNS_TABLE = """
CREATE TABLE IF NOT EXISTS runs (
    id TEXT PRIMARY KEY,
    sandbox_id TEXT NOT NULL,
    started_at TEXT NOT NULL,
    completed_at TEXT,
    duration_ms INTEGER,
    exit_code INTEGER,
    error TEXT,
    output TEXT,
    FOREIGN KEY (sandbox_id) REFERENCES sandboxes(id)
)
"""


class SandboxNotFound(Exception):
    pass


class Registry:
    def __init__(self, db_path: Path = DB_PATH) -> None:
        db_path.parent.mkdir(parents=True, exist_ok=True)
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.execute(CREATE_SANDBOXES_TABLE)
        self._conn.execute(CREATE_SANDBOXES_INDEX)
        self._conn.execute(CREATE_RUNS_TABLE)
        self._conn.commit()

    def add(self, sandbox: Sandbox) -> None:
        self._conn.execute(
            "INSERT INTO sandboxes VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
            (
                sandbox.id,
                sandbox.language,
                sandbox.container_id,
                str(sandbox.workspace_path) if sandbox.workspace_path else None,
                sandbox.status.value,
                sandbox.created_at.isoformat(),
                sandbox.expires_at.isoformat(),
                None,
                sandbox.agent,
                sandbox.created_by,
            ),
        )
        self._conn.commit()

    def get(self, sandbox_id: str) -> Sandbox:
        row = self._conn.execute(
            "SELECT * FROM sandboxes WHERE id = ? AND deleted_at IS NULL",
            (sandbox_id,),
        ).fetchone()
        if row is None:
            raise SandboxNotFound(sandbox_id)
        return self._row_to_sandbox(row)

    def remove(self, sandbox_id: str) -> None:
        if (
            self._conn.execute(
                "SELECT id FROM sandboxes WHERE id = ?", (sandbox_id,)
            ).fetchone()
            is None
        ):
            raise SandboxNotFound(sandbox_id)
        now = datetime.now(timezone.utc).isoformat()
        self._conn.execute(
            "UPDATE sandboxes SET status = ?, deleted_at = ? WHERE id = ?",
            (SandboxStatus.DELETED.value, now, sandbox_id),
        )
        self._conn.commit()

    def _row_to_sandbox(self, row: tuple) -> Sandbox:  # type: ignore[type-arg]
        return Sandbox(
            id=row[0],
            language=row[1],
            container_id=row[2],
            workspace_path=Path(row[3]) if row[3] else None,
            status=SandboxStatus(row[4]),
            created_at=datetime.fromisoformat(row[5]),
            expires_at=datetime.fromisoformat(row[6]),
            agent=row[8],
            created_by=row[9],
        )

    def update_expires_at(self, sandbox_id: str, expires_at: datetime) -> None:
        self._conn.execute(
            "UPDATE sandboxes SET expires_at = ? WHERE id = ?",
            (expires_at.isoformat(), sandbox_id),
        )
        self._conn.commit()

    def list_expired(self) -> list[Sandbox]:
        now = datetime.now(timezone.utc).isoformat()
        rows = self._conn.execute(
            "SELECT * FROM sandboxes WHERE expires_at < ?", (now,)
        ).fetchall()
        return [self._row_to_sandbox(row) for row in rows]

    def list_active(self) -> list[Sandbox]:
        now = datetime.now(timezone.utc).isoformat()
        rows = self._conn.execute(
            "SELECT * FROM sandboxes "
            "WHERE deleted_at IS NULL AND expires_at > ? "
            "ORDER BY created_at DESC",
            (now,),
        ).fetchall()
        return [self._row_to_sandbox(row) for row in rows]

    def list_all(self, limit: int = 50, offset: int = 0) -> list[Sandbox]:
        rows = self._conn.execute(
            "SELECT * FROM sandboxes ORDER BY created_at DESC LIMIT ? OFFSET ?",
            (limit, offset),
        ).fetchall()
        return [self._row_to_sandbox(row) for row in rows]

    def add_run(
        self,
        run_id: str,
        sandbox_id: str,
        started_at: datetime,
        completed_at: datetime,
        duration_ms: int,
        exit_code: int,
        error: str | None,
        output: str | None,
    ) -> None:
        self._conn.execute(
            "INSERT INTO runs VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
            (
                run_id,
                sandbox_id,
                started_at.isoformat(),
                completed_at.isoformat(),
                duration_ms,
                exit_code,
                error,
                output,
            ),
        )
        self._conn.commit()

    def list_runs(self, sandbox_id: str) -> list[dict]:  # type: ignore[type-arg]
        rows = self._conn.execute(
            "SELECT id, started_at, completed_at, duration_ms, exit_code, error "
            "FROM runs WHERE sandbox_id = ? ORDER BY started_at DESC",
            (sandbox_id,),
        ).fetchall()
        return [
            {
                "id": row[0],
                "started_at": row[1],
                "completed_at": row[2],
                "duration_ms": row[3],
                "exit_code": row[4],
                "error": row[5],
            }
            for row in rows
        ]

    def get_metrics(self) -> dict:  # type: ignore[type-arg]
        active = self._conn.execute(
            "SELECT COUNT(*) FROM sandboxes WHERE deleted_at IS NULL"
        ).fetchone()[0]
        total = self._conn.execute("SELECT COUNT(*) FROM sandboxes").fetchone()[0]
        runs_total = self._conn.execute("SELECT COUNT(*) FROM runs").fetchone()[0]
        runs_failed = self._conn.execute(
            "SELECT COUNT(*) FROM runs WHERE exit_code != 0"
        ).fetchone()[0]
        avg_duration = self._conn.execute(
            "SELECT AVG(duration_ms) FROM runs WHERE duration_ms IS NOT NULL"
        ).fetchone()[0]
        by_agent = {}
        rows = self._conn.execute(
            "SELECT agent, COUNT(*), SUM(CASE WHEN exit_code != 0 THEN 1 ELSE 0 END) "
            "FROM runs JOIN sandboxes ON runs.sandbox_id = sandboxes.id "
            "WHERE sandboxes.agent IS NOT NULL "
            "GROUP BY sandboxes.agent"
        ).fetchall()
        for row in rows:
            agent, count, failed = row
            by_agent[agent] = {
                "runs": count,
                "success_rate": round(1 - (failed / count), 2) if count else 0,
            }
        return {
            "sandboxes_active": active,
            "sandboxes_total": total,
            "runs_total": runs_total,
            "runs_failed": runs_failed,
            "success_rate": round(1 - (runs_failed / runs_total), 2)
            if runs_total
            else 1.0,
            "avg_duration_ms": int(avg_duration) if avg_duration else 0,
            "by_agent": by_agent,
        }
