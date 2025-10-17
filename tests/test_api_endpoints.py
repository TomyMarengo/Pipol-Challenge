"""Integration tests for API endpoints."""

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
                "client_secret": "pipol_secret_2024",
            },
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
                "client_secret": "wrong_secret",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_get_token_invalid_grant_type(self, client):
        """Test token generation with invalid grant type."""
        response = client.post(
            "/auth/token",
            json={
                "grant_type": "password",
                "client_id": "pipol_client",
                "client_secret": "pipol_secret_2024",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST


class TestRefreshTokenEndpoint:
    """Test cases for refresh token endpoint."""

    def test_refresh_token_success(self, client):
        """Test successful token refresh."""
        # First, get a token with refresh token
        token_response = client.post(
            "/auth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": "pipol_client",
                "client_secret": "pipol_secret_2024",
            },
        )

        assert token_response.status_code == status.HTTP_200_OK
        token_data = token_response.json()
        refresh_token = token_data["refresh_token"]

        # Now use refresh token to get new access token
        response = client.post(
            "/auth/refresh",
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": "pipol_client",
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"
        assert "expires_in" in data
        assert "refresh_expires_in" in data

    def test_refresh_token_invalid_token(self, client):
        """Test refresh with invalid refresh token."""
        response = client.post(
            "/auth/refresh",
            json={
                "grant_type": "refresh_token",
                "refresh_token": "invalid_refresh_token_12345",
                "client_id": "pipol_client",
            },
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_refresh_token_invalid_grant_type(self, client):
        """Test refresh with invalid grant type."""
        response = client.post(
            "/auth/refresh",
            json={
                "grant_type": "client_credentials",
                "refresh_token": "some_token",
                "client_id": "pipol_client",
            },
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_refresh_token_missing_fields(self, client):
        """Test refresh with missing required fields."""
        response = client.post(
            "/auth/refresh",
            json={
                "grant_type": "refresh_token",
                "client_id": "pipol_client",
                # Missing refresh_token
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    def test_refresh_token_workflow(self, client):
        """Test complete refresh token workflow."""
        # 1. Get initial token
        token_response = client.post(
            "/auth/token",
            json={
                "grant_type": "client_credentials",
                "client_id": "pipol_client",
                "client_secret": "pipol_secret_2024",
            },
        )

        token_data = token_response.json()
        original_access = token_data["access_token"]
        refresh_token = token_data["refresh_token"]

        # 2. Use refresh token to get new access token
        refresh_response = client.post(
            "/auth/refresh",
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,
                "client_id": "pipol_client",
            },
        )

        assert refresh_response.status_code == status.HTTP_200_OK
        new_token_data = refresh_response.json()
        new_access = new_token_data["access_token"]
        new_refresh = new_token_data["refresh_token"]

        # 3. Verify we got new tokens
        assert new_access != original_access
        assert new_refresh != refresh_token

        # 4. Verify new access token works with GraphQL
        graphql_response = client.post(
            "/graphql",
            headers={"Authorization": f"Bearer {new_access}"},
            json={"query": "{ stats { totalRecords } }"},
        )
        assert graphql_response.status_code == status.HTTP_200_OK

        # 5. Verify old refresh token is revoked (should fail)
        old_refresh_response = client.post(
            "/auth/refresh",
            json={
                "grant_type": "refresh_token",
                "refresh_token": refresh_token,  # Old token
                "client_id": "pipol_client",
            },
        )
        assert old_refresh_response.status_code == status.HTTP_401_UNAUTHORIZED


class TestGraphQLEndpoint:
    """Test cases for GraphQL endpoint."""

    def test_graphql_without_auth(self, client):
        """Test GraphQL access without authentication."""
        response = client.post("/graphql", json={"query": "{ stats { totalRecords } }"})

        # Should return 403 Forbidden or 401 Unauthorized
        assert response.status_code in [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN]

    def test_graphql_with_invalid_token(self, client):
        """Test GraphQL access with invalid token."""
        headers = {"Authorization": "Bearer invalid_token_here"}
        response = client.post(
            "/graphql", headers=headers, json={"query": "{ stats { totalRecords } }"}
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
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "stats" in data["data"]
        assert "totalRecords" in data["data"]["stats"]

    def test_graphql_brands_query(self, client, auth_headers):
        """Test GraphQL brands query with authentication."""
        response = client.post("/graphql", headers=auth_headers, json={"query": "{ brands }"})

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
                        searchProducts(filters: { limit: 5, offset: 0 }) {
                            descGaNombreProducto1
                            descGaMarcaProducto
                        }
                    }
                """
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "searchProducts" in data["data"]
        assert isinstance(data["data"]["searchProducts"], list)

    def test_graphql_search_products_query(self, client, auth_headers):
        """Test GraphQL search products with filter."""
        response = client.post(
            "/graphql",
            headers=auth_headers,
            json={
                "query": """
                    query {
                        searchProducts(filters: { limit: 5 }) {
                            descGaNombreProducto1
                            descGaMarcaProducto
                        }
                    }
                """
            },
        )

        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "data" in data
        assert "searchProducts" in data["data"]
