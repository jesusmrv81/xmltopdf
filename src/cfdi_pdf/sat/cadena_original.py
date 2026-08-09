"""Generación de cadenas originales usando los XSLT oficiales del SAT.

El SAT publica las transformaciones ``cadenaoriginal_4_0.xslt`` y
``cadenaoriginal_TFD_1_1.xslt`` (versión 2.0 de XSLT). Aunque lxml/libxslt solo
implementa XSLT 1.0, estos estilos usan únicamente características compatibles
con 1.0, por lo que pueden ejecutarse con ``lxml.etree.XSLT``.

Los archivos NO se empaquetan en la biblioteca: se descargan en runtime desde
el SAT (con mirror verificado como respaldo) mediante :class:`SATResourceManager`
y se cachean en disco.
"""

import logging
from functools import lru_cache

from lxml import etree

from ..exceptions import XMLParseError
from .resources import XSLT_RESOURCES, get_manager

logger = logging.getLogger(__name__)

# Rutas relativas (dentro de sitio_internet/cfd) de los XSLT principales.
_CFD_MAIN_XSLT = "4/cadenaoriginal_4_0/cadenaoriginal_4_0.xslt"
_TFD_XSLT = "TimbreFiscalDigital/cadenaoriginal_TFD_1_1.xslt"


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


def _ensure_xslt_tree() -> None:
    """Descarga (una vez) todo el árbol XSLT de la cadena original 4.0."""
    get_manager().ensure_many(XSLT_RESOURCES)


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
        SATResourceError: si no se pueden descargar los XSLT del SAT.
    """
    _ensure_xslt_tree()
    transform = _compile_transform(str(get_manager().path(_CFD_MAIN_XSLT)))

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
    _ensure_xslt_tree()
    transform = _compile_transform(str(get_manager().path(_TFD_XSLT)))
    return str(transform(tfd_element))
