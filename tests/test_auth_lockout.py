def _register(client):
    client.post("/api/auth/register", json={
        "full_name": "Lockout Test",
        "phone_number": "+254700222333",
        "age": 25,
        "gender": "male",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "correctpass123",
    })


def test_account_locks_after_five_failed_attempts(client):
    _register(client)

    for _ in range(5):
        res = client.post("/api/auth/login", json={
            "phone_number": "+254700222333",
            "password": "wrongpass",
        })
        assert res.status_code == 401

    locked = client.post("/api/auth/login", json={
        "phone_number": "+254700222333",
        "password": "correctpass123",
    })
    assert locked.status_code == 423


def test_successful_login_resets_failed_attempts(client):
    _register(client)

    for _ in range(3):
        client.post("/api/auth/login", json={
            "phone_number": "+254700222333",
            "password": "wrongpass",
        })

    ok = client.post("/api/auth/login", json={
        "phone_number": "+254700222333",
        "password": "correctpass123",
    })
    assert ok.status_code == 200
