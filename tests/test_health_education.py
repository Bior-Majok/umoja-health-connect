def test_public_get_health_education(client, admin_headers):
    client.post("/api/health-education", headers=admin_headers, json={
        "title": "Preventing Malaria",
        "body": "Sleep under a treated mosquito net...",
        "category": "prevention",
        "language": "en",
        "is_verified": True,
    })
    res = client.get("/api/health-education")
    assert res.status_code == 200
    assert len(res.get_json()["articles"]) == 1


def test_create_requires_admin(client, auth_headers):
    res = client.post("/api/health-education", headers=auth_headers, json={
        "title": "X", "body": "Y", "category": "z",
    })
    assert res.status_code == 403


def test_create_requires_fields(client, admin_headers):
    res = client.post("/api/health-education", headers=admin_headers, json={"title": "X"})
    assert res.status_code == 400


def test_filter_by_language(client, admin_headers):
    client.post("/api/health-education", headers=admin_headers, json={
        "title": "English article", "body": "body", "category": "general", "language": "en",
    })
    client.post("/api/health-education", headers=admin_headers, json={
        "title": "French article", "body": "corps", "category": "general", "language": "fr",
    })
    res = client.get("/api/health-education?lang=fr")
    articles = res.get_json()["articles"]
    assert len(articles) == 1
    assert articles[0]["language"] == "fr"


def test_update_article(client, admin_headers):
    create = client.post("/api/health-education", headers=admin_headers, json={
        "title": "Draft", "body": "body", "category": "general",
    })
    article_id = create.get_json()["article"]["id"]
    update = client.patch(f"/api/health-education/{article_id}", headers=admin_headers, json={"is_verified": True})
    assert update.status_code == 200
    assert update.get_json()["article"]["is_verified"] is True
