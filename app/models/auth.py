"""Authentication models."""

from pydantic import BaseModel, Field


class TokenRequest(BaseModel):
    """OAuth2 client credentials token request."""
    
    grant_type: str = Field(
        ...,
        description="OAuth2 grant type (must be 'client_credentials')"
    )
    client_id: str = Field(..., description="Client ID")
    client_secret: str = Field(..., description="Client secret")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "grant_type": "client_credentials",
                "client_id": "pipol_client",
                "client_secret": "pipol_secret_2024"
            }
        }


class TokenResponse(BaseModel):
    """OAuth2 token response."""
    
    access_token: str = Field(..., description="JWT access token")
    token_type: str = Field(default="bearer", description="Token type")
    expires_in: int = Field(..., description="Token expiration time in seconds")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "expires_in": 1800
            }
        }


class ErrorResponse(BaseModel):
    """OAuth2 error response."""
    
    error: str = Field(..., description="Error code")
    error_description: str = Field(..., description="Error description")

    class Config:
        """Pydantic configuration."""
        json_schema_extra = {
            "example": {
                "error": "invalid_client",
                "error_description": "Invalid client credentials"
            }
        }

