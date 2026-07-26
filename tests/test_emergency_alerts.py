def test_trigger_alert_notifies_regional_providers(client, auth_headers, provider_headers):
    res = client.post("/api/emergency-alerts", headers=auth_headers, json={
        "location": "Nairobi, Kenya",
        "condition": "Severe bleeding",
    })
    assert res.status_code == 201
    body = res.get_json()
    assert body["providers_notified"] == 1
    assert body["emergency_alert"]["status"] == "notified"


def test_trigger_alert_requires_location_and_condition(client, auth_headers):
    res = client.post("/api/emergency-alerts", headers=auth_headers, json={})
    assert res.status_code == 400


def test_provider_can_resolve_alert_and_notifies_family(client, app, auth_headers, provider_headers):
    # give the patient a family contact so we can assert the resolve-time SMS fires
    client.patch("/api/auth/me", headers=auth_headers, json={"family_contact_phone": "+254700111222"})

    trigger = client.post("/api/emergency-alerts", headers=auth_headers, json={
        "location": "Nairobi, Kenya",
        "condition": "High fever",
    })
    alert_id = trigger.get_json()["emergency_alert"]["id"]

    headers, _ = provider_headers
    resolve = client.patch(f"/api/emergency-alerts/{alert_id}/resolve", headers=headers)
    assert resolve.status_code == 200
    assert resolve.get_json()["emergency_alert"]["status"] == "resolved"

    with app.app_context():
        from app.models.notification_log import NotificationLog
        family_sms = NotificationLog.query.filter_by(recipient="+254700111222").all()
        assert len(family_sms) == 1


def test_provider_sees_alerts_in_their_region(client, auth_headers, provider_headers):
    client.post("/api/emergency-alerts", headers=auth_headers, json={
        "location": "Nairobi, Kenya",
        "condition": "Chest pain",
    })
    headers, _ = provider_headers
    listing = client.get("/api/emergency-alerts", headers=headers)
    assert listing.status_code == 200
    assert len(listing.get_json()["emergency_alerts"]) == 1
