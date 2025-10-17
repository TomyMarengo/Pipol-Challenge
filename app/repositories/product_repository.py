"""Repository for product data access from CSV."""

from pathlib import Path
from typing import List, Optional

import pandas as pd

from app.core.config import settings
from app.models.domain.products import ProductData, ProductDataFilter


class ProductRepository:
    """Repository for accessing product data from CSV file."""

    def __init__(self):
        """Initialize the repository and load CSV data."""
        self.csv_path = Path(settings.CSV_FILE_PATH)
        self._df: Optional[pd.DataFrame] = None

    def _load_data(self) -> pd.DataFrame:
        """Load CSV data into pandas DataFrame."""
        if self._df is None:
            try:
                # Define numeric columns upfront
                numeric_columns = [
                    "id_cli_cliente", "id_ga_vista", "id_ga_tipo_dispositivo", 
                    "id_ga_fuente_medio", "fc_agregado_carrito_cant", 
                    "fc_ingreso_producto_monto", "fc_retirado_carrito_cant", 
                    "fc_detalle_producto_cant", "fc_producto_cant", 
                    "fc_visualizaciones_pag_cant", "flag_pipol", "id_ga_producto"
                ]

                # Read CSV once with proper NaN handling
                self._df = pd.read_csv(
                    self.csv_path, 
                    na_values=['', 'nan', 'NaN', 'null'],
                    keep_default_na=True,
                    dtype=str  # Read all as strings first to avoid type issues
                )

                # Convert numeric columns efficiently (vectorized)
                for col in numeric_columns:
                    if col in self._df.columns:
                        # Only convert non-empty, non-'nan' strings to numeric
                        mask = (self._df[col].notna()) & (self._df[col] != 'nan') & (self._df[col] != '')
                        if mask.any():
                            self._df.loc[mask, col] = pd.to_numeric(self._df.loc[mask, col], errors='coerce')
                            # Replace any NaN results from failed conversions back to None
                            self._df[col] = self._df[col].where(pd.notnull(self._df[col]), None)
                        else:
                            # If all values are None/nan/empty, set the whole column to None
                            self._df[col] = None

                # Convert id_tie_fecha_valor to string if it exists
                if "id_tie_fecha_valor" in self._df.columns:
                    self._df["id_tie_fecha_valor"] = self._df["id_tie_fecha_valor"].astype(str)
                    # Replace 'nan' strings with None
                    self._df["id_tie_fecha_valor"] = self._df["id_tie_fecha_valor"].replace('nan', None)

                # Replace NaN values with None for Pydantic compatibility
                # Use where() method instead of fillna for better compatibility
                self._df = self._df.where(pd.notnull(self._df), None)

            except Exception as e:
                raise IOError(f"Error loading CSV file: {str(e)}") from e
        return self._df

    def get_all(self, limit: int = 100, offset: int = 0) -> List[ProductData]:
        """
        Get all product records with pagination.

        Args:
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of ProductData objects
        """
        df = self._load_data()

        # Apply pagination
        paginated_df = df.iloc[offset : offset + limit]

        # Convert to list of dictionaries
        records = paginated_df.to_dict("records")

        # Convert to ProductData objects (no cleaning needed - handled in _load_data)
        return [ProductData(**record) for record in records]

    def get_by_filter(self, filter_params: ProductDataFilter) -> List[ProductData]:
        """
        Get product records based on filter parameters.

        Args:
            filter_params: Filter parameters

        Returns:
            List of filtered ProductData objects
        """
        df = self._load_data()

        # Apply filters
        if filter_params.date:
            df = df[df["id_tie_fecha_valor"] == filter_params.date]

        if filter_params.client_id is not None:
            df = df[df["id_cli_cliente"] == filter_params.client_id]

        if filter_params.brand:
            df = df[
                df["desc_ga_marca_producto"].str.contains(filter_params.brand, case=False, na=False)
            ]

        if filter_params.sku:
            df = df[df["desc_ga_sku_producto"] == filter_params.sku]

        if filter_params.category:
            df = df[
                df["desc_categoria_prod_principal"].str.contains(
                    filter_params.category, case=False, na=False
                )
            ]

        # Apply pagination
        offset = filter_params.offset or 0
        limit = filter_params.limit or 100
        paginated_df = df.iloc[offset : offset + limit]

        # Convert to list of dictionaries
        records = paginated_df.to_dict("records")

        # Convert to ProductData objects (no cleaning needed - handled in _load_data)
        return [ProductData(**record) for record in records]

    def count(self) -> int:
        """Get total count of records."""
        df = self._load_data()
        return len(df)

    def get_brands(self) -> List[str]:
        """Get list of unique brands."""
        df = self._load_data()
        brands = df["desc_ga_marca_producto"].dropna().unique().tolist()
        return sorted([str(b) for b in brands if b != "No Aplica"])

    def get_categories(self) -> List[str]:
        """Get list of unique categories."""
        df = self._load_data()
        categories = df["desc_categoria_prod_principal"].dropna().unique().tolist()
        return sorted([str(c) for c in categories])


# Singleton instance
product_repository = ProductRepository()
