def test_list_requires_auth(client):
    res = client.get("/api/records")
    assert res.status_code == 401


def test_create_and_list_record(client, auth_headers):
    create = client.post("/api/records", headers=auth_headers, json={
        "title": "Blood Pressure Screening",
        "details": "118/76 mmHg",
        "recorded_at": "2026-06-02T09:00:00",
        "status": "normal",
    })
    assert create.status_code == 201
    assert create.get_json()["record"]["status"] == "normal"

    listing = client.get("/api/records", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.get_json()["records"]) == 1


def test_create_defaults_recorded_at_and_status(client, auth_headers):
    res = client.post("/api/records", headers=auth_headers, json={"title": "Weight Check"})
    assert res.status_code == 201
    body = res.get_json()["record"]
    assert body["status"] == "normal"
    assert body["recorded_at"]


def test_create_requires_title(client, auth_headers):
    res = client.post("/api/records", headers=auth_headers, json={"details": "no title"})
    assert res.status_code == 400


def test_create_rejects_bad_status(client, auth_headers):
    res = client.post("/api/records", headers=auth_headers, json={"title": "X", "status": "unknown"})
    assert res.status_code == 400
