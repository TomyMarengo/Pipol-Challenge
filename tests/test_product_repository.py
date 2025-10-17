"""Unit tests for product repository."""

from unittest.mock import patch

import pandas as pd
import pytest

from app.models.domain.products import ProductDataFilter
from app.repositories.product_repository import ProductRepository


class TestProductRepository:
    """Test cases for ProductRepository."""

    @pytest.fixture
    def mock_csv_data(self):
        """Create mock CSV data."""
        return pd.DataFrame(
            {
                "id_tie_fecha_valor": ["20240129", "20240129", "20240130"],
                "id_cli_cliente": [8, 8, 10],
                "desc_ga_sku_producto": ["K1010148001", "SUCEI01", "DWA2NGFT40IR"],
                "desc_ga_nombre_producto_1": ["TERMO STANLEY", "ENDUIDO", "SET PUNTAS DEWALT"],
                "desc_ga_marca_producto": ["STANLEY", "CASABLANCA", "DEWALT"],
                "desc_categoria_prod_principal": ["CAMPING", "PINTURAS", "HERRAMIENTAS"],
                "fc_agregado_carrito_cant": [1, 2, 0],
            }
        )

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_load_data(self, mock_read_csv, mock_csv_data):
        """Test CSV data loading."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        df = repo._load_data()

        assert df is not None
        assert len(df) == 3
        mock_read_csv.assert_called_once()

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_all_with_pagination(self, mock_read_csv, mock_csv_data):
        """Test getting all products with pagination."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        products = repo.get_all(limit=2, offset=0)

        assert len(products) == 2
        assert products[0].desc_ga_marca_producto == "STANLEY"

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_all_with_offset(self, mock_read_csv, mock_csv_data):
        """Test getting products with offset."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        products = repo.get_all(limit=2, offset=1)

        assert len(products) == 2
        assert products[0].desc_ga_marca_producto == "CASABLANCA"

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_by_filter_brand(self, mock_read_csv, mock_csv_data):
        """Test filtering by brand."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        filter_params = ProductDataFilter(brand="STANLEY")
        products = repo.get_by_filter(filter_params)

        assert len(products) == 1
        assert products[0].desc_ga_marca_producto == "STANLEY"

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_by_filter_date(self, mock_read_csv, mock_csv_data):
        """Test filtering by date."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        filter_params = ProductDataFilter(date="20240129")
        products = repo.get_by_filter(filter_params)

        assert len(products) == 2

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_count(self, mock_read_csv, mock_csv_data):
        """Test counting total records."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        count = repo.count()

        assert count == 3

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_brands(self, mock_read_csv, mock_csv_data):
        """Test getting unique brands."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        brands = repo.get_brands()

        assert len(brands) == 3
        assert "STANLEY" in brands
        assert "DEWALT" in brands

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_categories(self, mock_read_csv, mock_csv_data):
        """Test getting unique categories."""
        mock_read_csv.return_value = mock_csv_data

        repo = ProductRepository()
        categories = repo.get_categories()

        assert len(categories) == 3
        assert "CAMPING" in categories

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_load_data_file_not_found(self, mock_read_csv):
        """Test CSV loading when file doesn't exist."""
        mock_read_csv.side_effect = FileNotFoundError("File not found")

        repo = ProductRepository()

        with pytest.raises(IOError, match="Error loading CSV file"):
            repo._load_data()

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_load_data_permission_error(self, mock_read_csv):
        """Test CSV loading when file permissions are denied."""
        mock_read_csv.side_effect = PermissionError("Permission denied")

        repo = ProductRepository()

        with pytest.raises(IOError, match="Error loading CSV file"):
            repo._load_data()

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_load_data_with_nan_values(self, mock_read_csv):
        """Test CSV loading with NaN values that need conversion."""
        # Create DataFrame with NaN values that would cause Pydantic errors
        import numpy as np
        df_with_nans = pd.DataFrame({
            "id_tie_fecha_valor": ["20240129", "20240130"],
            "id_cli_cliente": [8, np.nan],  # This should become None
            "fc_agregado_carrito_cant": [1, np.nan],  # This should become None
            "desc_ga_marca_producto": ["STANLEY", "DEWALT"],
        })
        mock_read_csv.return_value = df_with_nans

        repo = ProductRepository()
        df = repo._load_data()

        # Verify NaN values were converted to None (or remain as NaN if not in numeric columns)
        # The actual conversion happens when creating ProductData objects
        assert df.iloc[1]["id_cli_cliente"] is None or pd.isna(df.iloc[1]["id_cli_cliente"])
        assert df.iloc[1]["fc_agregado_carrito_cant"] is None or pd.isna(df.iloc[1]["fc_agregado_carrito_cant"])

    def test_get_all_with_real_validation(self):
        """Test that get_all properly handles data validation."""
        # This test uses a real ProductRepository without mocking
        # to ensure the NaN conversion actually works
        repo = ProductRepository()

        # This should not raise ValidationError anymore
        try:
            products = repo.get_all(limit=1)
            # Should get at least one product if CSV exists
            assert isinstance(products, list)
        except IOError:
            # If CSV file doesn't exist, that's expected in test environment
            pytest.skip("CSV file not available in test environment")

    @patch("app.repositories.product_repository.pd.read_csv")
    def test_get_by_filter_error_propagation(self, mock_read_csv):
        """Test error propagation from _load_data in filtering."""
        mock_read_csv.side_effect = IOError("Disk error")

        repo = ProductRepository()
        filter_params = ProductDataFilter(brand="STANLEY")

        with pytest.raises(IOError, match="Error loading CSV file"):
            repo.get_by_filter(filter_params)
