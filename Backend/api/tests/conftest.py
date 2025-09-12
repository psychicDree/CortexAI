import os
import sys
import pathlib
import shutil
import tempfile
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="session", autouse=True)
def _set_test_database_env() -> None:
    # Use a temporary SQLite database file for the test session
    tmp_dir = tempfile.mkdtemp(prefix="cortexai_test_")
    db_path = pathlib.Path(tmp_dir) / "cortexai_test.db"
    os.environ["DATABASE_URL"] = f"sqlite:///{db_path}"
    yield
    try:
        shutil.rmtree(tmp_dir, ignore_errors=True)
    except Exception:
        pass


@pytest.fixture()
def client(_set_test_database_env):
    # Import after DATABASE_URL is set so the app binds to the test DB
    # Ensure repository root (Backend/api) is on sys.path for 'app' package
    repo_root = pathlib.Path(__file__).resolve().parents[1]
    if str(repo_root) not in sys.path:
        sys.path.insert(0, str(repo_root))
    from app.main import create_app

    app = create_app()
    with TestClient(app) as test_client:
        yield test_client


def _register_and_login(client: TestClient, email: str, password: str) -> dict:
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 400)
    lr = client.post(
        "/auth/login",
        data={"username": email, "password": password, "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert lr.status_code == 200, lr.text
    token = lr.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def auth_headers(client: TestClient) -> dict:
    return _register_and_login(client, "user@example.com", "secret123")

