from fastapi.testclient import TestClient


def test_health(client: TestClient):
    res = client.get("/health")
    assert res.status_code == 200
    assert res.json() == {"status": "ok"}


def test_register_and_login(client: TestClient):
    email = "test@example.com"
    password = "secret123"
    r = client.post("/auth/register", json={"email": email, "password": password})
    assert r.status_code in (200, 400)
    lr = client.post(
        "/auth/login",
        data={"username": email, "password": password, "grant_type": "password"},
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    assert lr.status_code == 200
    data = lr.json()
    assert "access_token" in data
    assert data.get("token_type") == "bearer"


def test_users_me_and_list(client: TestClient, auth_headers: dict):
    me = client.get("/users/me", headers=auth_headers)
    assert me.status_code == 200
    assert "email" in me.json()

    lst = client.get("/users/", headers=auth_headers)
    assert lst.status_code == 200
    assert isinstance(lst.json(), list)


def test_sessions_crud(client: TestClient, auth_headers: dict):
    created = client.post(
        "/sessions/",
        json={"mood": "sadness", "duration_seconds": 600},
        headers=auth_headers,
    )
    assert created.status_code == 200, created.text
    body = created.json()
    assert body.get("mood") == "sadness"
    assert body.get("duration_seconds") == 600

    lst = client.get("/sessions/", headers=auth_headers)
    assert lst.status_code == 200
    assert len(lst.json()) >= 1


def test_onboarding_upsert_and_get(client: TestClient):
    payload = {"client_user_id": "abc123456", "display_name": "Alice", "age": 22}
    res = client.post("/onboarding/", json=payload)
    assert res.status_code == 200, res.text
    data = res.json()
    assert data["client_user_id"] == payload["client_user_id"]
    assert data["display_name"] == payload["display_name"]
    assert data["age"] == payload["age"]

    # Update
    payload_update = {"client_user_id": "abc123456", "display_name": "Alice B", "age": 23}
    res2 = client.post("/onboarding/", json=payload_update)
    assert res2.status_code == 200
    data2 = res2.json()
    assert data2["display_name"] == "Alice B"
    assert data2["age"] == 23

    fetched = client.get(f"/onboarding/{payload['client_user_id']}")
    assert fetched.status_code == 200
    assert fetched.json()["client_user_id"] == payload["client_user_id"]

