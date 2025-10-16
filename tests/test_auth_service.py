"""Unit tests for authentication service."""

import pytest
from datetime import timedelta
from app.services.auth_service import AuthService


class TestAuthService:
    """Test cases for AuthService."""

    def setup_method(self):
        """Set up test instance."""
        self.auth_service = AuthService()

    def test_verify_client_credentials_valid(self):
        """Test verification with valid credentials."""
        result = self.auth_service.verify_client_credentials(
            "pipol_client",
            "pipol_secret_2024"
        )
        assert result is True

    def test_verify_client_credentials_invalid_id(self):
        """Test verification with invalid client ID."""
        result = self.auth_service.verify_client_credentials(
            "invalid_client",
            "pipol_secret_2024"
        )
        assert result is False

    def test_verify_client_credentials_invalid_secret(self):
        """Test verification with invalid client secret."""
        result = self.auth_service.verify_client_credentials(
            "pipol_client",
            "wrong_secret"
        )
        assert result is False

    def test_create_access_token(self):
        """Test JWT token creation."""
        data = {"sub": "pipol_client", "type": "client_credentials"}
        token = self.auth_service.create_access_token(data)
        
        assert token is not None
        assert isinstance(token, str)
        assert len(token) > 0

    def test_create_access_token_with_expiration(self):
        """Test JWT token creation with custom expiration."""
        data = {"sub": "pipol_client"}
        expires_delta = timedelta(minutes=60)
        token = self.auth_service.create_access_token(data, expires_delta)
        
        assert token is not None
        assert isinstance(token, str)

    def test_verify_token_valid(self):
        """Test token verification with valid token."""
        data = {"sub": "pipol_client", "type": "client_credentials"}
        token = self.auth_service.create_access_token(data)
        
        payload = self.auth_service.verify_token(token)
        
        assert payload is not None
        assert payload["sub"] == "pipol_client"
        assert payload["type"] == "client_credentials"
        assert "exp" in payload
        assert "iat" in payload

    def test_verify_token_invalid(self):
        """Test token verification with invalid token."""
        invalid_token = "invalid.token.here"
        payload = self.auth_service.verify_token(invalid_token)
        
        assert payload is None

    def test_verify_token_malformed(self):
        """Test token verification with malformed token."""
        malformed_token = "not-a-jwt-token"
        payload = self.auth_service.verify_token(malformed_token)
        
        assert payload is None

