"""Tax models for CFDI 4.0."""

from decimal import Decimal

from pydantic import BaseModel, Field


class Traslado(BaseModel):
    """Represents a tax transfer (Traslado)."""

    base: Decimal = Field(..., description="Base gravable")
    impuesto: str = Field(..., description="Clave del impuesto (001=ISR, 002=IVA, 003=IEPS)")
    tipo_factor: str = Field(..., description="Tipo de factor (Tasa, Cuota, Exento)")
    tasa_o_cuota: Decimal | None = Field(None, description="Tasa o cuota del impuesto")
    importe: Decimal | None = Field(None, description="Importe del impuesto")

    model_config = {"frozen": True, "extra": "forbid"}


class Retencion(BaseModel):
    """Represents a tax withholding (Retención)."""

    base: Decimal | None = Field(None, description="Base gravable")
    impuesto: str = Field(..., description="Clave del impuesto (001=ISR, 002=IVA, 003=IEPS)")
    tipo_factor: str | None = Field(None, description="Tipo de factor")
    tasa_o_cuota: Decimal | None = Field(None, description="Tasa o cuota")
    importe: Decimal = Field(..., description="Importe retenido")

    model_config = {"frozen": True, "extra": "forbid"}


class ImpuestosConcepto(BaseModel):
    """Represents taxes at the concept level."""

    traslados: list[Traslado] = Field(default_factory=list, description="Traslados del concepto")
    retenciones: list[Retencion] = Field(
        default_factory=list, description="Retenciones del concepto"
    )

    model_config = {"frozen": True, "extra": "forbid"}


class ImpuestosComprobante(BaseModel):
    """Represents taxes at the comprobante level."""

    total_impuestos_trasladados: Decimal | None = Field(
        None, description="Total de impuestos trasladados"
    )
    total_impuestos_retenidos: Decimal | None = Field(
        None, description="Total de impuestos retenidos"
    )
    traslados: list[Traslado] = Field(
        default_factory=list, description="Traslados del comprobante"
    )
    retenciones: list[Retencion] = Field(
        default_factory=list, description="Retenciones del comprobante"
    )

    model_config = {"frozen": True, "extra": "forbid"}
