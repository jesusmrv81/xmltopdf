"""Main CFDI 4.0 model."""

from decimal import Decimal

from pydantic import BaseModel, Field

from .concepto import Concepto
from .emisor import Emisor
from .impuestos import ImpuestosComprobante
from .pagos import Pagos
from .receptor import Receptor
from .timbre import TimbreFiscalDigital


class CFDI(BaseModel):
    """Represents a complete CFDI 4.0 comprobante."""

    version: str = Field(..., description="Versión del CFDI (4.0)")
    serie: str | None = Field(None, description="Serie del comprobante")
    folio: str | None = Field(None, description="Folio del comprobante")
    fecha: str = Field(..., description="Fecha y hora de expedición")
    forma_pago: str | None = Field(
        None, description="Clave de forma de pago (c_FormaPago). Opcional en CFDI tipo P (Pago)"
    )
    metodo_pago: str | None = Field(
        None, description="Método de pago (PUE/PPD). Opcional en CFDI tipo P (Pago)"
    )
    condiciones_pago: str | None = Field(None, description="Condiciones de pago")
    sub_total: Decimal = Field(..., description="Subtotal del comprobante")
    descuento: Decimal | None = Field(None, description="Descuento total")
    moneda: str = Field(..., description="Clave de moneda (c_Moneda)")
    tipo_cambio: Decimal | None = Field(None, description="Tipo de cambio")
    total: Decimal = Field(..., description="Total del comprobante")
    tipo_comprobante: str = Field(..., description="Tipo (I=Ingreso, E=Egreso, T=Traslado, P=Pago)")
    exportacion: str = Field(..., description="Clave de exportación (c_Exportacion)")
    lugar_expedicion: str = Field(..., description="Código postal de expedición")
    confirmacion: str | None = Field(None, description="Clave de confirmación")
    no_certificado: str = Field(..., description="Número de certificado del emisor")
    certificado: str = Field(..., description="Certificado del emisor")

    emisor: Emisor = Field(..., description="Datos del emisor")
    receptor: Receptor = Field(..., description="Datos del receptor")
    conceptos: list[Concepto] = Field(..., min_length=1, description="Conceptos")
    impuestos: ImpuestosComprobante | None = Field(None, description="Impuestos")
    timbre_fiscal: TimbreFiscalDigital | None = Field(None, description="Timbre Fiscal Digital")

    pagos: Pagos | None = Field(None, description="Complemento de Pago 2.0")

    complementos: dict[str, dict[str, object]] = Field(
        default_factory=dict,
        description="Complementos adicionales (Carta Porte, Nómina, etc.)",
    )

    model_config = {"frozen": True, "extra": "forbid"}
