def test_public_get_facilities(client, admin_headers):
    client.post("/api/facilities", headers=admin_headers, json={
        "name": "Kisumu Community Clinic",
        "facility_type": "clinic",
        "country": "Kenya",
        "region": "Kisumu",
    })
    res = client.get("/api/facilities")
    assert res.status_code == 200
    assert len(res.get_json()["facilities"]) == 1


def test_create_requires_admin(client, auth_headers):
    res = client.post("/api/facilities", headers=auth_headers, json={
        "name": "X", "country": "Kenya", "region": "Nairobi",
    })
    assert res.status_code == 403


def test_create_requires_fields(client, admin_headers):
    res = client.post("/api/facilities", headers=admin_headers, json={"name": "X"})
    assert res.status_code == 400


def test_create_rejects_bad_type(client, admin_headers):
    res = client.post("/api/facilities", headers=admin_headers, json={
        "name": "X", "country": "Kenya", "region": "Nairobi", "facility_type": "spaceship",
    })
    assert res.status_code == 400


def test_filter_by_region(client, admin_headers):
    client.post("/api/facilities", headers=admin_headers, json={
        "name": "Nairobi Hospital", "country": "Kenya", "region": "Nairobi", "facility_type": "hospital",
    })
    client.post("/api/facilities", headers=admin_headers, json={
        "name": "Kisumu Clinic", "country": "Kenya", "region": "Kisumu",
    })
    res = client.get("/api/facilities?region=Kisumu")
    facilities = res.get_json()["facilities"]
    assert len(facilities) == 1
    assert facilities[0]["region"] == "Kisumu"


def test_admin_can_delete_facility(client, admin_headers):
    create = client.post("/api/facilities", headers=admin_headers, json={
        "name": "Temp Clinic", "country": "Kenya", "region": "Nairobi",
    })
    facility_id = create.get_json()["facility"]["id"]
    delete = client.delete(f"/api/facilities/{facility_id}", headers=admin_headers)
    assert delete.status_code == 200
    res = client.get("/api/facilities")
    assert len(res.get_json()["facilities"]) == 0
