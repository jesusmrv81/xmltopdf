"""Concept (line item) model for CFDI 4.0."""

from decimal import Decimal

from pydantic import BaseModel, Field

from .impuestos import ImpuestosConcepto


class Concepto(BaseModel):
    """Represents a CFDI concept (line item)."""

    clave_prod_serv: str = Field(..., description="Clave del producto o servicio")
    cantidad: Decimal = Field(..., description="Cantidad")
    clave_unidad: str = Field(..., description="Clave de unidad (c_ClaveUnidad)")
    unidad: str | None = Field(None, description="Nombre de la unidad")
    descripcion: str = Field(..., description="Descripción del concepto")
    valor_unitario: Decimal = Field(..., description="Valor unitario")
    importe: Decimal = Field(..., description="Importe total (cantidad × valor unitario)")
    descuento: Decimal | None = Field(None, description="Descuento aplicado")
    objeto_imp: str = Field(..., description="Objeto de impuesto (01-04)")
    impuestos: ImpuestosConcepto | None = Field(
        None, description="Impuestos aplicables al concepto"
    )

    model_config = {"frozen": True, "extra": "forbid"}
