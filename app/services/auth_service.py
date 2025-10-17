"""Authentication service for OAuth2 client credentials flow."""

from datetime import datetime, timedelta
from typing import Optional, Dict, Set
from jose import JWTError, jwt
import secrets
from app.core.config import settings


class AuthService:
    """Service for handling OAuth2 authentication and JWT tokens."""
    
    def __init__(self):
        """Initialize the auth service with refresh token storage."""
        # In-memory storage for refresh tokens (in production, use Redis/Database)
        self._refresh_tokens: Set[str] = set()

    def verify_client_credentials(self, client_id: str, client_secret: str) -> bool:
        """
        Verify client credentials.
        
        Args:
            client_id: Client ID
            client_secret: Client secret
            
        Returns:
            True if credentials are valid, False otherwise
        """
        return (
            client_id == settings.CLIENT_ID and
            client_secret == settings.CLIENT_SECRET
        )

    def create_access_token(
        self,
        data: dict,
        expires_delta: Optional[timedelta] = None
    ) -> str:
        """
        Create a JWT access token.
        
        Args:
            data: Data to encode in the token
            expires_delta: Optional expiration time delta
            
        Returns:
            Encoded JWT token
        """
        to_encode = data.copy()
        
        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(
                minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
            )
        
        to_encode.update({
            "exp": expire,
            "iat": datetime.utcnow(),
            "jti": secrets.token_hex(16),  # JWT ID for uniqueness
        })
        
        encoded_jwt = jwt.encode(
            to_encode,
            settings.SECRET_KEY,
            algorithm=settings.ALGORITHM
        )
        
        return encoded_jwt

    def verify_token(self, token: str) -> Optional[dict]:
        """
        Verify and decode a JWT token.
        
        Args:
            token: JWT token to verify
            
        Returns:
            Decoded token data if valid, None otherwise
        """
        try:
            payload = jwt.decode(
                token,
                settings.SECRET_KEY,
                algorithms=[settings.ALGORITHM]
            )
            return payload
        except JWTError:
            return None

    def create_refresh_token(self, client_id: str) -> str:
        """
        Create a refresh token.
        
        Args:
            client_id: Client ID to associate with the refresh token
            
        Returns:
            Refresh token string
        """
        # Generate secure random token
        refresh_token = secrets.token_urlsafe(32)
        
        # Store in memory (in production, use Redis/Database with expiration)
        self._refresh_tokens.add(refresh_token)
        
        return refresh_token

    def verify_refresh_token(self, refresh_token: str) -> bool:
        """
        Verify if a refresh token is valid.
        
        Args:
            refresh_token: Refresh token to verify
            
        Returns:
            True if valid, False otherwise
        """
        return refresh_token in self._refresh_tokens

    def refresh_access_token(self, refresh_token: str, client_id: str) -> Optional[str]:
        """
        Create a new access token using a refresh token.
        
        Args:
            refresh_token: Valid refresh token
            client_id: Client ID
            
        Returns:
            New access token if refresh token is valid, None otherwise
        """
        if not self.verify_refresh_token(refresh_token):
            return None
        
        # Create new access token
        return self.create_access_token(
            data={"sub": client_id, "type": "client_credentials"}
        )

    def revoke_refresh_token(self, refresh_token: str) -> bool:
        """
        Revoke a refresh token.
        
        Args:
            refresh_token: Refresh token to revoke
            
        Returns:
            True if token was revoked, False if token didn't exist
        """
        if refresh_token in self._refresh_tokens:
            self._refresh_tokens.remove(refresh_token)
            return True
        return False


# Singleton instance
auth_service = AuthService()

