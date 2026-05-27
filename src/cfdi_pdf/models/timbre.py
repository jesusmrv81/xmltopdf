"""Timbre Fiscal Digital (TFD) model for CFDI 4.0."""

from pydantic import BaseModel, Field


class TimbreFiscalDigital(BaseModel):
    """Represents the Timbre Fiscal Digital 1.1."""

    version: str = Field(..., description="Versión del TFD (1.1)")
    uuid: str = Field(..., description="Folio fiscal UUID")
    fecha_timbrado: str = Field(..., description="Fecha y hora de timbrado (ISO 8601)")
    rfc_prov_certif: str = Field(..., description="RFC del proveedor de certificación")
    sello_cfd: str = Field(..., description="Sello digital del CFDI")
    sello_sat: str = Field(..., description="Sello digital del SAT")
    no_certificado_sat: str = Field(..., description="Número de certificado del SAT")
    no_certificado_emisor: str | None = Field(None, description="Número de certificado del emisor")
    cadena_origen: str | None = Field(None, description="Cadena original del complemento")

    model_config = {"frozen": True, "extra": "forbid"}
