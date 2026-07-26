def test_list_requires_auth(client):
    res = client.get("/api/appointments")
    assert res.status_code == 401


def test_create_and_list_appointment(client, auth_headers, provider_headers):
    _, provider_id = provider_headers
    create = client.post("/api/appointments", headers=auth_headers, json={
        "provider_id": provider_id,
        "clinic_name": "Umoja Community Clinic",
        "scheduled_at": "2026-08-01T10:00:00",
        "notes": "Follow-up",
    })
    assert create.status_code == 201
    body = create.get_json()["appointment"]
    assert body["status"] == "upcoming"
    assert body["doctor_name"] == "Dr. Test Provider"

    listing = client.get("/api/appointments", headers=auth_headers)
    assert listing.status_code == 200
    assert len(listing.get_json()["appointments"]) == 1


def test_create_requires_fields(client, auth_headers):
    res = client.post("/api/appointments", headers=auth_headers, json={"clinic_name": "Clinic"})
    assert res.status_code == 400


def test_create_rejects_unverified_provider(client, auth_headers):
    res = client.post("/api/appointments", headers=auth_headers, json={
        "provider_id": "NOTREAL1",
        "clinic_name": "Clinic",
        "scheduled_at": "2026-08-01T10:00:00",
    })
    assert res.status_code == 400


def test_create_rejects_bad_datetime(client, auth_headers, provider_headers):
    _, provider_id = provider_headers
    res = client.post("/api/appointments", headers=auth_headers, json={
        "provider_id": provider_id,
        "clinic_name": "Clinic",
        "scheduled_at": "not-a-date",
    })
    assert res.status_code == 400


def test_cancel_appointment(client, auth_headers, provider_headers):
    _, provider_id = provider_headers
    create = client.post("/api/appointments", headers=auth_headers, json={
        "provider_id": provider_id,
        "clinic_name": "Umoja Community Clinic",
        "scheduled_at": "2026-08-01T10:00:00",
    })
    appointment_id = create.get_json()["appointment"]["id"]

    cancel = client.patch(f"/api/appointments/{appointment_id}", headers=auth_headers, json={"status": "cancelled"})
    assert cancel.status_code == 200
    assert cancel.get_json()["appointment"]["status"] == "cancelled"


def test_cancel_nonexistent_appointment(client, auth_headers):
    res = client.patch("/api/appointments/999", headers=auth_headers, json={"status": "cancelled"})
    assert res.status_code == 404


def test_provider_lists_and_completes_their_appointments(client, auth_headers, provider_headers):
    headers, provider_id = provider_headers
    create = client.post("/api/appointments", headers=auth_headers, json={
        "provider_id": provider_id,
        "clinic_name": "Umoja Community Clinic",
        "scheduled_at": "2026-08-01T10:00:00",
    })
    appointment_id = create.get_json()["appointment"]["id"]

    listing = client.get("/api/appointments/provider", headers=headers)
    assert listing.status_code == 200
    assert len(listing.get_json()["appointments"]) == 1

    complete = client.patch(f"/api/appointments/{appointment_id}/complete", headers=headers)
    assert complete.status_code == 200
    assert complete.get_json()["appointment"]["status"] == "completed"
