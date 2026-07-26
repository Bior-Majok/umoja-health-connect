def test_patient_create_consultation_auto_assigns_provider(client, auth_headers, provider_headers):
    _, provider_id = provider_headers
    res = client.post("/api/consultations", headers=auth_headers, json={
        "symptoms": "Fever and headache",
        "language": "en",
    })
    assert res.status_code == 201
    body = res.get_json()["consultation"]
    assert body["provider_id"] == provider_id
    assert body["status"] == "assigned"


def test_consultation_requires_symptoms(client, auth_headers):
    res = client.post("/api/consultations", headers=auth_headers, json={})
    assert res.status_code == 400


def test_volunteer_creates_consultation_for_patient(client, auth_headers, volunteer_headers, provider_headers):
    res = client.post("/api/consultations", headers=volunteer_headers, json={
        "symptoms": "Cough",
        "patient_phone_number": "+254700000000",
    })
    assert res.status_code == 201
    assert res.get_json()["consultation"]["created_by_volunteer_id"] is not None


def test_provider_sees_only_assigned_consultations(client, auth_headers, provider_headers):
    headers, provider_id = provider_headers
    client.post("/api/consultations", headers=auth_headers, json={"symptoms": "Fever"})

    listing = client.get("/api/consultations", headers=headers)
    assert listing.status_code == 200
    consultations = listing.get_json()["consultations"]
    assert len(consultations) == 1
    assert consultations[0]["provider_id"] == provider_id


def test_provider_respond_and_critical_escalates_to_alert(client, auth_headers, provider_headers):
    headers, provider_id = provider_headers
    create = client.post("/api/consultations", headers=auth_headers, json={"symptoms": "High fever"})
    consultation_id = create.get_json()["consultation"]["id"]

    respond = client.patch(f"/api/consultations/{consultation_id}/respond", headers=headers, json={
        "response_notes": "Needs urgent care",
        "status": "responded",
        "urgency": "critical",
    })
    assert respond.status_code == 200
    body = respond.get_json()
    assert body["consultation"]["urgency"] == "critical"
    assert "emergency_alert" in body
    assert body["emergency_alert"]["severity"] == "critical"


def test_respond_requires_assigned_provider(client, auth_headers, provider_headers):
    headers, provider_id = provider_headers
    res = client.patch("/api/consultations/999/respond", headers=headers, json={"status": "responded"})
    assert res.status_code == 404
