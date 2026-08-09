"""Modelos Pydantic para el Complemento de Nómina 1.2 (nomina12)."""

from decimal import Decimal

from pydantic import BaseModel, Field


class NominaEmisor(BaseModel):
    """Emisor dentro del complemento de nómina."""

    registro_patronal: str | None = Field(
        None, alias="RegistroPatronal", description="Registro patronal"
    )


class NominaReceptor(BaseModel):
    """Receptor dentro del complemento de nómina."""

    num_seguridad_social: str | None = Field(None, alias="NumSeguridadSocial")
    fecha_inicio_rel_laboral: str | None = Field(None, alias="FechaInicioRelLaboral")
    antiguedad: str | None = Field(None, alias="Antigüedad")
    continuidad_laboral: str | None = Field(None, alias="ContinuidadLaboral")
    sindicalizado: str | None = Field(None, alias="Sindicalizado")
    tipo_contrato: str = Field(..., alias="TipoContrato")
    tipo_jornada: str | None = Field(None, alias="TipoJornada")
    tipo_regimen: str = Field(..., alias="TipoRegimen")
    num_empleado: str = Field(..., alias="NumEmpleado")
    departamento: str | None = Field(None, alias="Departamento")
    puesto: str | None = Field(None, alias="Puesto")
    riesgo_puesto: str | None = Field(None, alias="RiesgoPuesto")
    periodicidad_pago: str = Field(..., alias="PeriodicidadPago")
    banco: str | None = Field(None, alias="Banco")
    clave_banco: str | None = Field(None, alias="ClaveBanco")
    salario_base_cot_apor: Decimal | None = Field(None, alias="SalarioBaseCotApor")
    salario_diario_integrado: Decimal | None = Field(None, alias="SalarioDiarioIntegrado")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Percepcion(BaseModel):
    """Percepción individual."""

    tipo_percepcion: str = Field(..., alias="TipoPercepcion")
    clave: str = Field(..., alias="Clave")
    concepto: str = Field(..., alias="Concepto")
    importe_gravado: Decimal = Field(..., alias="ImporteGravado")
    importe_exento: Decimal = Field(..., alias="ImporteExento")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Percepciones(BaseModel):
    """Percepciones del trabajador."""

    total_sueldos: Decimal | None = Field(None, alias="TotalSueldos")
    total_separacion_indemnizacion: Decimal | None = Field(
        None, alias="TotalSeparacionIndemnizacion"
    )
    total_jubilacion_pension_retiro: Decimal | None = Field(
        None, alias="TotalJubilacionPensionRetiro"
    )
    total_gravado: Decimal | None = Field(None, alias="TotalGravado")
    total_exento: Decimal | None = Field(None, alias="TotalExento")
    percepcion: list[Percepcion] = Field(default_factory=list, alias="Percepcion")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Deduccion(BaseModel):
    """Deducción individual."""

    tipo_deduccion: str = Field(..., alias="TipoDeduccion")
    clave: str = Field(..., alias="Clave")
    concepto: str = Field(..., alias="Concepto")
    importe: Decimal = Field(..., alias="Importe")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Deducciones(BaseModel):
    """Deducciones del trabajador."""

    total_otras_deducciones: Decimal | None = Field(None, alias="TotalOtrasDeducciones")
    total_impuestos_retenidos: Decimal | None = Field(None, alias="TotalImpuestosRetenidos")
    deduccion: list[Deduccion] = Field(default_factory=list, alias="Deduccion")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class OtroPago(BaseModel):
    """Otro pago (no percepción ni deducción)."""

    tipo_otro_pago: str = Field(..., alias="TipoOtroPago")
    clave: str = Field(..., alias="Clave")
    concepto: str = Field(..., alias="Concepto")
    importe: Decimal = Field(..., alias="Importe")
    subsidio_al_empleo: Decimal | None = Field(None, alias="SubsidioAlEmpleo")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class OtrosPagos(BaseModel):
    """Otros pagos."""

    otro_pago: list[OtroPago] = Field(default_factory=list, alias="OtroPago")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Nomina(BaseModel):
    """Raíz del complemento de Nómina 1.2."""

    version: str = Field(..., description="Versión del complemento (1.2)")
    tipo_nomina: str = Field(
        ..., alias="TipoNomina", description="Tipo de nómina (O=Egreso, I=Ingreso)"
    )
    fecha_pago: str = Field(..., alias="FechaPago")
    fecha_inicial_pago: str = Field(..., alias="FechaInicialPago")
    fecha_final_pago: str = Field(..., alias="FechaFinalPago")
    num_dias_pagados: Decimal = Field(..., alias="NumDiasPagados")
    total_percepciones: Decimal | None = Field(None, alias="TotalPercepciones")
    total_deducciones: Decimal | None = Field(None, alias="TotalDeducciones")
    total_otros_pagos: Decimal | None = Field(None, alias="TotalOtrosPagos")

    emisor: NominaEmisor | None = Field(None, alias="Emisor")
    receptor: NominaReceptor = Field(..., alias="Receptor")
    percepciones: Percepciones | None = Field(None, alias="Percepciones")
    deducciones: Deducciones | None = Field(None, alias="Deducciones")
    otros_pagos: OtrosPagos | None = Field(None, alias="OtrosPagos")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
