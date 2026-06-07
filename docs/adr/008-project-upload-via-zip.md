# ADR 008 - Project Upload via Zip

**Status:** Accepted

## Context

The current upload endpoint accepts one file at a time and strips directory paths.
This means folder structure is lost - a project with `app.py`, `tests/test_app.py`, 
and `requirements.txt` cannot be uploaded correctly.

Test mode (ADR 007) requires the full project structure to be preserved in the
sandbox workspace - test runners depend on finding tests in the right directories.

## Decision

Add a new endpoint to accept a zip file and extract it into the sandbox workspace,
preserving the full folder structure.

The existing single-file upload endpoint is retained for simple use cases.

## API Change

```
POST /v1/sandboxes/{id}/upload
Content-Type: multipart/form-data

file: <project.zip>
```

Petri extracts the zip into the sandbox workspace. Folder structure is preserved.

## Behaviour

- Only `.zip` files are accepted
- Files are extracted relative to the sandbox workspace root
- Existing files in the workspace are overwritten if present
- Zip files with absolute paths or path traversal(`../`) are rejected for security

## SDK

The SDK will handle zipping transparently. The user points to a local folder:

```python
sandbox = Sandbox.from_folder("./my_project")
```

The SDK zips the folder and calls the upload endpoint. The user never interacts
with zip files directly.

Delta sync - uploading only changed files on subsequent uploads - is deferred to future release.

## Consequences

- Full project structure is preserved in the sandbox workspace
- Test mode (ADR 007) works correctly with nested test directories
- Single-file upload endpoint remains unchanged
- Zip extraction happens synchronously - large projects may be slow to upload
