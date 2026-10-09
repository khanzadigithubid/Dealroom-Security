def test_register_returns_token(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "new@example.com",
            "password": "password123",
            "full_name": "New User",
            "company_name": "New Co",
        },
    )
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["token_type"] == "bearer"
    assert body["access_token"]


def test_register_duplicate_email(client, register):
    user = register(email="dupe@example.com")
    resp = client.post(
        "/api/auth/register",
        json={
            "email": user["email"],
            "password": "password123",
            "full_name": "Other",
            "company_name": "Other Co",
        },
    )
    assert resp.status_code == 400
    assert "already registered" in resp.text.lower()


def test_register_rejects_short_password(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "short@example.com",
            "password": "short",
            "full_name": "A",
            "company_name": "Acme",
        },
    )
    assert resp.status_code == 422


def test_register_rejects_email_without_domain_dot(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "user@localhost",
            "password": "password123",
            "full_name": "A",
            "company_name": "Acme",
        },
    )
    assert resp.status_code == 422


def test_register_rejects_short_company_name(client):
    resp = client.post(
        "/api/auth/register",
        json={
            "email": "ok@example.com",
            "password": "password123",
            "full_name": "A",
            "company_name": "X",
        },
    )
    assert resp.status_code == 422


def test_login_success(client, register):
    user = register(email="login@example.com", password="password123")
    resp = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": "password123"},
    )
    assert resp.status_code == 200, resp.text
    assert resp.json()["access_token"]


def test_login_wrong_password(client, register):
    user = register(email="wrong@example.com", password="password123")
    resp = client.post(
        "/api/auth/login",
        data={"username": user["email"], "password": "nope-nope-nope"},
    )
    assert resp.status_code == 400


def test_me_requires_token(client):
    assert client.get("/api/auth/me").status_code == 401


def test_me_returns_current_user(client, register):
    user = register(email="me@example.com", full_name="Me Myself")
    resp = client.get("/api/auth/me", headers=user["headers"])
    assert resp.status_code == 200
    assert resp.json()["email"] == user["email"]
    assert resp.json()["full_name"] == "Me Myself"
