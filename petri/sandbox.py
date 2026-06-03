import secrets
from dataclasses import dataclass, field
from datetime import datetime, timezone
from enum import Enum


class SandboxStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    STOPPED = "stopped"
    ERROR = "error"


@dataclass
class Sandbox:
    # secrets.token_hex over uuid4 - signals security intent for exposed IDs
    id: str = field(default_factory=lambda: f"sb_{secrets.token_hex(16)}")
    language: str = "python"
    container_id: str | None = None
    status: SandboxStatus = SandboxStatus.CREATED
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
