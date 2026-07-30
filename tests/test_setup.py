def test_seed_admin_rejects_without_secret_configured(client):
    res = client.post("/api/setup/seed-admin", json={
        "full_name": "New Admin",
        "phone_number": "+254700000111",
        "password": "adminpass123",
    })
    assert res.status_code == 403


def test_seed_admin_rejects_wrong_secret(app, client):
    app.config["SETUP_SECRET"] = "correct-secret"
    try:
        res = client.post(
            "/api/setup/seed-admin",
            json={"full_name": "New Admin", "phone_number": "+254700000111", "password": "adminpass123"},
            headers={"X-Setup-Secret": "wrong-secret"},
        )
        assert res.status_code == 403
    finally:
        app.config["SETUP_SECRET"] = None


def test_seed_admin_creates_with_correct_secret(app, client):
    app.config["SETUP_SECRET"] = "correct-secret"
    try:
        res = client.post(
            "/api/setup/seed-admin",
            json={"full_name": "New Admin", "phone_number": "+254700000111", "password": "adminpass123"},
            headers={"X-Setup-Secret": "correct-secret"},
        )
        assert res.status_code == 201
        assert res.get_json()["admin_id"]

        login = client.post("/api/auth/admin/login", json={
            "phone_number": "+254700000111",
            "password": "adminpass123",
        })
        assert login.status_code == 200
    finally:
        app.config["SETUP_SECRET"] = None


def test_seed_admin_rejects_duplicate_phone(app, client):
    app.config["SETUP_SECRET"] = "correct-secret"
    try:
        payload = {"full_name": "New Admin", "phone_number": "+254700000111", "password": "adminpass123"}
        headers = {"X-Setup-Secret": "correct-secret"}
        first = client.post("/api/setup/seed-admin", json=payload, headers=headers)
        assert first.status_code == 201
        second = client.post("/api/setup/seed-admin", json=payload, headers=headers)
        assert second.status_code == 409
    finally:
        app.config["SETUP_SECRET"] = None
