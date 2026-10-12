"""
Capstone Backend Tests — Auth  
===========================================
Use pytest + fastapi.testclient.TestClient. Test registration, login, and
that protected routes reject requests without a valid token.

TODO: write at least 1-2 tests covering register/login/protected-route auth.
"""

# TODO: 
from fastapi.testclient import TestClient
# TODO: 
from backend.main import app
# TODO: 
client = TestClient(app)

# TODO: 
def test_register_creates_user():
    response = client.post(
        "/auth/register",
        json={
            "username": "auth_test_user",
            "email": "auth_test_user@example.com",
            "password": "TestPassword123!"
        }
    )

    # Registration should succeed, or report that the user already exists.
    assert response.status_code in [200, 400, 409]

    if response.status_code == 200:
        assert response.json()["username"] == "auth_test_user"
        assert response.json()["email"] == "auth_test_user@example.com"

def test_login_returns_token():
    # First, register a user first so the test can log in (ignore if already exists)
    client.post(
        "/auth/register",
        json={
            "username": "auth_test_user",
            "email": "auth_test_user@example.com",
            "password": "TestPassword123!"
        }
    )


    # Then, attempt to login
    response = client.post(
        "/auth/token",
        data={
            "username": "auth_test_user",
            "password": "TestPassword123!"
        }
    )

    assert response.status_code == 200
    assert "access_token" in response.json()

def test_protected_route_requires_auth(): 
    response = client.get("/auth/me")

    assert response.status_code == 401