"""Modelos Pydantic para el complemento de Leyendas Fiscales."""

from pydantic import BaseModel, Field


class Leyenda(BaseModel):
    """Leyenda fiscal individual."""

    disposicion_fiscal: str = Field(..., alias="disposicionFiscal")
    norma: str | None = Field(None, alias="norma")
    texto_leyenda: str = Field(..., alias="textoLeyenda")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class LeyendasFiscales(BaseModel):
    """Complemento de Leyendas Fiscales."""

    version: str = Field(..., description="Versión del complemento (1.0)")
    leyenda: list[Leyenda] = Field(default_factory=list, alias="Leyenda")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
