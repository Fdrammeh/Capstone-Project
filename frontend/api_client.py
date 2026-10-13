import os
import requests

API_URL = os.getenv("API_URL", "http://localhost:8000").rstrip("/")


def _request(method: str, endpoint: str, **kwargs):
    """Send an API request and raise a user-friendly error if it fails."""
    kwargs.setdefault("timeout", 30)

    try:
        response = requests.request(
            method,
            f"{API_URL}{endpoint}",
            **kwargs,
        )
        response.raise_for_status()
        return response

    except requests.exceptions.Timeout as error:
        raise requests.RequestException(
            "The request took too long. Please try again later."
        ) from error

    except requests.exceptions.ConnectionError as error:
        raise requests.RequestException(
            "TravelWise cannot connect to the backend. "
            "Please check that the application is running."
        ) from error

    except requests.exceptions.HTTPError as error:
        status_code = error.response.status_code

        if status_code == 401 and endpoint == "/auth/token":
            message = "Incorrect username or password. Please try again."
        elif status_code == 401:
            message = "Your session may have expired. Please log in again."
        elif status_code == 403:
            message = "You do not have permission to perform this action."
        elif status_code == 404:
            message = "The requested information could not be found."
        elif status_code == 422:
            message = "Some information is missing or invalid. Please check your entries."
        elif status_code >= 500:
            message = "The server encountered a problem. Please try again later."
        else:
            message = "The request could not be completed. Please check your entries."

        raise requests.RequestException(message) from error


def _json_request(method: str, endpoint: str, **kwargs):
    """Send a request and return its JSON response."""
    response = _request(method, endpoint, **kwargs)
    return response.json()


def register_user(username: str, email: str, password: str):
    """Register a new TravelWise user."""
    return _json_request(
        "POST",
        "/auth/register",
        json={
            "username": username,
            "email": email,
            "password": password,
        },
    )


def login_user(username: str, password: str):
    """Log in and return the access token."""
    return _json_request(
        "POST",
        "/auth/token",
        data={
            "username": username,
            "password": password,
        },
    )


def get_profile(token: str):
    """Get the logged-in user's profile."""
    return _json_request(
        "GET",
        "/auth/me",
        headers={"Authorization": f"Bearer {token}"},
    )


def get_trips(token: str):
    """Get the logged-in user's trips."""
    return _json_request(
        "GET",
        "/trips",
        headers={"Authorization": f"Bearer {token}"},
    )


def create_trip(token: str, trip_data: dict):
    """Create a trip for the logged-in user."""
    return _json_request(
        "POST",
        "/trips",
        json=trip_data,
        headers={"Authorization": f"Bearer {token}"},
    )


def update_trip(token, trip_id, trip_data):
    """Update an existing trip."""
    return _json_request(
        "PATCH",
        f"/trips/{trip_id}",
        json=trip_data,
        headers={"Authorization": f"Bearer {token}"},
    )


def delete_trip(token, trip_id):
    """Delete an existing trip."""
    response = _request(
        "DELETE",
        f"/trips/{trip_id}",
        headers={"Authorization": f"Bearer {token}"},
    )
    return response.json() if response.content else None


def ask_travel_question(question: str, token: str):
    """Ask the backend the TravelWise AI travel assistant."""
    return _json_request(
        "POST",
        "/ask",
        json={"question": question},
        headers={"Authorization": f"Bearer {token}"},
        timeout=130,
    )


def get_destinations(token):
    """Get available travel destinations."""
    return _json_request(
        "GET",
        "/destinations",
        headers={"Authorization": f"Bearer {token}"},
    )