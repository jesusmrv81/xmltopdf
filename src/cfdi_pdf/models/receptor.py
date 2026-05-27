"""Receptor (recipient) model for CFDI 4.0."""

from pydantic import BaseModel, Field


class Receptor(BaseModel):
    """Represents the CFDI recipient (Receptor)."""

    rfc: str = Field(..., description="RFC del receptor")
    nombre: str = Field(..., description="Nombre o razón social del receptor")
    domicilio_fiscal: str = Field(
        ..., description="Código postal del domicilio fiscal del receptor"
    )
    regimen_fiscal: str = Field(
        ..., description="Clave del régimen fiscal del receptor (c_RegimenFiscal)"
    )
    uso_cfdi: str = Field(..., description="Clave del uso del CFDI (c_UsoCFDI)")

    model_config = {"frozen": True, "extra": "forbid"}
