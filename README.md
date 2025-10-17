# Pipol Challenge API

A comprehensive API built with FastAPI featuring GraphQL data access, OAuth 2.0 authentication with JWT, and complete Swagger documentation.

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [API Documentation](#api-documentation)
- [Usage Examples](#usage-examples)
- [Project Structure](#project-structure)
- [Configuration](#configuration)

## 🎯 Overview

This project implements three main services as part of a backend programming challenge:

1. **Data Service**: GraphQL API for querying product analytics data from a CSV file (25,864 records)
2. **Auth Service**: OAuth 2.0 client credentials flow with JWT token generation
3. **Docs Service**: Comprehensive Swagger/OpenAPI documentation

**Data Source**: The CSV file contains product analytics data with 244 unique brands and 384 categories.

## ✨ Features

### Data Service (GraphQL)
- ✅ GraphQL endpoint at `/graphql`
- ✅ Query products with pagination
- ✅ Advanced filtering (by date, brand, category, SKU, client)
- ✅ Get dataset statistics
- ✅ List available brands and categories
- ✅ Protected with JWT authentication
- ✅ Interactive GraphQL Playground

### Auth Service (OAuth 2.0)
- ✅ OAuth 2.0 Client Credentials flow
- ✅ JWT token generation and validation
- ✅ Refresh token support
- ✅ Endpoints: `/auth/token`, `/auth/refresh`
- ✅ Secure token-based authentication

### Docs Service (Swagger)
- ✅ Interactive Swagger UI at `/docs`
- ✅ ReDoc documentation at `/redoc`
- ✅ OpenAPI 3.0 specification
- ✅ Comprehensive examples and descriptions

## 🏗️ Architecture

The project follows **Clean Architecture** principles with clear separation of concerns:

```
app/
├── controllers/      # API layer (GraphQL, Auth endpoints)
├── models/          # Data models and schemas
│   ├── domain/      # Business domain models
│   └── graphql/     # GraphQL type definitions
├── repositories/    # Data access layer
├── services/        # Business logic
└── core/           # Configuration and dependencies
```

## 📦 Prerequisites

- **Docker** and **Docker Compose** (recommended)
- OR **Python 3.11+** (for local development)
- Git

## 🚀 Installation

### Option 1: Using Docker (Recommended)

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd pipol-challenge
   ```

2. **Ensure data.csv is in the project root**

3. **Build and run with Docker Compose:**
   ```bash
   docker-compose up --build
   ```

The API will be available at `http://localhost:8000`

### Option 2: Local Development

1. **Clone the repository:**
   ```bash
   git clone <your-repository-url>
   cd pipol-challenge
   ```

2. **Create a virtual environment:**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Create .env file** (or use the existing one):
   ```bash
   cp .env.example .env
   ```

5. **Run the application:**
   ```bash
   uvicorn app.main:app --reload
   ```

The API will be available at `http://localhost:8000`

## 🎮 Running the Application

### With Docker Compose

```bash
# Start the services
docker-compose up

# Start in detached mode
docker-compose up -d

# View logs
docker-compose logs -f

# Stop the services
docker-compose down
```

### Without Docker

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload

# Production mode
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once the application is running, access the documentation at:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
- **GraphQL Playground**: http://localhost:8000/graphql

## 💡 Usage Examples

### 1. Get an Access Token

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "pipol_client",
    "client_secret": "pipol_secret_2024"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 1800,
  "refresh_token": "pipol_client:abc123...",
  "refresh_expires_in": 604800
}
```

### 2. Query GraphQL Endpoint

**Using cURL:**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ searchProducts(filter: { limit: 5 }) { desc_ga_nombre_producto_1 desc_ga_marca_producto fc_agregado_carrito_cant } }"
  }'
```

**Using GraphQL Playground** (http://localhost:8000/graphql):

1. First, add your token to HTTP Headers:
```json
{
  "Authorization": "Bearer YOUR_TOKEN_HERE"
}
```

2. Then run queries:

**Query all products:**
```graphql
query {
  searchProducts(filter: { limit: 10, offset: 0 }) {
    desc_ga_nombre_producto_1
    desc_ga_marca_producto
    desc_categoria_prod_principal
    fc_agregado_carrito_cant
  }
}
```

**Search with filters:**
```graphql
query {
  searchProducts(filter: {
    brand: "STANLEY"
    limit: 5
  }) {
    desc_ga_nombre_producto_1
    desc_ga_marca_producto
    fc_agregado_carrito_cant
  }
}
```

**Get statistics:**
```graphql
query {
  stats {
    totalRecords
    brandsCount
    categoriesCount
  }
}
```

**Get available brands:**
```graphql
query {
  brands
}
```

**Get available categories:**
```graphql
query {
  categories
}
```

### 3. Complete Workflow Example

**Step 1: Get Token**
```bash
TOKEN=$(curl -s -X POST "http://localhost:8000/auth/token" \
  -H "Content-Type: application/json" \
  -d '{
    "grant_type": "client_credentials",
    "client_id": "pipol_client",
    "client_secret": "pipol_secret_2024"
  }' | jq -r '.access_token')

echo $TOKEN
```

**Step 2: Query GraphQL**
```bash
curl -X POST "http://localhost:8000/graphql" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "{ stats { totalRecords brandsCount categoriesCount } }"
  }' | jq
```

## 📁 Project Structure

```
pipol-challenge/
├── app/
│   ├── controllers/
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   └── router.py          # OAuth2 endpoints
│   │   └── products/
│   │       ├── __init__.py
│   │       ├── resolvers.py       # GraphQL query resolvers
│   │       └── router.py          # GraphQL router config
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py              # App configuration
│   │   └── dependencies.py        # FastAPI dependencies
│   ├── models/
│   │   ├── domain/
│   │   │   ├── __init__.py
│   │   │   ├── auth.py            # Auth models
│   │   │   └── products.py        # Product data models
│   │   └── graphql/
│   │       ├── __init__.py
│   │       └── product_types.py   # GraphQL type definitions
│   ├── repositories/
│   │   ├── __init__.py
│   │   └── product_repository.py  # CSV data access
│   ├── services/
│   │   ├── __init__.py
│   │   ├── auth_service.py        # JWT token service
│   │   └── products_service.py    # Product business logic
│   ├── __init__.py
│   └── main.py                    # FastAPI application
├── tests/                         # Unit and integration tests
├── data.csv                       # Product data
├── api-tests.http                 # HTTP test requests
├── pyproject.toml                 # Linting configuration
├── pytest.ini                     # Test configuration
├── .env                           # Environment variables
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

## 🔐 Default Credentials

For testing purposes, the following credentials are configured:

- **Client ID**: `pipol_client`
- **Client Secret**: `pipol_secret_2024`

⚠️ **Security Note**: In production, use strong, unique credentials and store them securely using environment variables or secrets management systems.

## 🔧 Configuration

Environment variables can be configured in the `.env` file:

```env
# Application Settings
APP_NAME="Pipol Challenge API"
APP_VERSION="1.0.0"
DEBUG=True

# Server Settings
HOST=0.0.0.0
PORT=8000

# JWT Settings
SECRET_KEY=your-secret-key-here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OAuth2 Client Credentials
CLIENT_ID=pipol_client
CLIENT_SECRET=pipol_secret_2024

# CSV Data
CSV_FILE_PATH=data.csv
```
