"""Modelos Pydantic para el Complemento de Carta Porte 3.1 (subconjunto esencial).

Nota: Carta Porte 3.1 es un esquema muy extenso. Aquí se modelan las
estructuras más relevantes para representación en PDF (Ubicaciones,
Mercancías y Figura de Transporte).
"""

from decimal import Decimal

from pydantic import BaseModel, Field


class Domicilio(BaseModel):
    """Domicilio dentro de una Ubicación."""

    calle: str = Field(..., alias="Calle")
    numero_exterior: str | None = Field(None, alias="NumeroExterior")
    numero_interior: str | None = Field(None, alias="NumeroInterior")
    colonia: str | None = Field(None, alias="Colonia")
    localidad: str | None = Field(None, alias="Localidad")
    municipio: str | None = Field(None, alias="Municipio")
    estado: str = Field(..., alias="Estado")
    pais: str = Field(..., alias="Pais")
    codigo_postal: str = Field(..., alias="CodigoPostal")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Ubicacion(BaseModel):
    """Ubicación de origen/destino del traslado."""

    tipo_estacion: str = Field(..., alias="TipoEstacion", description="Origen o Destino")
    dist_recorrida: Decimal | None = Field(None, alias="DistRecorrida")
    id_ubicacion: str | None = Field(None, alias="IDUbicacion")
    rfc_remitente_destinatario: str | None = Field(None, alias="RFCRemitenteDestinatario")
    nombre_estacion: str | None = Field(None, alias="NombreEstacion")
    fecha_hora_salida_llegada: str | None = Field(None, alias="FechaHoraSalidaLlegada")
    domicilio: Domicilio | None = Field(None, alias="Domicilio")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Ubicaciones(BaseModel):
    """Ubicaciones del traslado."""

    ubicacion: list[Ubicacion] = Field(..., alias="Ubicacion", min_length=2)

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Mercancia(BaseModel):
    """Mercancía transportada."""

    bienes_transp: str = Field(..., alias="BienesTransp")
    clave_stcc: str = Field(..., alias="ClaveSTCC")
    descripcion: str = Field(..., alias="Descripcion")
    cantidad: Decimal = Field(..., alias="Cantidad")
    clave_unidad: str = Field(..., alias="ClaveUnidad")
    material_peligroso: str | None = Field(None, alias="MaterialPeligroso")
    peso_en_kg: Decimal | None = Field(None, alias="PesoEnKg")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Autotransporte(BaseModel):
    """Información del autotransporte (si el medio es autotransporte)."""

    permiso_sct: str = Field(..., alias="PermisoSCT")
    num_permiso_sct: str = Field(..., alias="NumPermisoSCT")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Mercancias(BaseModel):
    """Mercancías transportadas."""

    peso_bruto_total: Decimal = Field(..., alias="PesoBrutoTotal")
    unidad_peso: str = Field(..., alias="UnidadPeso")
    num_total_mercancias: int = Field(..., alias="NumTotalMercancias")
    mercancia: list[Mercancia] = Field(..., alias="Mercancia", min_length=1)
    autotransporte: Autotransporte | None = Field(None, alias="Autotransporte")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class Figura(BaseModel):
    """Figura de transporte."""

    tipo_figura: str = Field(..., alias="TipoFigura")
    rfc_figura: str | None = Field(None, alias="RFCFigura")
    num_licencia: str | None = Field(None, alias="NumLicencia")
    nombre_figura: str | None = Field(None, alias="NombreFigura")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class FiguraTransporte(BaseModel):
    """Figuras que participan en el transporte."""

    figura: list[Figura] = Field(..., alias="Figura", min_length=1)

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}


class CartaPorte(BaseModel):
    """Raíz del complemento de Carta Porte 3.1."""

    version: str = Field(..., description="Versión del complemento (3.1)")
    id_ccp: str | None = Field(None, alias="IdCCP")
    serie: str | None = Field(None, alias="Serie")
    folio: str | None = Field(None, alias="Folio")
    fecha_expedicion: str = Field(..., alias="FechaExpedicion")
    tipo_de_transporte: str = Field(..., alias="TipoDeTransporte")
    trans_internacional: str = Field(..., alias="TransInternacional")
    total_dist_recorrida: Decimal | None = Field(None, alias="TotalDistRecorrida")

    ubicaciones: Ubicaciones | None = Field(None, alias="Ubicaciones")
    mercancias: Mercancias | None = Field(None, alias="Mercancias")
    figura_transporte: FiguraTransporte | None = Field(None, alias="FiguraTransporte")

    model_config = {"frozen": True, "extra": "forbid", "populate_by_name": True}
