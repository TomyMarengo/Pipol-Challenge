"""Unit tests for authentication service."""

from datetime import timedelta

from app.services.auth_service import AuthService


class TestAuthService:
    """Test cases for AuthService."""

    def setup_method(self):
        """Set up test instance."""
        self.auth_service = AuthService()

    def test_verify_client_credentials_valid(self):
        """Test verification with valid credentials."""
        result = self.auth_service.verify_client_credentials("pipol_client", "pipol_secret_2024")
        assert result is True

    def test_verify_client_credentials_invalid_id(self):
        """Test verification with invalid client ID."""
        result = self.auth_service.verify_client_credentials("invalid_client", "pipol_secret_2024")
        assert result is False

    def test_verify_client_credentials_invalid_secret(self):
        """Test verification with invalid client secret."""
        result = self.auth_service.verify_client_credentials("pipol_client", "wrong_secret")
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

    def test_create_refresh_token(self):
        """Test refresh token creation."""
        client_id = "pipol_client"
        refresh_token = self.auth_service.create_refresh_token(client_id)

        assert refresh_token is not None
        assert isinstance(refresh_token, str)
        assert len(refresh_token) > 0
        # Check that token is stored
        assert self.auth_service.verify_refresh_token(refresh_token) is True

    def test_verify_refresh_token_valid(self):
        """Test refresh token verification with valid token."""
        client_id = "pipol_client"
        refresh_token = self.auth_service.create_refresh_token(client_id)

        result = self.auth_service.verify_refresh_token(refresh_token)
        assert result is True

    def test_verify_refresh_token_invalid(self):
        """Test refresh token verification with invalid token."""
        invalid_token = "invalid_refresh_token_12345"
        result = self.auth_service.verify_refresh_token(invalid_token)
        assert result is False

    def test_refresh_access_token_success(self):
        """Test creating new access token with valid refresh token."""
        client_id = "pipol_client"
        refresh_token = self.auth_service.create_refresh_token(client_id)

        new_access_token = self.auth_service.refresh_access_token(refresh_token, client_id)

        assert new_access_token is not None
        assert isinstance(new_access_token, str)
        assert len(new_access_token) > 0

        # Verify the new token is valid
        payload = self.auth_service.verify_token(new_access_token)
        assert payload is not None
        assert payload["sub"] == client_id

    def test_refresh_access_token_invalid(self):
        """Test creating new access token with invalid refresh token."""
        client_id = "pipol_client"
        invalid_refresh_token = "invalid_token_12345"

        new_access_token = self.auth_service.refresh_access_token(invalid_refresh_token, client_id)

        assert new_access_token is None

    def test_revoke_refresh_token_success(self):
        """Test revoking a valid refresh token."""
        client_id = "pipol_client"
        refresh_token = self.auth_service.create_refresh_token(client_id)

        # Verify token exists
        assert self.auth_service.verify_refresh_token(refresh_token) is True

        # Revoke token
        result = self.auth_service.revoke_refresh_token(refresh_token)
        assert result is True

        # Verify token is no longer valid
        assert self.auth_service.verify_refresh_token(refresh_token) is False

    def test_revoke_refresh_token_invalid(self):
        """Test revoking an invalid refresh token."""
        invalid_token = "invalid_token_12345"
        result = self.auth_service.revoke_refresh_token(invalid_token)
        assert result is False

    def test_refresh_token_workflow(self):
        """Test complete refresh token workflow."""
        client_id = "pipol_client"

        # 1. Create refresh token
        refresh_token = self.auth_service.create_refresh_token(client_id)
        assert self.auth_service.verify_refresh_token(refresh_token) is True

        # 2. Use refresh token to get new access token
        new_access_token = self.auth_service.refresh_access_token(refresh_token, client_id)
        assert new_access_token is not None

        # 3. Verify new access token works
        payload = self.auth_service.verify_token(new_access_token)
        assert payload["sub"] == client_id

        # 4. Refresh token should still be valid (until revoked)
        assert self.auth_service.verify_refresh_token(refresh_token) is True
