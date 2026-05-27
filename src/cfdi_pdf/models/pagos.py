"""Pydantic models for Complemento de Pago 2.0 (Pagos20)."""

from decimal import Decimal

from pydantic import BaseModel, Field


class TrasladoDR(BaseModel):
    """Tax transfer at the DoctoRelacionado level."""

    base_dr: Decimal = Field(..., alias="BaseDR", description="Base del impuesto")
    impuesto_dr: str = Field(..., alias="ImpuestoDR", description="Clave del impuesto (002=IVA)")
    tipo_factor_dr: str = Field(..., alias="TipoFactorDR", description="Tipo de factor")
    tasa_o_cuota_dr: Decimal = Field(
        ..., alias="TasaOCuotaDR", description="Tasa o cuota del impuesto"
    )
    importe_dr: Decimal = Field(..., alias="ImporteDR", description="Importe del impuesto")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class RetencionDR(BaseModel):
    """Tax withholding at the DoctoRelacionado level."""

    base_dr: Decimal = Field(..., alias="BaseDR", description="Base del impuesto")
    impuesto_dr: str = Field(..., alias="ImpuestoDR", description="Clave del impuesto (002=IVA)")
    tipo_factor_dr: str = Field(..., alias="TipoFactorDR", description="Tipo de factor")
    tasa_o_cuota_dr: Decimal = Field(
        ..., alias="TasaOCuotaDR", description="Tasa o cuota del impuesto"
    )
    importe_dr: Decimal = Field(..., alias="ImporteDR", description="Importe del impuesto")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class ImpuestosDR(BaseModel):
    """Taxes at the DoctoRelacionado level."""

    retenciones_dr: list[RetencionDR] = Field(
        default_factory=list, alias="RetencionesDR", description="Retenciones del documento"
    )
    traslados_dr: list[TrasladoDR] = Field(
        default_factory=list, alias="TrasladosDR", description="Traslados del documento"
    )

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class DoctoRelacionado(BaseModel):
    """Related document referenced by a payment."""

    id_documento: str = Field(
        ..., alias="IdDocumento", description="UUID del documento relacionado"
    )
    moneda_dr: str = Field(..., alias="MonedaDR", description="Moneda del documento relacionado")
    equivalencia_dr: Decimal = Field(
        ..., alias="EquivalenciaDR", description="Tipo de cambio respecto a moneda del pago"
    )
    num_parcialidad: int = Field(..., alias="NumParcialidad", description="Número de parcialidad")
    imp_saldo_ant: Decimal = Field(
        ..., alias="ImpSaldoAnt", description="Saldo anterior del documento"
    )
    imp_pagado: Decimal = Field(..., alias="ImpPagado", description="Monto pagado del documento")
    imp_saldo_insoluto: Decimal = Field(
        ..., alias="ImpSaldoInsoluto", description="Saldo insoluto del documento"
    )
    objeto_imp_dr: str = Field(
        ..., alias="ObjetoImpDR", description="Objeto de impuesto del documento (01-04)"
    )
    impuestos_dr: ImpuestosDR | None = Field(
        None, alias="ImpuestosDR", description="Impuestos del documento relacionado"
    )

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class TrasladoP(BaseModel):
    """Tax transfer at the payment level."""

    base_p: Decimal = Field(..., alias="BaseP", description="Base del impuesto")
    impuesto_p: str = Field(..., alias="ImpuestoP", description="Clave del impuesto")
    tipo_factor_p: str = Field(..., alias="TipoFactorP", description="Tipo de factor")
    tasa_o_cuota_p: Decimal = Field(
        ..., alias="TasaOCuotaP", description="Tasa o cuota del impuesto"
    )
    importe_p: Decimal = Field(..., alias="ImporteP", description="Importe del impuesto")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class RetencionP(BaseModel):
    """Tax withholding at the payment level."""

    impuesto_p: str = Field(..., alias="ImpuestoP", description="Clave del impuesto")
    importe_p: Decimal = Field(..., alias="ImporteP", description="Importe retenido")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class ImpuestosP(BaseModel):
    """Taxes at the payment level."""

    retenciones_p: list[RetencionP] = Field(
        default_factory=list, alias="RetencionesP", description="Retenciones del pago"
    )
    traslados_p: list[TrasladoP] = Field(
        default_factory=list, alias="TrasladosP", description="Traslados del pago"
    )

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Pago(BaseModel):
    """Individual payment (Pago) within Pagos complement."""

    fecha_pago: str = Field(..., alias="FechaPago", description="Fecha y hora del pago")
    forma_de_pago_p: str = Field(
        ..., alias="FormaDePagoP", description="Forma de pago (c_FormaDePagoP)"
    )
    moneda_p: str = Field(..., alias="MonedaP", description="Moneda del pago")
    tipo_cambio_p: Decimal = Field(..., alias="TipoCambioP", description="Tipo de cambio del pago")
    monto: Decimal = Field(..., alias="Monto", description="Monto del pago")
    num_operacion: str | None = Field(None, alias="NumOperacion", description="Número de operación")
    rfc_emisor_cta_ord: str | None = Field(
        None, alias="RfcEmisorCtaOrd", description="RFC del emisor de la cuenta ordenante"
    )
    rfc_emisor_cta_ben: str | None = Field(
        None, alias="RfcEmisorCtaBen", description="RFC del emisor de la cuenta beneficiaria"
    )
    docto_relacionado: list[DoctoRelacionado] = Field(
        ..., alias="DoctoRelacionado", min_length=1, description="Documentos relacionados"
    )
    impuestos_p: ImpuestosP | None = Field(
        None, alias="ImpuestosP", description="Impuestos del pago"
    )

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Totales(BaseModel):
    """Totales within Pagos complement."""

    monto_total_pagos: Decimal = Field(
        ..., alias="MontoTotalPagos", description="Monto total de los pagos"
    )
    total_retenciones_iva: Decimal | None = Field(
        None, alias="TotalRetencionesIVA", description="Total de retenciones de IVA"
    )
    total_retenciones_isr: Decimal | None = Field(
        None, alias="TotalRetencionesISR", description="Total de retenciones de ISR"
    )
    total_retenciones_ieps: Decimal | None = Field(
        None, alias="TotalRetencionesIEPS", description="Total de retenciones de IEPS"
    )
    total_traslados_base_iva16: Decimal | None = Field(
        None, alias="TotalTrasladosBaseIVA16", description="Base de IVA 16%"
    )
    total_traslados_impuesto_iva16: Decimal | None = Field(
        None, alias="TotalTrasladosImpuestoIVA16", description="Importe de IVA 16%"
    )
    total_traslados_base_iva8: Decimal | None = Field(
        None, alias="TotalTrasladosBaseIVA8", description="Base de IVA 8%"
    )
    total_traslados_impuesto_iva8: Decimal | None = Field(
        None, alias="TotalTrasladosImpuestoIVA8", description="Importe de IVA 8%"
    )
    total_traslados_base_iva0: Decimal | None = Field(
        None, alias="TotalTrasladosBaseIVA0", description="Base de IVA 0%"
    )
    total_traslados_impuesto_iva0: Decimal | None = Field(
        None, alias="TotalTrasladosImpuestoIVA0", description="Importe de IVA exento"
    )
    total_traslados_base_iva_frontera: Decimal | None = Field(
        None, alias="TotalTrasladosBaseIVAFrontera", description="Base de IVA Frontera"
    )
    total_traslados_impuesto_iva_frontera: Decimal | None = Field(
        None, alias="TotalTrasladosImpuestoIVAFrontera", description="Importe de IVA Frontera"
    )
    total_traslados_base_exento: Decimal | None = Field(
        None, alias="TotalTrasladosBaseExento", description="Base exenta"
    )

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Pagos(BaseModel):
    """Root model for Complemento de Pago 2.0."""

    version: str = Field(..., description="Versión del complemento (2.0)")
    totales: Totales = Field(..., alias="Totales", description="Totales de los pagos")
    pago: list[Pago] = Field(..., alias="Pago", min_length=1, description="Lista de pagos")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
