"""Modelos Pydantic para el complemento de IEPS."""

from decimal import Decimal

from pydantic import BaseModel, Field


class TrasladoIEPS(BaseModel):
    """Traslado de IEPS."""

    base: Decimal | None = Field(None, alias="Base")
    impuesto: str = Field(..., alias="Impuesto")
    tipo_factor: str | None = Field(None, alias="TipoFactor")
    tasa_o_cuota: Decimal | None = Field(None, alias="TasaOCuota")
    importe: Decimal | None = Field(None, alias="Importe")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class RetencionIEPS(BaseModel):
    """Retención de IEPS."""

    impuesto: str = Field(..., alias="Impuesto")
    importe: Decimal | None = Field(None, alias="Importe")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class IEPS(BaseModel):
    """Complemento de IEPS."""

    version: str = Field(..., description="Versión del complemento (1.0)")
    traslado: list[TrasladoIEPS] = Field(default_factory=list, alias="Traslado")
    retencion: list[RetencionIEPS] = Field(default_factory=list, alias="Retencion")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
