from pathlib import Path


def evict_logs_if_needed(workspace_root: Path, max_mb: int) -> None:
    log_files = sorted(
        workspace_root.rglob("runs/*.log"),
        key=lambda f: f.stat().st_mtime,
    )
    max_bytes = max_mb * 1024 * 1024
    total = sum(f.stat().st_size for f in log_files)
    while total > max_bytes and log_files:
        oldest = log_files.pop(0)
        total -= oldest.stat().st_size
        oldest.unlink()
