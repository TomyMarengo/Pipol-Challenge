"""Integration tests for API endpoints."""

import pytest
from fastapi import status


class TestHealthEndpoint:
    """Test cases for health check endpoint."""

    def test_health_check(self, client):
        """Test health check endpoint."""
        response = client.get("/")
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["status"] == "ok"
        assert "endpoints" in data


class TestAuthEndpoint:
    """Test cases for authentication endpoint."""

    def test_get_token_success(self, client):
        """Test successful token generation."""
        response = client.post(
            "/auth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": "pipol_client",
                "client_secret": "pipol_secret_2024"
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data

    def test_get_token_invalid_credentials(self, client):
        """Test token generation with invalid credentials."""
        response = client.post(
            "/auth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": "wrong_client",
                "client_secret": "wrong_secret"
            }
        )
        
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_token_invalid_grant_type(self, client):
        """Test token generation with invalid grant type."""
        response = client.post(
            "/auth/token",
            json={
                "grant_type": "password",
                "client_id": "pipol_client",
                "client_secret": "pipol_secret_2024"
            }
        )
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestGraphQLEndpoint:
    """Test cases for GraphQL endpoint."""

    def test_graphql_without_auth(self, client):
        """Test GraphQL access without authentication."""
        response = client.post(
            "/graphql",
            json={"query": "{ stats { totalRecords } }"}
        )
        
        # Should return 403 Forbidden or 401 Unauthorized
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_graphql_with_invalid_token(self, client):
        """Test GraphQL access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.post(
            "/graphql",
            headers=headers,
            json={"query": "{ stats { totalRecords } }"}
        )
        
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_graphql_stats_query(self, client, auth_headers):
        """Test GraphQL stats query with authentication."""
        response = client.post(
            "/graphql",
            headers=auth_headers,
            json={
                "query": """
                    query {
                        stats {
                            totalRecords
                            brandsCount
                            categoriesCount
                        }
                    }
                """
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "stats" in data["data"]
        assert "totalRecords" in data["data"]["stats"]

    def test_graphql_brands_query(self, client, auth_headers):
        """Test GraphQL brands query with authentication."""
        response = client.post(
            "/graphql",
            headers=auth_headers,
            json={"query": "{ brands }"}
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "brands" in data["data"]
        assert isinstance(data["data"]["brands"], list)

    def test_graphql_products_query(self, client, auth_headers):
        """Test GraphQL products query with pagination."""
        response = client.post(
            "/graphql",
            headers=auth_headers,
            json={
                "query": """
                    query {
                        products(limit: 5, offset: 0) {
                            descGaNombreProducto1
                            descGaMarcaProducto
                        }
                    }
                """
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "products" in data["data"]
        assert isinstance(data["data"]["products"], list)

    def test_graphql_search_products_query(self, client, auth_headers):
        """Test GraphQL search products with filter."""
        response = client.post(
            "/graphql",
            headers=auth_headers,
            json={
                "query": """
                    query {
                        searchProducts(filter: { limit: 5 }) {
                            descGaNombreProducto1
                            descGaMarcaProducto
                        }
                    }
                """
            }
        )
        
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "searchProducts" in data["data"]

