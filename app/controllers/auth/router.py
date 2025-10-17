"""Authentication API endpoints."""

from datetime import timedelta

from fastapi import APIRouter, HTTPException, status

from app.core.config import settings
from app.models.domain.auth import (
    ErrorResponse,
    RefreshTokenRequest,
    TokenRequest,
    TokenResponse,
)
from app.services.auth_service import auth_service

router = APIRouter(prefix="/auth", tags=["OAuth2 Authentication"])


@router.post(
    "/token",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid credentials"},
        400: {"model": ErrorResponse, "description": "Invalid grant type"},
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
    """,
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
                "error_description": "Only 'client_credentials' grant type is supported",
            },
        )

    # Verify client credentials
    if not auth_service.verify_client_credentials(request.client_id, request.client_secret):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error": "invalid_client", "error_description": "Invalid client credentials"},
        )

    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": request.client_id, "type": "client_credentials"},
        expires_delta=access_token_expires,
    )

    # Create refresh token
    refresh_token = auth_service.create_refresh_token(request.client_id)

    return TokenResponse(
        access_token=access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=refresh_token,
        refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS
        * 24
        * 60
        * 60,  # Convert days to seconds
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    responses={
        401: {"model": ErrorResponse, "description": "Invalid refresh token"},
        400: {"model": ErrorResponse, "description": "Invalid grant type"},
    },
    summary="Refresh access token",
    description="""
    Refresh Token Flow endpoint.
    
    This endpoint allows clients to obtain a new access token using a valid refresh token
    without having to re-authenticate with client credentials.
    
    **Steps to use:**
    1. Use a valid refresh token from a previous token response
    2. Send a POST request with grant_type='refresh_token'
    3. Receive a new access token (and new refresh token)
    
    **Note:** The old refresh token becomes invalid after use.
    """,
)
async def refresh_token(request: RefreshTokenRequest):
    """
    Get new JWT access token using refresh token.

    Implements OAuth 2.0 refresh token flow (RFC 6749).
    """
    # Validate grant type
    if request.grant_type != "refresh_token":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": "unsupported_grant_type",
                "error_description": "Only 'refresh_token' grant type is supported for this endpoint",
            },
        )

    # Create new access token using refresh token
    new_access_token = auth_service.refresh_access_token(request.refresh_token, request.client_id)

    if not new_access_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": "invalid_grant",
                "error_description": "Invalid or expired refresh token",
            },
        )

    # Revoke old refresh token and create new one
    auth_service.revoke_refresh_token(request.refresh_token)
    new_refresh_token = auth_service.create_refresh_token(request.client_id)

    return TokenResponse(
        access_token=new_access_token,
        token_type="bearer",
        expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        refresh_token=new_refresh_token,
        refresh_expires_in=settings.REFRESH_TOKEN_EXPIRE_DAYS * 24 * 60 * 60,
    )
