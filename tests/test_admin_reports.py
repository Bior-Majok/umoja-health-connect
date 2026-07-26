def test_reports_requires_admin(client, auth_headers):
    res = client.get("/api/admin/reports", headers=auth_headers)
    assert res.status_code == 403


def test_reports_returns_aggregates(client, admin_headers, provider_headers):
    res = client.get("/api/admin/reports", headers=admin_headers)
    assert res.status_code == 200
    body = res.get_json()
    assert body["verified_providers"] == 1
    assert "providers_by_region" in body
    assert "consultations_by_status" in body
