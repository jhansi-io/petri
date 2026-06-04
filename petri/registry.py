from petri.sandbox import Sandbox


class SandboxNotFound(Exception):
    pass


class Registry:
    def __init__(self) -> None:
        self._sandboxes: dict[str, Sandbox] = {}

    def add(self, sandbox: Sandbox) -> None:
        self._sandboxes[sandbox.id] = sandbox

    def get(self, sandbox_id: str) -> Sandbox:
        if sandbox_id not in self._sandboxes:
            raise SandboxNotFound(sandbox_id)

        return self._sandboxes[sandbox_id]

    def remove(self, sandbox_id: str) -> None:
        if sandbox_id not in self._sandboxes:
            raise SandboxNotFound(sandbox_id)
        del self._sandboxes[sandbox_id]
