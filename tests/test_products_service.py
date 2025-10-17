"""Unit tests for products service."""

from unittest.mock import Mock

from app.models.domain.products import ProductData, ProductDataFilter
from app.services.products_service import ProductsService


class TestProductsService:
    """Test cases for ProductsService."""

    def setup_method(self):
        """Set up test instance."""
        self.service = ProductsService()

    def test_get_all_products(self):
        """Test getting all products."""
        # Mock the repository attribute
        mock_repo = Mock()
        mock_products = [
            ProductData(desc_ga_nombre_producto_1="Product 1"),
            ProductData(desc_ga_nombre_producto_1="Product 2"),
        ]
        mock_repo.get_all.return_value = mock_products
        self.service.repository = mock_repo

        # Call service method
        result = self.service.get_all_products(limit=10, offset=0)

        # Verify repository was called correctly
        mock_repo.get_all.assert_called_once_with(limit=10, offset=0)

        # Verify result
        assert result == mock_products
        assert len(result) == 2

    def test_search_products(self):
        """Test searching products with filters."""
        # Mock the repository attribute
        mock_repo = Mock()
        mock_products = [ProductData(desc_ga_marca_producto="STANLEY")]
        mock_repo.get_by_filter.return_value = mock_products
        self.service.repository = mock_repo

        # Create filter
        filter_params = ProductDataFilter(brand="STANLEY", limit=5)

        # Call service method
        result = self.service.search_products(filter_params)

        # Verify repository was called correctly
        mock_repo.get_by_filter.assert_called_once_with(filter_params)

        # Verify result
        assert result == mock_products

    def test_get_available_brands(self):
        """Test getting available brands."""
        # Mock the repository attribute
        mock_repo = Mock()
        mock_brands = ["STANLEY", "DEWALT", "CASABLANCA"]
        mock_repo.get_brands.return_value = mock_brands
        self.service.repository = mock_repo

        # Call service method
        result = self.service.get_available_brands()

        # Verify repository was called
        mock_repo.get_brands.assert_called_once()

        # Verify result
        assert result == mock_brands

    def test_get_available_categories(self):
        """Test getting available categories."""
        # Mock the repository attribute
        mock_repo = Mock()
        mock_categories = ["CAMPING", "HERRAMIENTAS", "PINTURAS"]
        mock_repo.get_categories.return_value = mock_categories
        self.service.repository = mock_repo

        # Call service method
        result = self.service.get_available_categories()

        # Verify repository was called
        mock_repo.get_categories.assert_called_once()

        # Verify result
        assert result == mock_categories

    def test_get_dataset_statistics(self):
        """Test getting dataset statistics."""
        # Mock the repository attribute
        mock_repo = Mock()
        mock_repo.count.return_value = 25864
        mock_repo.get_brands.return_value = ["Brand1", "Brand2", "Brand3"]
        mock_repo.get_categories.return_value = ["Cat1", "Cat2"]
        self.service.repository = mock_repo

        # Call service method
        result = self.service.get_dataset_statistics()

        # Verify repository calls
        mock_repo.count.assert_called_once()
        mock_repo.get_brands.assert_called_once()
        mock_repo.get_categories.assert_called_once()

        # Verify result
        expected = {"total_records": 25864, "brands_count": 3, "categories_count": 2}
        assert result == expected

    def test_validate_pagination_normal(self):
        """Test pagination validation with normal values."""
        limit, offset = self.service.validate_pagination(10, 5)
        assert limit == 10
        assert offset == 5

    def test_validate_pagination_limits(self):
        """Test pagination validation with edge cases."""
        # Test minimum limits
        limit, offset = self.service.validate_pagination(0, -5)
        assert limit == 1  # Minimum is 1
        assert offset == 0  # Minimum is 0

        # Test maximum limits
        limit, offset = self.service.validate_pagination(2000, 100)
        assert limit == 1000  # Maximum is 1000
        assert offset == 100  # Offset is preserved

    def test_build_filter_all_params(self):
        """Test building filter with all parameters."""
        filter_obj = self.service.build_filter(
            date="20240129",
            client_id=8,
            brand="STANLEY",
            sku="K1010148001",
            category="CAMPING",
            limit=50,
            offset=10,
        )

        assert filter_obj.date == "20240129"
        assert filter_obj.client_id == 8
        assert filter_obj.brand == "STANLEY"
        assert filter_obj.sku == "K1010148001"
        assert filter_obj.category == "CAMPING"
        assert filter_obj.limit == 50
        assert filter_obj.offset == 10

    def test_build_filter_minimal_params(self):
        """Test building filter with minimal parameters."""
        filter_obj = self.service.build_filter()

        assert filter_obj.date is None
        assert filter_obj.client_id is None
        assert filter_obj.brand is None
        assert filter_obj.sku is None
        assert filter_obj.category is None
        assert filter_obj.limit == 100  # Default
        assert filter_obj.offset == 0  # Default

    def test_build_filter_with_validation(self):
        """Test building filter with validation applied."""
        filter_obj = self.service.build_filter(
            limit=2000, offset=-10  # Should be capped at 1000  # Should be set to 0
        )

        assert filter_obj.limit == 1000
        assert filter_obj.offset == 0

    def test_service_singleton(self):
        """Test that service uses singleton pattern."""
        from app.services.products_service import products_service

        # Should be the same instance
        assert products_service is not None
        assert isinstance(products_service, ProductsService)
