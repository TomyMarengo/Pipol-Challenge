"""Unit tests for product repository."""

import pytest
from unittest.mock import Mock, patch
import pandas as pd
from app.repositories.product_repository import ProductRepository
from app.models.domain.products import ProductDataFilter


class TestProductRepository:
    """Test cases for ProductRepository."""

    @pytest.fixture
    def mock_csv_data(self):
        """Create mock CSV data."""
        return pd.DataFrame({
            'id_tie_fecha_valor': ['20240129', '20240129', '20240130'],
            'id_cli_cliente': [8, 8, 10],
            'desc_ga_sku_producto': ['K1010148001', 'SUCEI01', 'DWA2NGFT40IR'],
            'desc_ga_nombre_producto_1': ['TERMO STANLEY', 'ENDUIDO', 'SET PUNTAS DEWALT'],
            'desc_ga_marca_producto': ['STANLEY', 'CASABLANCA', 'DEWALT'],
            'desc_categoria_prod_principal': ['CAMPING', 'PINTURAS', 'HERRAMIENTAS'],
            'fc_agregado_carrito_cant': [1, 2, 0],
        })

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_load_data(self, mock_read_csv, mock_csv_data):
        """Test CSV data loading."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        df = repo._load_data()
        
        assert df is not None
        assert len(df) == 3
        mock_read_csv.assert_called_once()

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_get_all_with_pagination(self, mock_read_csv, mock_csv_data):
        """Test getting all products with pagination."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        products = repo.get_all(limit=2, offset=0)
        
        assert len(products) == 2
        assert products[0].desc_ga_marca_producto == 'STANLEY'

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_get_all_with_offset(self, mock_read_csv, mock_csv_data):
        """Test getting products with offset."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        products = repo.get_all(limit=2, offset=1)
        
        assert len(products) == 2
        assert products[0].desc_ga_marca_producto == 'CASABLANCA'

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_get_by_filter_brand(self, mock_read_csv, mock_csv_data):
        """Test filtering by brand."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        filter_params = ProductDataFilter(brand="STANLEY")
        products = repo.get_by_filter(filter_params)
        
        assert len(products) == 1
        assert products[0].desc_ga_marca_producto == 'STANLEY'

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_get_by_filter_date(self, mock_read_csv, mock_csv_data):
        """Test filtering by date."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        filter_params = ProductDataFilter(date="20240129")
        products = repo.get_by_filter(filter_params)
        
        assert len(products) == 2

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_count(self, mock_read_csv, mock_csv_data):
        """Test counting total records."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        count = repo.count()
        
        assert count == 3

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_get_brands(self, mock_read_csv, mock_csv_data):
        """Test getting unique brands."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        brands = repo.get_brands()
        
        assert len(brands) == 3
        assert 'STANLEY' in brands
        assert 'DEWALT' in brands

    @patch('app.repositories.product_repository.pd.read_csv')
    def test_get_categories(self, mock_read_csv, mock_csv_data):
        """Test getting unique categories."""
        mock_read_csv.return_value = mock_csv_data
        
        repo = ProductRepository()
        categories = repo.get_categories()
        
        assert len(categories) == 3
        assert 'CAMPING' in categories

