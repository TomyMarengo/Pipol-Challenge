#!/usr/bin/env python
"""Test all endpoints running in Docker container."""

import requests
import json
import time

base_url = "http://localhost:8000"

def test_endpoint(name, func):
    """Helper to run and display test results."""
    print(f"\n{'='*80}")
    print(f"TEST: {name}")
    print('='*80)
    try:
        func()
        print("✅ PASSED")
    except AssertionError as e:
        print(f"❌ FAILED: {e}")
    except Exception as e:
        print(f"⚠️  ERROR: {e}")

def test_health():
    """Test 1: Health check endpoint"""
    response = requests.get(f"{base_url}/")
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert data["status"] == "ok", "Status should be ok"

def test_auth_success():
    """Test 2: Get OAuth token with valid credentials"""
    response = requests.post(
        f"{base_url}/auth/token",
        json={
            "grant_type": "client_credentials",
            "client_id": "pipol_client",
            "client_secret": "pipol_secret_2024"
        }
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    print(f"Token received: {data['access_token'][:50]}...")
    assert "access_token" in data, "Should have access_token"
    assert data["token_type"] == "bearer", "Token type should be bearer"
    return data["access_token"]

def test_auth_invalid():
    """Test 3: OAuth with invalid credentials (should fail)"""
    response = requests.post(
        f"{base_url}/auth/token",
        json={
            "grant_type": "client_credentials",
            "client_id": "wrong",
            "client_secret": "wrong"
        }
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 401, "Should return 401 Unauthorized"
    print("Correctly rejected invalid credentials")

def test_graphql_no_auth():
    """Test 4: GraphQL without authentication (should fail)"""
    response = requests.post(
        f"{base_url}/graphql",
        json={"query": "{ stats { totalRecords } }"}
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 403, "Should return 403 Forbidden"
    print("Correctly blocked unauthenticated request")

def test_graphql_invalid_token():
    """Test 5: GraphQL with invalid token (should fail)"""
    response = requests.post(
        f"{base_url}/graphql",
        headers={"Authorization": "Bearer invalid_token"},
        json={"query": "{ stats { totalRecords } }"}
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 401, "Should return 401 Unauthorized"
    print("Correctly rejected invalid token")

def test_graphql_stats(token):
    """Test 6: GraphQL stats query with authentication"""
    response = requests.post(
        f"{base_url}/graphql",
        headers={"Authorization": f"Bearer {token}"},
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
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    assert "data" in data, "Should have data field"
    assert "stats" in data["data"], "Should have stats"

def test_graphql_brands(token):
    """Test 7: GraphQL brands query"""
    response = requests.post(
        f"{base_url}/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "{ brands }"}
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    brands = data.get("data", {}).get("brands", [])
    print(f"Found {len(brands)} brands")
    print(f"Sample brands: {brands[:5]}")

def test_graphql_categories(token):
    """Test 8: GraphQL categories query"""
    response = requests.post(
        f"{base_url}/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={"query": "{ categories }"}
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    categories = data.get("data", {}).get("categories", [])
    print(f"Found {len(categories)} categories")
    print(f"Sample categories: {categories[:3]}")

def test_graphql_products(token):
    """Test 9: GraphQL products query with pagination"""
    response = requests.post(
        f"{base_url}/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": """
                query {
                    products(limit: 3, offset: 0) {
                        descGaNombreProducto1
                        descGaMarcaProducto
                        fcAgregadoCarritoCant
                    }
                }
            """
        }
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")
    products = data.get("data", {}).get("products", [])
    print(f"Returned {len(products)} products")

def test_graphql_search(token):
    """Test 10: GraphQL search with filters"""
    response = requests.post(
        f"{base_url}/graphql",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "query": """
                query {
                    searchProducts(filter: { brand: "STANLEY", limit: 2 }) {
                        descGaNombreProducto1
                        descGaMarcaProducto
                    }
                }
            """
        }
    )
    print(f"Status Code: {response.status_code}")
    assert response.status_code == 200, "Should return 200"
    data = response.json()
    print(f"Response: {json.dumps(data, indent=2)}")

# Main execution
if __name__ == "__main__":
    print("\n" + "="*80)
    print("TESTING PIPOL CHALLENGE API IN DOCKER")
    print("="*80)
    
    # Wait for container to be fully ready
    print("\nWaiting for container to be ready...")
    time.sleep(3)
    
    # Run tests
    test_endpoint("Health Check", test_health)
    
    token = None
    def get_token():
        global token
        token = test_auth_success()
    test_endpoint("OAuth2 - Valid Credentials", get_token)
    
    test_endpoint("OAuth2 - Invalid Credentials", test_auth_invalid)
    test_endpoint("GraphQL - No Authentication", test_graphql_no_auth)
    test_endpoint("GraphQL - Invalid Token", test_graphql_invalid_token)
    
    if token:
        test_endpoint("GraphQL - Stats Query", lambda: test_graphql_stats(token))
        test_endpoint("GraphQL - Brands Query", lambda: test_graphql_brands(token))
        test_endpoint("GraphQL - Categories Query", lambda: test_graphql_categories(token))
        test_endpoint("GraphQL - Products Query", lambda: test_graphql_products(token))
        test_endpoint("GraphQL - Search Query", lambda: test_graphql_search(token))
    
    print("\n" + "="*80)
    print("✨ ALL TESTS COMPLETE!")
    print("="*80)
    print("\n📚 Access the API documentation at:")
    print(f"   - Swagger UI: {base_url}/docs")
    print(f"   - ReDoc: {base_url}/redoc")
    print(f"   - GraphQL Playground: {base_url}/graphql")
    print("\n🐳 Docker container is running!")
    print("   - View logs: docker-compose logs -f")
    print("   - Stop: docker-compose down")
    print("="*80 + "\n")

