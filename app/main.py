"""Main FastAPI application entry point."""

import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.controllers.auth.router import router as auth_router
from app.controllers.products.router import graphql_router

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

app = FastAPI(
    title="Pipol Challenge API",
    description="""
# Pipol Challenge API

This API provides access to product analytics data from a CSV file through multiple services:

## Services

### 1. 📊 Data Service (GraphQL)
- **Endpoint:** `/graphql`
- **Authentication:** Required (Bearer JWT token)
- **Description:** GraphQL API for querying product analytics data
- **Features:**
  - Query products with pagination
  - Filter by date, brand, category, SKU, client
  - Get statistics (total records, brands, categories)
  - List available brands and categories

### 2. 🔐 Auth Service (OAuth 2.0)
- **Endpoint:** `/auth/token`
- **Description:** OAuth 2.0 Client Credentials flow for obtaining JWT tokens
- **Grant Type:** `client_credentials`
- **Default Credentials:**
  - Client ID: `pipol_client`
  - Client Secret: `pipol_secret_2024`

### 3. 📚 Docs Service (Swagger/OpenAPI)
- **Swagger UI:** `/docs` (this page)
- **ReDoc:** `/redoc`
- **OpenAPI JSON:** `/openapi.json`

## How to Use

1. **Get an access token:**
   - Use the `/auth/token` endpoint with your client credentials
   - You'll receive a JWT token

2. **Access GraphQL:**
   - Go to `/graphql` with the token in the Authorization header
   - Format: `Authorization: Bearer <your_token>`
   - Use the GraphQL Playground to explore queries

3. **Available GraphQL Queries:**
   ```graphql
   # Get products with pagination
   query {
     searchProducts(filter: { limit: 10, offset: 0 }) {
       desc_ga_nombre_producto_1
       desc_ga_marca_producto
       fc_agregado_carrito_cant
     }
   }
   
   # Search with filters
   query {
     searchProducts(filter: { brand: "STANLEY", limit: 5 }) {
       desc_ga_nombre_producto_1
       desc_ga_marca_producto
     }
   }
   
   # Get statistics
   query {
     stats {
       totalRecords
       brandsCount
       categoriesCount
     }
   }
   ```

## Technology Stack
- **Framework:** FastAPI
- **GraphQL:** Strawberry GraphQL
- **Authentication:** OAuth 2.0 + JWT
- **Data:** Pandas (CSV processing)
    """,
    version="1.0.0",
    contact={
        "name": "Pipol Challenge",
        "url": "https://github.com",
    },
    license_info={
        "name": "MIT",
    },
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
        "endpoints": {"graphql": "/graphql", "docs": "/docs", "auth": "/auth/token"},
    }
