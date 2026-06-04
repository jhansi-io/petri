import os
from pathlib import Path

WORKSPACE_ROOT: Path = Path(
    os.environ.get("PETRI_WORKSPACE_ROOT", "~/.petri/workspaces")
).expanduser()
