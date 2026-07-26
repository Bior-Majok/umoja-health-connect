def test_default_labels_are_english(client):
    res = client.get("/api/labels")
    assert res.status_code == 200
    body = res.get_json()
    assert body["language"] == "en"
    assert body["dir"] == "ltr"
    assert body["labels"]["login"] == "Login"


def test_arabic_is_rtl(client):
    res = client.get("/api/labels?lang=ar")
    body = res.get_json()
    assert body["dir"] == "rtl"
    assert body["labels"]["login"] == "تسجيل الدخول"


def test_unknown_language_falls_back_to_english(client):
    res = client.get("/api/labels?lang=xx")
    assert res.get_json()["language"] == "en"


def test_languages_endpoint(client):
    res = client.get("/api/labels/languages")
    assert set(res.get_json()["languages"]) == {"en", "fr", "sw", "ar"}
