
import os
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def register_user(username: str, email: str, password: str):
    """Register a new TravelWise user."""
    response = requests.post(
        f"{API_URL}/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def login_user(username: str, password: str):
    """Log in and return the access token."""
    response = requests.post(
        f"{API_URL}/auth/token",
        data={
            "username": username,
            "password": password,
        },
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_profile(token: str):
    """Get the logged-in user's profile."""
    response = requests.get(
        f"{API_URL}/auth/me",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def get_trips(token: str):
    """Get the logged-in user's trips."""
    response = requests.get(
        f"{API_URL}/trips",
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def create_trip(token: str, trip_data: dict):
    """Create a trip for the logged-in user."""
    response = requests.post(
        f"{API_URL}/trips",
        json=trip_data,
        headers={"Authorization": f"Bearer {token}"},
        timeout=30,
    )
    response.raise_for_status()
    return response.json()


def update_trip(token, trip_id, trip_data):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.patch(
        f"{API_URL}/trips/{trip_id}",
        json=trip_data,
        headers=headers
    )

    response.raise_for_status()
    return response.json()


def delete_trip(token, trip_id):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.delete(
        f"{API_URL}/trips/{trip_id}",
        headers=headers
    )

    response.raise_for_status()
    return response.json() if response.content else None


def ask_travel_question(question: str, token: str):
    """Ask the backend the TravelWise AI travel assistant."""
    response = requests.post(
        f"{API_URL}/ask",
        json={"question": question},
        headers={"Authorization": f"Bearer {token}"},
        timeout=120,
    )
    response.raise_for_status()
    return response.json()


def get_destinations(token):
    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{API_URL}/destinations",
        headers=headers
    )

    response.raise_for_status()
    return response.json()