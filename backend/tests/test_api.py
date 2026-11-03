import os
os.environ["DATABASE_URL"] = "sqlite:///./test_collabdocs.db"
import pytest
from fastapi.testclient import TestClient
from app.main import app, Base, engine

@pytest.fixture
def client():
    Base.metadata.drop_all(engine)
    with TestClient(app) as c:
        yield c

def test_document_persists_formatting(client):
    c = client
    doc = c.post("/documents", json={"title": "Plan"}).json()
    content = {"type": "doc", "content": [{"type": "paragraph", "content": [{"type": "text", "text": "Hello", "marks": [{"type": "bold"}]}]}]}
    assert c.patch(f"/documents/{doc['id']}", json={"content": content}).status_code == 200
    assert c.get(f"/documents/{doc['id']}").json()["content"] == content
    # A new application client still reads the committed document from disk.
    with TestClient(app) as reopened:
        assert reopened.get(f"/documents/{doc['id']}").json()["content"] == content

def test_sharing_and_permissions(client):
    c = client
    doc = c.post("/documents", json={"title": "Shared"}).json()
    bob = {"X-User-Id": "2"}
    assert c.get(f"/documents/{doc['id']}", headers=bob).status_code == 403
    assert c.post(f"/documents/{doc['id']}/share", json={"user_id": 2}).status_code == 200
    assert c.get(f"/documents/{doc['id']}", headers=bob).status_code == 200
    assert len(c.get("/documents", headers=bob).json()["shared"]) == 1
    assert c.patch(f"/documents/{doc['id']}", headers=bob, json={"title": "No"}).status_code == 403
    assert c.delete(f"/documents/{doc['id']}", headers=bob).status_code == 403

def test_import_validation_and_content(client):
    c = client
    assert c.post("/documents/import", files={"file": ("bad.pdf", b"x")}).status_code == 422
    doc = c.post("/documents/import", files={"file": ("notes.md", b"# Heading\nBody")}).json()
    assert doc["content"]["content"][0]["type"] == "heading"
    assert c.get(f"/documents/{doc['id']}").status_code == 200
