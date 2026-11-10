import os
import sys
import tempfile
from pathlib import Path

# Use a throw-away database and make sure tests never touch your real one.
_tmp = tempfile.mkdtemp()
os.environ["DATABASE_URL"] = f"sqlite:///{Path(_tmp, 'test.db').as_posix()}"
os.environ["ALLOW_PRIVATE_TARGETS"] = "false"
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture(scope="session")
def client():
    with TestClient(app) as c:
        yield c


def make_user(client, name):
    client.post("/api/auth/register", json={"username": name, "email": f"{name}@example.com", "password": "password123"})
    r = client.post("/api/auth/login", data={"username": name, "password": "password123"})
    return {"Authorization": "Bearer " + r.json()["access_token"]}
