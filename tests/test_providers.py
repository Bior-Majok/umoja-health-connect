def test_register_provider_unverified_cannot_login(client):
    client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Jane",
        "phone_number": "+254711100000",
        "specialization": "Pediatrics",
        "country": "Kenya",
        "region": "Kisumu",
        "password": "password123",
    })
    res = client.post("/api/auth/provider/login", json={
        "phone_number": "+254711100000",
        "password": "password123",
    })
    assert res.status_code == 403


def test_admin_can_verify_and_suspend_provider(client, admin_headers):
    reg = client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Jane",
        "phone_number": "+254711100001",
        "specialization": "Pediatrics",
        "country": "Kenya",
        "region": "Kisumu",
        "password": "password123",
    })
    provider_id = reg.get_json()["provider"]["provider_id"]

    verify = client.patch(f"/api/providers/{provider_id}/verify", headers=admin_headers)
    assert verify.status_code == 200
    assert verify.get_json()["provider"]["is_verified"] is True

    login = client.post("/api/auth/provider/login", json={
        "phone_number": "+254711100001",
        "password": "password123",
    })
    assert login.status_code == 200

    suspend = client.patch(f"/api/providers/{provider_id}/suspend", headers=admin_headers)
    assert suspend.status_code == 200
    assert suspend.get_json()["provider"]["is_verified"] is False


def test_verify_requires_admin_role(client, auth_headers):
    res = client.patch("/api/providers/SOMEID/verify", headers=auth_headers)
    assert res.status_code == 403


def test_list_providers_only_verified_by_default(client, provider_headers):
    client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Unverified",
        "phone_number": "+254711100002",
        "specialization": "Pediatrics",
        "country": "Kenya",
        "region": "Kisumu",
        "password": "password123",
    })
    res = client.get("/api/providers")
    assert res.status_code == 200
    providers = res.get_json()["providers"]
    assert all(p["is_verified"] for p in providers)
