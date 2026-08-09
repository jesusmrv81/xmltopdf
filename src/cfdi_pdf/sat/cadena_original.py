"""Generación de cadenas originales usando los XSLT oficiales del SAT.

El SAT publica las transformaciones ``cadenaoriginal_4_0.xslt`` y
``cadenaoriginal_TFD_1_1.xslt`` (versión 2.0 de XSLT). Aunque lxml/libxslt solo
implementa XSLT 1.0, estos estilos usan únicamente características compatibles
con 1.0, por lo que pueden ejecutarse con ``lxml.etree.XSLT``.

Los archivos se empaquetan dentro del paquete en ``cfdi_pdf/xslt/`` y se
resuelven en runtime con ``importlib.resources``.
"""

import logging
from functools import lru_cache
from importlib.resources import files

from lxml import etree

from ..exceptions import XMLParseError

logger = logging.getLogger(__name__)

# Raíz del árbol de XSLT del comprobante (espejo de www.sat.gob.mx/sitio_internet/cfd)
_CFD_XSLT_ROOT = files("cfdi_pdf") / "xslt" / "cfd"
_TFD_XSLT_PATH = files("cfdi_pdf") / "xslt" / "cadenaoriginal_TFD_1_1.xslt"

# Ruta relativa del XSLT principal del comprobante dentro del árbol
_CFD_MAIN_XSLT = "4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt"


def _secure_parser() -> etree.XMLParser:
    """Parser lxml con las mismas protecciones que el parser principal."""
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        dtd_validation=False,
        huge_tree=False,
    )


@lru_cache(maxsize=2)
def _compile_transform(xslt_path: str) -> etree.XSLT:
    """Compila un XSLT (con sus ``xsl:include``) y lo cachea."""
    try:
        doc = etree.parse(xslt_path, _secure_parser())
        return etree.XSLT(doc)
    except etree.XMLSyntaxError as exc:
        raise XMLParseError(f"XSLT inválido: {xslt_path}: {exc}") from exc


def _transform_path(*parts: str) -> str:
    """Devuelve la ruta de archivo real de un recurso empaquetado."""
    resource = _CFD_XSLT_ROOT
    for part in parts:
        resource = resource / part
    return str(resource)


def cadena_original_comprobante(xml: str | bytes | etree._Element) -> str:
    """
    Aplica ``cadenaoriginal_4_0.xslt`` a un CFDI 4.0 y devuelve la cadena original.

    Args:
        xml: documento CFDI 4.0 (string, bytes o elemento ``Comprobante``).

    Returns:
        Cadena original del comprobante, incluyendo los complementos presentes
        (Pagos, Nómina, Carta Porte, etc.) según las XSLT incluidas.

    Raises:
        XMLParseError: si el XSLT no puede compilarse.
    """
    transform = _compile_transform(_transform_path(*_CFD_MAIN_XSLT.split("/")))

    if isinstance(xml, str):
        document = etree.fromstring(xml.encode("utf-8"), _secure_parser())
    elif isinstance(xml, bytes):
        document = etree.fromstring(xml, _secure_parser())
    else:
        document = xml

    return str(transform(document))


def cadena_original_tfd(tfd_element: etree._Element) -> str:
    """
    Aplica ``cadenaoriginal_TFD_1_1.xslt`` al elemento TimbreFiscalDigital.

    Args:
        tfd_element: elemento ``tfd:TimbreFiscalDigital``.

    Returns:
        Cadena original del timbre fiscal digital.
    """
    transform = _compile_transform(str(_TFD_XSLT_PATH))
    return str(transform(tfd_element))
