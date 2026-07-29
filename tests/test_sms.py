def test_symptom_command_creates_consultation(client, auth_headers, provider_headers):
    _, provider_id = provider_headers
    res = client.post("/api/sms/inbound", data={
        "from": "+254700000000",
        "text": "SYMPTOM fever and chills for two days",
    })
    assert res.status_code == 201
    body = res.get_json()
    assert body["status"] == "consultation_created"

    listing = client.get("/api/consultations", headers=auth_headers)
    consultations = listing.get_json()["consultations"]
    assert any(c["id"] == body["consultation_id"] and c["provider_id"] == provider_id for c in consultations)


def test_emergency_command_creates_alert(client, auth_headers, provider_headers):
    res = client.post("/api/sms/inbound", data={
        "from": "+254700000000",
        "text": "EMERGENCY severe bleeding after accident",
    })
    assert res.status_code == 201
    assert res.get_json()["status"] == "alert_created"

    listing = client.get("/api/emergency-alerts", headers=auth_headers)
    alerts = listing.get_json()["emergency_alerts"]
    assert any(a["id"] == res.get_json()["alert_id"] for a in alerts)


def test_unknown_command_sends_help(app, client, auth_headers):
    res = client.post("/api/sms/inbound", data={
        "from": "+254700000000",
        "text": "WHATEVER",
    })
    assert res.status_code == 200
    assert res.get_json()["status"] == "help_sent"

    with app.app_context():
        from app.models.notification_log import NotificationLog
        logs = NotificationLog.query.filter_by(recipient="+254700000000", channel="sms").all()
        assert any("commands" in log.message.lower() for log in logs)


def test_unknown_phone_number_gets_no_account_reply(app, client):
    res = client.post("/api/sms/inbound", data={
        "from": "+254799000000",
        "text": "SYMPTOM headache",
    })
    assert res.status_code == 200
    assert res.get_json()["status"] == "no_account"

    with app.app_context():
        from app.models.notification_log import NotificationLog
        logs = NotificationLog.query.filter_by(recipient="+254799000000", channel="sms").all()
        assert any("could not find" in log.message.lower() for log in logs)


def test_missing_fields_rejected(client):
    res = client.post("/api/sms/inbound", data={"from": "+254700000000"})
    assert res.status_code == 400


def test_inbound_requires_shared_secret_when_configured(app, client):
    app.config["SMS_INBOUND_SECRET"] = "topsecret"
    try:
        res = client.post("/api/sms/inbound", data={"from": "+254700000000", "text": "HELP"})
        assert res.status_code == 403

        res = client.post("/api/sms/inbound", data={"from": "+254700000000", "text": "HELP", "secret": "topsecret"})
        assert res.status_code == 200
    finally:
        app.config["SMS_INBOUND_SECRET"] = None
