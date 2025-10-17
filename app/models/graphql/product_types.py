"""GraphQL types and schema definitions using Strawberry."""

from typing import Optional

import strawberry


@strawberry.type
class ProductDataType:
    """GraphQL type for product data."""

    id_tie_fecha_valor: Optional[str] = strawberry.field(description="Date value ID")
    id_cli_cliente: Optional[int] = strawberry.field(description="Client ID")
    id_ga_vista: Optional[int] = strawberry.field(description="View ID")
    id_ga_tipo_dispositivo: Optional[int] = strawberry.field(description="Device type ID")
    id_ga_fuente_medio: Optional[int] = strawberry.field(description="Source/Medium ID")
    desc_ga_sku_producto: Optional[str] = strawberry.field(description="Product SKU")
    desc_ga_categoria_producto: Optional[str] = strawberry.field(description="Product category")
    fc_agregado_carrito_cant: Optional[int] = strawberry.field(description="Added to cart quantity")
    fc_ingreso_producto_monto: Optional[float] = strawberry.field(
        description="Product revenue amount"
    )
    fc_retirado_carrito_cant: Optional[int] = strawberry.field(
        description="Removed from cart quantity"
    )
    fc_detalle_producto_cant: Optional[int] = strawberry.field(
        description="Product detail views count"
    )
    fc_producto_cant: Optional[int] = strawberry.field(description="Product quantity")
    desc_ga_nombre_producto: Optional[str] = strawberry.field(description="Product name (1)")
    fc_visualizaciones_pag_cant: Optional[int] = strawberry.field(description="Page views count")
    flag_pipol: Optional[int] = strawberry.field(description="Pipol flag")
    sasasa: Optional[str] = strawberry.field(description="SASASA field")
    id_ga_producto: Optional[int] = strawberry.field(description="Product ID")
    desc_ga_nombre_producto_1: Optional[str] = strawberry.field(description="Product name")
    desc_ga_sku_producto_1: Optional[str] = strawberry.field(description="Product SKU (alt)")
    desc_ga_marca_producto: Optional[str] = strawberry.field(description="Product brand")
    desc_ga_cod_producto: Optional[str] = strawberry.field(description="Product code")
    desc_categoria_producto: Optional[str] = strawberry.field(
        description="Product category (detailed)"
    )
    desc_categoria_prod_principal: Optional[str] = strawberry.field(
        description="Main product category"
    )


@strawberry.input
class ProductFilterInput:
    """GraphQL input type for filtering product data."""

    date: Optional[str] = strawberry.field(default=None, description="Filter by date")
    client_id: Optional[int] = strawberry.field(default=None, description="Filter by client ID")
    brand: Optional[str] = strawberry.field(default=None, description="Filter by product brand")
    sku: Optional[str] = strawberry.field(default=None, description="Filter by product SKU")
    category: Optional[str] = strawberry.field(default=None, description="Filter by category")
    limit: Optional[int] = strawberry.field(
        default=100, description="Maximum number of records (max 1000)"
    )
    offset: Optional[int] = strawberry.field(default=0, description="Number of records to skip")


@strawberry.type
class StatsType:
    """GraphQL type for statistics."""

    total_records: int = strawberry.field(description="Total number of records in dataset")
    brands_count: int = strawberry.field(description="Number of unique brands")
    categories_count: int = strawberry.field(description="Number of unique categories")
