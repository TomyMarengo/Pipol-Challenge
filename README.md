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

This project implements **3 services with 3+ endpoints** as required by the backend programming challenge:

### **📊 Service 1: Data Service**

- **Endpoint**: `POST /graphql`
- **Purpose**: GraphQL API for querying product analytics data from CSV file (25,864 records)
- **Features**: Pagination, filtering, statistics, brands/categories listing
- **Authentication**: Required (JWT Bearer token)

### **🔐 Service 2: Auth Service**

- **Endpoints**: `POST /auth/token`, `POST /auth/refresh`
- **Purpose**: OAuth 2.0 client credentials flow with JWT token generation
- **Features**: Access tokens, refresh tokens, secure authentication

### **📚 Service 3: Docs Service**

- **Endpoints**: `GET /docs`, `GET /redoc`, `GET /openapi.json`
- **Purpose**: Interactive API documentation with Swagger/OpenAPI 3.0
- **Features**: Interactive testing, request examples, schema definitions

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
   git clone https://github.com/TomyMarengo/Pipol-Challenge
   cd Pipol-Challenge
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
   git clone https://github.com/TomyMarengo/Pipol-Challenge
   cd Pipol-Challenge
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
    "query": "{ searchProducts(filters: { limit: 5 }) { desc_ga_nombre_producto_1 desc_ga_marca_producto fc_agregado_carrito_cant } }"
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
  searchProducts(filters: { limit: 10, offset: 0 }) {
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
  searchProducts(filters: { brand: "STANLEY", limit: 5 }) {
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
