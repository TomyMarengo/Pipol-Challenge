"""Products business logic service."""

from typing import List, Optional

from app.models.domain.products import ProductData, ProductDataFilter
from app.repositories.product_repository import product_repository


class ProductsService:
    """Service for handling products business logic."""

    def __init__(self):
        """Initialize the products service."""
        self.repository = product_repository

    def get_all_products(self, limit: int = 100, offset: int = 0) -> List[ProductData]:
        """
        Get all products with pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of ProductData objects
        """
        return self.repository.get_all(limit=limit, offset=offset)

    def search_products(self, filter_params: ProductDataFilter) -> List[ProductData]:
        """
        Search products with filters.

        Args:
            filter_params: Filter parameters

        Returns:
            List of filtered ProductData objects
        """
        return self.repository.get_by_filter(filter_params)

    def get_available_brands(self) -> List[str]:
        """
        Get list of all unique brands.

        Returns:
            List of brand names sorted alphabetically
        """
        return self.repository.get_brands()

    def get_available_categories(self) -> List[str]:
        """
        Get list of all unique categories.

        Returns:
            List of category names sorted alphabetically
        """
        return self.repository.get_categories()

    def get_dataset_statistics(self) -> dict:
        """
        Get statistics about the dataset.

        Returns:
            Dictionary with dataset statistics
        """
        total_records = self.repository.count()
        brands = self.get_available_brands()
        categories = self.get_available_categories()

        return {
            "total_records": total_records,
            "brands_count": len(brands),
            "categories_count": len(categories),
        }

    def validate_pagination(self, limit: int, offset: int) -> tuple[int, int]:
        """
        Validate and normalize pagination parameters.

        Args:
            limit: Requested limit
            offset: Requested offset

        Returns:
            Tuple of (validated_limit, validated_offset)
        """
        # Ensure reasonable limits
        validated_limit = min(max(1, limit), 1000)  # Between 1 and 1000
        validated_offset = max(0, offset)  # Non-negative

        return validated_limit, validated_offset

    def build_filter(
        self,
        date: Optional[str] = None,
        client_id: Optional[int] = None,
        brand: Optional[str] = None,
        sku: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 100,
        offset: int = 0,
    ) -> ProductDataFilter:
        """
        Build a ProductDataFilter with validated parameters.

        Args:
            date: Filter by date
            client_id: Filter by client ID
            brand: Filter by brand
            sku: Filter by SKU
            category: Filter by category
            limit: Maximum records
            offset: Records to skip

        Returns:
            ProductDataFilter object
        """
        validated_limit, validated_offset = self.validate_pagination(limit, offset)

        return ProductDataFilter(
            date=date,
            client_id=client_id,
            brand=brand,
            sku=sku,
            category=category,
            limit=validated_limit,
            offset=validated_offset,
        )


# Singleton instance
products_service = ProductsService()
