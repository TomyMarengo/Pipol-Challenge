"""Products business logic service."""

import re
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
        max_limit = 100
        validated_limit = min(max(1, limit), max_limit)  # Between 1 and 100
        validated_offset = max(0, offset)  # Non-negative

        return validated_limit, validated_offset

    def build_filter(
        self,
        date: Optional[str] = None,
        client_id: Optional[int] = None,
        brand: Optional[str] = None,
        sku: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50,
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

        # Sanitize string inputs to prevent injection attacks
        sanitized_date = self._sanitize_string_input(date) if date else None
        sanitized_brand = self._sanitize_string_input(brand) if brand else None
        sanitized_sku = self._sanitize_string_input(sku) if sku else None
        sanitized_category = self._sanitize_string_input(category) if category else None

        return ProductDataFilter(
            date=sanitized_date,
            client_id=client_id,
            brand=sanitized_brand,
            sku=sanitized_sku,
            category=sanitized_category,
            limit=validated_limit,
            offset=validated_offset,
        )


    def _sanitize_string_input(self, value: str) -> str:
        """
        Sanitize string inputs to prevent injection attacks.

        Args:
            value: Input string to sanitize

        Returns:
            Sanitized string
        """
        if not value:
            return value

        # Remove potentially dangerous SQL and XSS characters
        # First remove specific dangerous patterns
        dangerous_patterns = [
            r'[;\'"<>]',  # SQL injection and XSS characters
            r'--',        # SQL comments
            r'/\*',       # SQL block comments
            r'\*/',       # SQL block comments
            r'script|alert|eval|document|window',    # XSS functions and objects (case insensitive)
            r'DROP|INSERT|UPDATE|DELETE|SELECT|UNION|TABLE',  # SQL keywords (case insensitive)
        ]

        sanitized = value.strip()
        for pattern in dangerous_patterns:
            sanitized = re.sub(pattern, '', sanitized, flags=re.IGNORECASE)

        # Keep only alphanumeric, spaces, hyphens, underscores, dots, and safe punctuation
        sanitized = re.sub(r'[^\w\s\-_.,&()]+', '', sanitized)

        # Limit string length to prevent memory attacks
        max_length = 100
        if len(sanitized) > max_length:
            sanitized = sanitized[:max_length]

        return sanitized.strip()


# Singleton instance
products_service = ProductsService()
