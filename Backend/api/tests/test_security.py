import time

import pytest
from fastapi.testclient import TestClient

from conftest import _register_and_login

OWNER = {"X-Device-Secret": "a" * 64}
OTHER = {"X-Device-Secret": "b" * 64}


def profile(client_user_id, name="Sam"):
    return {"client_user_id": client_user_id, "display_name": name, "age": 30}


@pytest.mark.parametrize("headers", [{}, {"X-Device-Secret": "short"}])
def test_onboarding_requires_device_secret(client: TestClient, headers):
    assert client.post("/onboarding/", json=profile("dev-secret-1"), headers=headers).status_code == 401
    assert client.get("/onboarding/dev-secret-1", headers=headers).status_code == 401


def test_onboarding_profile_cannot_be_overwritten_by_another_device(client: TestClient):
    assert client.post("/onboarding/", json=profile("dev-secret-2"), headers=OWNER).status_code == 200

    r = client.post("/onboarding/", json=profile("dev-secret-2", name="Mallory"), headers=OTHER)
    assert r.status_code == 403
    assert client.get("/onboarding/dev-secret-2", headers=OWNER).json()["display_name"] == "Sam"


def test_onboarding_profile_hidden_from_other_devices(client: TestClient):
    client.post("/onboarding/", json=profile("dev-secret-3"), headers=OWNER)
    assert client.get("/onboarding/dev-secret-3", headers=OTHER).status_code == 404
    assert client.get("/onboarding/does-not-exist", headers=OWNER).status_code == 404


def test_legacy_profile_is_claimed_by_first_secret(client: TestClient):
    from app import models
    from app.database import SessionLocal

    with SessionLocal() as db:
        db.add(models.OnboardingProfile(client_user_id="legacy-profile", display_name="Old", age=40))
        db.commit()

    assert client.get("/onboarding/legacy-profile", headers=OWNER).status_code == 404
    assert client.post("/onboarding/", json=profile("legacy-profile"), headers=OWNER).status_code == 200
    assert client.post("/onboarding/", json=profile("legacy-profile"), headers=OTHER).status_code == 403


def test_secret_is_stored_hashed(client: TestClient):
    from app import models
    from app.database import SessionLocal

    client.post("/onboarding/", json=profile("dev-secret-4"), headers=OWNER)
    with SessionLocal() as db:
        cred = db.query(models.OnboardingCredential).filter_by(client_user_id="dev-secret-4").one()
    assert cred.secret_hash != OWNER["X-Device-Secret"]
    assert len(cred.secret_hash) == 64


def test_user_list_is_admin_only(client: TestClient, monkeypatch):
    headers = _register_and_login(client, "plain@example.com", "secret123")
    monkeypatch.delenv("ADMIN_EMAILS", raising=False)
    assert client.get("/users/", headers=headers).status_code == 403

    monkeypatch.setenv("ADMIN_EMAILS", "boss@example.com, PLAIN@example.com")
    assert client.get("/users/", headers=headers).status_code == 200


def test_login_token_uses_configured_expiry(client: TestClient, monkeypatch):
    from jose import jwt
    from app import auth

    monkeypatch.setattr(auth, "ACCESS_TOKEN_EXPIRE_MINUTES", 5)
    headers = _register_and_login(client, "expiry@example.com", "secret123")
    claims = jwt.get_unverified_claims(headers["Authorization"].split()[1])
    me = client.get("/users/me", headers=headers)
    assert me.status_code == 200
    assert 0 < claims["exp"] - time.time() <= 5 * 60


def _preflight(client, origin):
    return client.options(
        "/health",
        headers={"Origin": origin, "Access-Control-Request-Method": "GET"},
    )


def test_cors_allows_only_configured_origins(monkeypatch):
    from app.main import create_app

    monkeypatch.delenv("CORS_ORIGINS", raising=False)
    with TestClient(create_app()) as c:
        assert _preflight(c, "http://localhost:5173").headers.get("access-control-allow-origin") == "http://localhost:5173"
        assert "access-control-allow-origin" not in _preflight(c, "https://evil.example").headers

    monkeypatch.setenv("CORS_ORIGINS", "https://app.example.com")
    with TestClient(create_app()) as c:
        assert _preflight(c, "https://app.example.com").headers.get("access-control-allow-origin") == "https://app.example.com"
        assert "access-control-allow-origin" not in _preflight(c, "http://localhost:5173").headers


@pytest.mark.parametrize("secret", [None, "dev_secret_change_me", "too-short"])
def test_production_refuses_weak_jwt_secret(monkeypatch, secret):
    from app.main import create_app

    monkeypatch.setenv("APP_ENV", "production")
    if secret is None:
        monkeypatch.delenv("JWT_SECRET", raising=False)
    else:
        monkeypatch.setenv("JWT_SECRET", secret)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        create_app()


def test_production_accepts_strong_jwt_secret(monkeypatch):
    from app.main import create_app

    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("JWT_SECRET", "x" * 48)
    create_app()
