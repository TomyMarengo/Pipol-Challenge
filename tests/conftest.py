"""Pytest configuration and fixtures."""

import pytest
from fastapi.testclient import TestClient

from app.main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_token(client):
    """Get a valid authentication token."""
    response = client.post(
        "/auth/token",
        json={
            "grant_type": "client_credentials",
            "client_id": "pipol_client",
            "client_secret": "pipol_secret_2024",
        },
    )
    return response.json()["access_token"]


@pytest.fixture
def auth_headers(auth_token):
    """Get authentication headers with valid token."""
    return {"Authorization": f"Bearer {auth_token}"}
