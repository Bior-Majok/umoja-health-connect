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


def test_region_matching_is_case_and_whitespace_tolerant(client, admin_headers, auth_headers):
    # Patient region fixture is "Nairobi" — register a provider with mismatched
    # case/whitespace and confirm auto-assignment still finds them.
    reg = client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Messy Region",
        "phone_number": "+254733221100",
        "specialization": "General Medicine",
        "country": "Kenya",
        "region": "  nairobi ",
        "password": "providerpass123",
    })
    provider_id = reg.get_json()["provider"]["provider_id"]
    client.patch(f"/api/providers/{provider_id}/verify", headers=admin_headers)

    res = client.post("/api/consultations", headers=auth_headers, json={"symptoms": "Cough"})
    assert res.status_code == 201
    assert res.get_json()["consultation"]["provider_id"] == provider_id


def test_routine_response_notifies_patient_by_sms(client, app, auth_headers, provider_headers):
    headers, provider_id = provider_headers
    create = client.post("/api/consultations", headers=auth_headers, json={"symptoms": "Mild cough"})
    consultation_id = create.get_json()["consultation"]["id"]

    respond = client.patch(f"/api/consultations/{consultation_id}/respond", headers=headers, json={
        "response_notes": "Rest and fluids",
        "status": "closed",
    })
    assert respond.status_code == 200
    assert "emergency_alert" not in respond.get_json()

    with app.app_context():
        from app.models.notification_log import NotificationLog
        patient_sms = NotificationLog.query.filter_by(recipient="+254700000000", channel="sms").all()
        assert any("responded" in log.message for log in patient_sms)


def test_child_symptoms_route_to_pediatric_provider_over_general(client, admin_headers, auth_headers, provider_headers):
    # provider_headers fixture is a "General Medicine" provider in Nairobi (least loaded
    # by default); register a pediatric-specialized provider in the same region and
    # confirm symptom text mentioning a child routes there instead (FR 2.2).
    _, general_provider_id = provider_headers
    reg = client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Pediatric Test",
        "phone_number": "+254733112211",
        "specialization": "Pediatric Medicine",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "providerpass123",
    })
    pediatric_provider_id = reg.get_json()["provider"]["provider_id"]
    client.patch(f"/api/providers/{pediatric_provider_id}/verify", headers=admin_headers)

    res = client.post("/api/consultations", headers=auth_headers, json={"symptoms": "My baby has a high fever"})
    assert res.status_code == 201
    assert res.get_json()["consultation"]["provider_id"] == pediatric_provider_id
    assert res.get_json()["consultation"]["provider_id"] != general_provider_id


def test_escalation_sweep_reassigns_stale_critical_consultation(app, client, auth_headers, provider_headers, admin_headers):
    from datetime import datetime, timedelta
    from app import db
    from app.models.consultation import Consultation
    from app.routes.consultations import run_escalation_sweep

    headers, first_provider_id = provider_headers
    reg = client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Backup Provider",
        "phone_number": "+254733445566",
        "specialization": "General Medicine",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "providerpass123",
    })
    second_provider_id = reg.get_json()["provider"]["provider_id"]
    client.patch(f"/api/providers/{second_provider_id}/verify", headers=admin_headers)

    create = client.post("/api/consultations", headers=auth_headers, json={"symptoms": "Chest pain"})
    consultation_id = create.get_json()["consultation"]["id"]
    assert create.get_json()["consultation"]["provider_id"] == first_provider_id

    with app.app_context():
        consultation = db.session.get(Consultation, consultation_id)
        consultation.urgency = "critical"
        consultation.assigned_at = datetime.utcnow() - timedelta(hours=3)
        db.session.commit()

        escalated_ids = run_escalation_sweep()
        assert consultation_id in escalated_ids

        refreshed = db.session.get(Consultation, consultation_id)
        assert refreshed.provider_id == second_provider_id
        assert refreshed.escalation_count == 1


def test_escalation_sweep_leaves_fresh_consultations_alone(app, client, auth_headers, provider_headers):
    from app import db
    from app.models.consultation import Consultation
    from app.routes.consultations import run_escalation_sweep

    headers, provider_id = provider_headers
    create = client.post("/api/consultations", headers=auth_headers, json={"symptoms": "Mild headache"})
    consultation_id = create.get_json()["consultation"]["id"]

    with app.app_context():
        escalated_ids = run_escalation_sweep()
        assert consultation_id not in escalated_ids
        assert db.session.get(Consultation, consultation_id).provider_id == provider_id
