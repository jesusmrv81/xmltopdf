"""Emisor (issuer) model for CFDI 4.0."""

from pydantic import BaseModel, Field


class Emisor(BaseModel):
    """Represents the CFDI issuer (Emisor)."""

    rfc: str = Field(..., description="RFC del emisor")
    nombre: str = Field(..., description="Nombre o razón social del emisor")
    regimen_fiscal: str = Field(..., description="Clave del régimen fiscal (c_RegimenFiscal)")

    model_config = {"frozen": True, "extra": "forbid"}
