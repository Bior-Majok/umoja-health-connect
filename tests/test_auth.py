def register(client, phone="+254700000001"):
    return client.post("/api/auth/register", json={
        "full_name": "Jane Doe",
        "phone_number": phone,
        "age": 25,
        "gender": "female",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "password123",
    })


def test_register_success(client):
    res = register(client)
    assert res.status_code == 201
    assert res.get_json()["patient"]["phone_number"] == "+254700000001"


def test_register_duplicate_phone_rejected(client):
    register(client)
    res = register(client)
    assert res.status_code == 409


def test_register_rejects_invalid_phone(client):
    res = client.post("/api/auth/register", json={
        "full_name": "Jane Doe",
        "phone_number": "abc",
        "age": 25,
        "gender": "female",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "password123",
    })
    assert res.status_code == 400


def test_register_rejects_invalid_age(client):
    res = client.post("/api/auth/register", json={
        "full_name": "Jane Doe",
        "phone_number": "+254700000002",
        "age": -5,
        "gender": "female",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "password123",
    })
    assert res.status_code == 400


def test_login_success_and_failure(client):
    register(client)
    ok = client.post("/api/auth/login", json={
        "phone_number": "+254700000001",
        "password": "password123",
    })
    assert ok.status_code == 200
    assert "access_token" in ok.get_json()

    bad = client.post("/api/auth/login", json={
        "phone_number": "+254700000001",
        "password": "wrong",
    })
    assert bad.status_code == 401


def test_me_requires_auth(client):
    res = client.get("/api/auth/me")
    assert res.status_code == 401


def test_me_get_and_update(client, auth_headers):
    res = client.get("/api/auth/me", headers=auth_headers)
    assert res.status_code == 200
    assert res.get_json()["patient"]["full_name"] == "Test Patient"

    patch = client.patch("/api/auth/me", headers=auth_headers, json={"full_name": "Updated Name"})
    assert patch.status_code == 200
    assert patch.get_json()["patient"]["full_name"] == "Updated Name"
