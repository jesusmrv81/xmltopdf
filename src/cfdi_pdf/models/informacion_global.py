"""Modelo para Información Global del comprobante (cfdi:InformacionGlobal)."""

from pydantic import BaseModel, Field


class InformacionGlobal(BaseModel):
    """Información de un comprobante global (nodo hijo de Comprobante)."""

    periodicidad: str = Field(
        ..., alias="Periodicidad", description="Clave de periodicidad (c_Periodicidad)"
    )
    meses: str = Field(..., alias="Meses", description="Meses que cubre el comprobante")
    anio: int = Field(..., alias="Año", description="Año al que corresponde la información")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
