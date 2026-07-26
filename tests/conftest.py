import uuid
import pytest
from app import create_app, db
from app.models.admin import Administrator


@pytest.fixture
def app():
    app = create_app({
        "TESTING": True,
        "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    })
    yield app


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_headers(client):
    client.post("/api/auth/register", json={
        "full_name": "Test Patient",
        "phone_number": "+254700000000",
        "age": 30,
        "gender": "female",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "password123",
    })
    res = client.post("/api/auth/login", json={
        "phone_number": "+254700000000",
        "password": "password123",
    })
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def admin_headers(app, client):
    with app.app_context():
        admin = Administrator(
            admin_id=str(uuid.uuid4())[:8].upper(),
            full_name="Test Admin",
            phone_number="+254799999999",
            scope_level="national",
        )
        admin.set_password("adminpass123")
        db.session.add(admin)
        db.session.commit()

    res = client.post("/api/auth/admin/login", json={
        "phone_number": "+254799999999",
        "password": "adminpass123",
    })
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def provider_headers(client, admin_headers):
    reg = client.post("/api/auth/provider/register", json={
        "full_name": "Dr. Test Provider",
        "phone_number": "+254788888888",
        "specialization": "General Medicine",
        "country": "Kenya",
        "region": "Nairobi",
        "password": "providerpass123",
    })
    provider_id = reg.get_json()["provider"]["provider_id"]

    client.patch(f"/api/providers/{provider_id}/verify", headers=admin_headers)

    res = client.post("/api/auth/provider/login", json={
        "phone_number": "+254788888888",
        "password": "providerpass123",
    })
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}, provider_id


@pytest.fixture
def volunteer_headers(client):
    client.post("/api/auth/volunteer/register", json={
        "full_name": "Test Volunteer",
        "phone_number": "+254777777777",
        "assigned_region": "Nairobi",
        "password": "volunteerpass123",
    })
    res = client.post("/api/auth/volunteer/login", json={
        "phone_number": "+254777777777",
        "password": "volunteerpass123",
    })
    token = res.get_json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
