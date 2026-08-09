"""Models package for CFDI PDF."""

from .carta_porte import (
    Autotransporte,
    CartaPorte,
    Domicilio,
    Figura,
    FiguraTransporte,
    Mercancia,
    Mercancias,
    Ubicacion,
    Ubicaciones,
)
from .cfdi import CFDI
from .concepto import Concepto
from .emisor import Emisor
from .ieps import IEPS, RetencionIEPS, TrasladoIEPS
from .impuestos import ImpuestosComprobante, ImpuestosConcepto, Retencion, Traslado
from .informacion_global import InformacionGlobal
from .leyendas import Leyenda, LeyendasFiscales
from .nomina import (
    Deduccion,
    Deducciones,
    Nomina,
    NominaEmisor,
    NominaReceptor,
    OtroPago,
    OtrosPagos,
    Percepcion,
    Percepciones,
)
from .pagos import (
    DoctoRelacionado,
    ImpuestosDR,
    ImpuestosP,
    Pago,
    Pagos,
    RetencionDR,
    RetencionP,
    Totales,
    TrasladoDR,
    TrasladoP,
)
from .receptor import Receptor
from .timbre import TimbreFiscalDigital

__all__ = [
    "CFDI",
    "IEPS",
    "Autotransporte",
    "CartaPorte",
    "Concepto",
    "Deduccion",
    "Deducciones",
    "DoctoRelacionado",
    "Domicilio",
    "Emisor",
    "Figura",
    "FiguraTransporte",
    "ImpuestosComprobante",
    "ImpuestosConcepto",
    "ImpuestosDR",
    "ImpuestosP",
    "InformacionGlobal",
    "Leyenda",
    "LeyendasFiscales",
    "Mercancia",
    "Mercancias",
    "Nomina",
    "NominaEmisor",
    "NominaReceptor",
    "OtroPago",
    "OtrosPagos",
    "Pago",
    "Pagos",
    "Percepcion",
    "Percepciones",
    "Receptor",
    "Retencion",
    "RetencionDR",
    "RetencionIEPS",
    "RetencionP",
    "TimbreFiscalDigital",
    "Totales",
    "Traslado",
    "TrasladoDR",
    "TrasladoIEPS",
    "TrasladoP",
    "Ubicacion",
    "Ubicaciones",
]
