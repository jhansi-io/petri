import pytest
from fastapi.testclient import TestClient

import petri.config as config
from petri.main import app, get_registry
from petri.registry import Registry


@pytest.fixture
def client(tmp_path) -> TestClient:
    config.WORKSPACE_ROOT = tmp_path
    registry = Registry()
    app.dependency_overrides[get_registry] = lambda: registry
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_health(client: TestClient) -> None:
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_create_sandbox(client: TestClient) -> None:
    response = client.post("/v1/sandboxes", json={"language": "python"})
    assert response.status_code == 201
    data = response.json()
    assert data["id"].startswith("sb_")
    assert data["language"] == "python"
    assert data["status"] == "created"


def test_get_sandbox(client: TestClient) -> None:
    response = client.get("/v1/sandboxes/sb_unknown")
    assert response.status_code == 404


def test_delete_sandbox(client: TestClient) -> None:
    created = client.post("/v1/sandboxes", json={"language": "python"})
    sandbox_id = created.json()["id"]
    response = client.delete(f"/v1/sandboxes/{sandbox_id}")
    assert response.status_code == 204


def test_delete_unknown_sandbox(client: TestClient) -> None:
    response = client.delete("/v1/sandboxes/sb_unknown")
    assert response.status_code == 404


def test_upload_file(client: TestClient) -> None:
    created = client.post("/v1/sandboxes", json={"language": "python"})
    sandbox_id = created.json()["id"]
    response = client.post(
        f"/v1/sandboxes/{sandbox_id}/files",
        files={"file": ("main.py", b"print('hello')", "text/plain")},
    )
    assert response.status_code == 201
    assert response.json() == {"filename": "main.py"}


def test_exec_sandbox(client: TestClient) -> None:
    created = client.post("/v1/sandboxes", json={"language": "python"})
    sandbox_id = created.json()["id"]
    response = client.post(
        f"/v1/sandboxes/{sandbox_id}/files",
        files={"file": ("main.py", b"print('hello')", "text/plain")},
    )
    assert response.status_code == 201

    response = client.post(
        f"/v1/sandboxes/{sandbox_id}/exec",
        json={"command": "python main.py"},
    )

    assert response.status_code == 200
    assert response.json() == {"output": "hello\n"}
