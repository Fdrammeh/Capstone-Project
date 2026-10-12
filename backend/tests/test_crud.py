"""
Capstone Backend Tests — CRUD  
===========================================
Test creating, reading, updating, and/or deleting your main entity
(whatever your app manages: documents, recipes, job postings, notes, etc.).

TODO: write at least 1-2 tests covering your core CRUD endpoints.
"""
from datetime import date, timedelta
from uuid import uuid4
# TODO: 
from fastapi.testclient import TestClient
# TODO: 
from backend.main import app
from backend.database import SessionLocal
from backend.models import Destination

# TODO: 
client = TestClient(app)

def get_auth_headers():
    """Register a test user and return authentication headers."""
    unique_id = uuid4().hex[:8]
    username = f"crud_{unique_id}"

    client.post(
        "/auth/register",
        json={
            "username": username,
            "email": f"{username}@example.com",
            "password": "TestPassword123!"
        }
    )

    response = client.post(
        "/auth/token",
        data={
            "username": username,
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200
    token = response.json()["access_token"]

    return {"Authorization": f"Bearer {token}"}

# TODO: 
def test_create_entity():
# TODO: 
    headers = get_auth_headers()



    db = SessionLocal()
    try:
        destination = db.query(Destination).first()
        assert destination is not None, "Add a destination before running this test."
        destination_id = destination.id
    finally:
        db.close()

    start_date = date.today() + timedelta(days=30)
    end_date = start_date + timedelta(days=5)

    response = client.post(
        "/trips",
        headers=headers,
        json={
            "trip_name": "Test Trip",
            "destination_id": destination_id,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(),
            "notes": "Created by a CRUD test"
        }
    )

    assert response.status_code == 200
    assert response.json()["trip_name"] == "Test Trip"
def test_list_entities():
    headers = get_auth_headers()

    response = client.get(
        "/trips",
        headers=headers
    )

    assert response.status_code == 200
    assert isinstance(response.json(), list)
