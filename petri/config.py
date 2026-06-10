import os
from pathlib import Path

WORKSPACE_ROOT: Path = Path(
    os.environ.get("PETRI_WORKSPACE_ROOT", "~/.petri/workspaces")
).expanduser()

TTL_SECONDS: int = int(os.environ.get("PETRI_SANDBOX_TTL_SECONDS", "3600"))
