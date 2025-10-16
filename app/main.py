"""Main FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.graphql.router import graphql_router
from app.api.auth.router import router as auth_router

app = FastAPI(
    title="Pipol Challenge API",
    description="API with GraphQL, OAuth2, and Swagger documentation",
    version="1.0.0",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(graphql_router, tags=["GraphQL Data Service"])


@app.get("/", tags=["Health"])
async def root():
    """Health check endpoint."""
    return {
        "status": "ok",
        "message": "Pipol Challenge API is running",
        "version": "1.0.0",
        "endpoints": {
            "graphql": "/graphql",
            "docs": "/docs",
            "auth": "/auth/token"
        }
    }

