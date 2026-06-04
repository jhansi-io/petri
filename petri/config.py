from pathlib import Path
import os

WORKSPACE_ROOT: Path = Path(
    os.environ.get("PETRI_WORKSPACE_ROOT", "~/.petri/workspaces")
).expanduser()
