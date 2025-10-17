"""Product data models."""

from typing import Optional

from pydantic import BaseModel, Field


class ProductData(BaseModel):
    """Model for product analytics data from CSV."""

    id_tie_fecha_valor: Optional[str] = Field(None, description="Date value ID")
    id_cli_cliente: Optional[int] = Field(None, description="Client ID")
    id_ga_vista: Optional[int] = Field(None, description="View ID")
    id_ga_tipo_dispositivo: Optional[int] = Field(None, description="Device type ID")
    id_ga_fuente_medio: Optional[int] = Field(None, description="Source/Medium ID")
    desc_ga_sku_producto: Optional[str] = Field(None, description="Product SKU")
    desc_ga_categoria_producto: Optional[str] = Field(None, description="Product category")
    fc_agregado_carrito_cant: Optional[int] = Field(None, description="Added to cart quantity")
    fc_ingreso_producto_monto: Optional[float] = Field(None, description="Product revenue amount")
    fc_retirado_carrito_cant: Optional[int] = Field(None, description="Removed from cart quantity")
    fc_detalle_producto_cant: Optional[int] = Field(None, description="Product detail views count")
    fc_producto_cant: Optional[int] = Field(None, description="Product quantity")
    desc_ga_nombre_producto: Optional[str] = Field(None, description="Product name (1)")
    fc_visualizaciones_pag_cant: Optional[int] = Field(None, description="Page views count")
    flag_pipol: Optional[int] = Field(None, description="Pipol flag")
    SASASA: Optional[str] = Field(None, description="SASASA field")
    id_ga_producto: Optional[int] = Field(None, description="Product ID")
    desc_ga_nombre_producto_1: Optional[str] = Field(None, description="Product name")
    desc_ga_sku_producto_1: Optional[str] = Field(None, description="Product SKU (alt)")
    desc_ga_marca_producto: Optional[str] = Field(None, description="Product brand")
    desc_ga_cod_producto: Optional[str] = Field(None, description="Product code")
    desc_categoria_producto: Optional[str] = Field(None, description="Product category (detailed)")
    desc_categoria_prod_principal: Optional[str] = Field(None, description="Main product category")

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {
            "example": {
                "id_tie_fecha_valor": "20240129",
                "id_cli_cliente": 8,
                "desc_ga_sku_producto": "K1010148001",
                "desc_ga_nombre_producto_1": "TERMO CLÁSICO STANLEY 950 ML",
                "desc_ga_marca_producto": "STANLEY",
                "fc_agregado_carrito_cant": 1,
            }
        }


class ProductDataFilter(BaseModel):
    """Filter parameters for product data queries."""

    date: Optional[str] = Field(None, description="Filter by date (id_tie_fecha_valor)")
    client_id: Optional[int] = Field(None, description="Filter by client ID")
    brand: Optional[str] = Field(None, description="Filter by product brand")
    sku: Optional[str] = Field(None, description="Filter by product SKU")
    category: Optional[str] = Field(None, description="Filter by category")
    limit: Optional[int] = Field(100, description="Maximum number of records to return", le=1000)
    offset: Optional[int] = Field(0, description="Number of records to skip", ge=0)

    class Config:
        """Pydantic configuration."""

        json_schema_extra = {"example": {"brand": "STANLEY", "limit": 10, "offset": 0}}
