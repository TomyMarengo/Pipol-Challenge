"""Authentication API endpoints."""

from fastapi import APIRouter, HTTPException, status
from datetime import timedelta
from app.models.domain.auth import TokenRequest, TokenResponse, ErrorResponse
from app.services.auth_service import auth_service
from app.core.config import settings

router = APIRouter(prefix="/auth", tags=["OAuth2 Authentication"])


@router.post(
    "/token",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        400: {"model": ErrorResponse, "description": "Invalid grant type"}
    },
    summary="Get access token",
    description="""
    OAuth 2.0 Client Credentials Flow endpoint.
    
    This endpoint implements the OAuth 2.0 client credentials grant type to obtain
    an access token. The token is a JWT that must be included in the Authorization
    header as a Bearer token for authenticated requests to the GraphQL endpoint.
    
    **Steps to use:**
    1. Send a POST request with your client_id and client_secret
    2. Receive a JWT access token
    3. Use the token in GraphQL requests: `Authorization: Bearer <token>`
    
    **Default credentials for testing:**
    - client_id: `pipol_client`
    - client_secret: `pipol_secret_2024`
    """
)
async def get_token(request: TokenRequest):
    """
    Get JWT access token using client credentials.
    
    Implements OAuth 2.0 client credentials flow (RFC 6749).
    """
    # Validate grant type
    if request.grant_type != "client_credentials":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "unsupported_grant_type",
                "error_description": "Only 'client_credentials' grant type is supported"
            }
        )
    
    # Verify client credentials
    if not auth_service.verify_client_credentials(request.client_id, request.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_client",
                "error_description": "Invalid client credentials"
            }
        )
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": request.client_id, "type": "client_credentials"},
        expires_delta=access_token_expires
    )
    
    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    )

