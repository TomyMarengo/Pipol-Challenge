"""GraphQL query resolvers."""

import strawberry
import logging
from typing import List, Optional
from app.models.graphql.product_types import ProductDataType, ProductFilterInput, StatsType
from app.repositories.product_repository import product_repository
from app.models.domain.products import ProductDataFilter

logger = logging.getLogger(__name__)


def product_data_to_graphql(product_data) -> ProductDataType:
    """Convert ProductData model to GraphQL type."""
    return ProductDataType(
        id_tie_fecha_valor=product_data.id_tie_fecha_valor,
        id_cli_cliente=product_data.id_cli_cliente,
        id_ga_vista=product_data.id_ga_vista,
        id_ga_tipo_dispositivo=product_data.id_ga_tipo_dispositivo,
        id_ga_fuente_medio=product_data.id_ga_fuente_medio,
        desc_ga_sku_producto=product_data.desc_ga_sku_producto,
        desc_ga_categoria_producto=product_data.desc_ga_categoria_producto,
        fc_agregado_carrito_cant=product_data.fc_agregado_carrito_cant,
        fc_ingreso_producto_monto=product_data.fc_ingreso_producto_monto,
        fc_retirado_carrito_cant=product_data.fc_retirado_carrito_cant,
        fc_detalle_producto_cant=product_data.fc_detalle_producto_cant,
        fc_producto_cant=product_data.fc_producto_cant,
        desc_ga_nombre_producto=product_data.desc_ga_nombre_producto,
        fc_visualizaciones_pag_cant=product_data.fc_visualizaciones_pag_cant,
        flag_pipol=product_data.flag_pipol,
        sasasa=product_data.SASASA,
        id_ga_producto=product_data.id_ga_producto,
        desc_ga_nombre_producto_1=product_data.desc_ga_nombre_producto_1,
        desc_ga_sku_producto_1=product_data.desc_ga_sku_producto_1,
        desc_ga_marca_producto=product_data.desc_ga_marca_producto,
        desc_ga_cod_producto=product_data.desc_ga_cod_producto,
        desc_categoria_producto=product_data.desc_categoria_producto,
        desc_categoria_prod_principal=product_data.desc_categoria_prod_principal,
    )


@strawberry.type
class Query:
    """Root GraphQL Query type."""

    @strawberry.field(description="Get all product data with pagination")
    def products(
        self,
        limit: int = 100,
        offset: int = 0
    ) -> List[ProductDataType]:
        """
        Get all products with pagination.
        
        Args:
            limit: Maximum number of records to return (default: 100)
            offset: Number of records to skip (default: 0)
        
        Returns:
            List of product data records
        """
        try:
            products = product_repository.get_all(limit=limit, offset=offset)
            return [product_data_to_graphql(p) for p in products]
        except Exception as e:
            # Log the error and return empty list rather than crashing
            logger.error(f"Error fetching products: {str(e)}", exc_info=True)
            return []

    @strawberry.field(description="Search and filter product data")
    def search_products(
        self,
        filter: Optional[ProductFilterInput] = None
    ) -> List[ProductDataType]:
        """
        Search products with filters.
        
        Args:
            filter: Filter parameters (date, brand, category, etc.)
        
        Returns:
            List of filtered product data records
        """
        try:
            if filter is None:
                filter = ProductFilterInput()
            
            # Convert GraphQL input to model filter
            model_filter = ProductDataFilter(
                date=filter.date,
                client_id=filter.client_id,
                brand=filter.brand,
                sku=filter.sku,
                category=filter.category,
                limit=filter.limit or 100,
                offset=filter.offset or 0
            )
            
            products = product_repository.get_by_filter(model_filter)
            return [product_data_to_graphql(p) for p in products]
        except Exception as e:
            # Log the error and return empty list rather than crashing
            logger.error(f"Error searching products: {str(e)}", exc_info=True)
            return []

    @strawberry.field(description="Get available brands")
    def brands(self) -> List[str]:
        """
        Get list of all unique brands.
        
        Returns:
            List of brand names
        """
        return product_repository.get_brands()

    @strawberry.field(description="Get available categories")
    def categories(self) -> List[str]:
        """
        Get list of all unique categories.
        
        Returns:
            List of category names
        """
        return product_repository.get_categories()

    @strawberry.field(description="Get dataset statistics")
    def stats(self) -> StatsType:
        """
        Get statistics about the dataset.
        
        Returns:
            Statistics including total records, brands, and categories
        """
        total_records = product_repository.count()
        brands = product_repository.get_brands()
        categories = product_repository.get_categories()
        
        return StatsType(
            total_records=total_records,
            brands_count=len(brands),
            categories_count=len(categories)
        )

