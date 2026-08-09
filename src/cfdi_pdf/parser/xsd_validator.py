"""Validación de CFDI 4.0 contra el esquema XSD oficial del SAT.

El paquete incluye ``cfdv40.xsd`` y sus dependencias (``catCFDI.xsd``,
``tdCFDI.xsd``). Al cargar el esquema se reescriben los ``schemaLocation``
para apuntar a los archivos locales empaquetados (sin red).
"""

import logging
from functools import lru_cache
from importlib.resources import files
from typing import Any, cast

from lxml import etree

from ..exceptions import InvalidCFDIError

logger = logging.getLogger(__name__)

# URLs de schemaLocation en cfdv40.xsd -> rutas locales empaquetadas
_SCHEMA_LOCATIONS: dict[bytes, bytes] = {
    b"http://www.sat.gob.mx/sitio_internet/cfd/catalogos/catCFDI.xsd": b"catCFDI.xsd",
    b"http://www.sat.gob.mx/sitio_internet/cfd/tipoDatos/tdCFDI/tdCFDI.xsd": b"tdCFDI/tdCFDI.xsd",
}

_XSD_DIR = files("cfdi_pdf") / "xsd"


def _secure_parser() -> etree.XMLParser:
    """Parser lxml con las mismas protecciones que el parser principal."""
    return etree.XMLParser(
        resolve_entities=False,
        no_network=True,
        load_dtd=False,
        dtd_validation=False,
        huge_tree=False,
    )


@lru_cache(maxsize=1)
def _load_schema() -> etree.XMLSchema:
    """Compila (una vez) el esquema XSD 4.0 con imports locales."""
    xsd_path = str(_XSD_DIR / "cfdv40.xsd")
    content = (_XSD_DIR / "cfdv40.xsd").read_bytes()
    for url, local in _SCHEMA_LOCATIONS.items():
        content = content.replace(url, local)
    document = etree.fromstring(content, _secure_parser(), base_url=xsd_path)
    return etree.XMLSchema(document)


class CFDIXSDValidator:
    """Valida documentos CFDI 4.0 contra el esquema XSD oficial."""

    def validate(self, xml: str | bytes | etree._Element) -> list[str]:
        """
        Valida un documento y devuelve la lista de errores.

        Returns:
            Lista vacía si el documento es válido; en otro caso, mensajes con
            número de línea.
        """
        schema = _load_schema()
        if isinstance(xml, str):
            document = etree.fromstring(xml.encode("utf-8"), _secure_parser())
        elif isinstance(xml, bytes):
            document = etree.fromstring(xml, _secure_parser())
        else:
            document = xml

        if schema.validate(document):
            return []

        error_log = cast("list[Any]", schema.error_log)
        return [f"línea {entry.line}: {entry.message}" for entry in error_log]

    def validate_raise(self, xml: str | bytes | etree._Element) -> None:
        """Valida y lanza InvalidCFDIError si el documento no es válido."""
        errors = self.validate(xml)
        if errors:
            detail = "; ".join(errors[:5])
            raise InvalidCFDIError(f"CFDI no válido contra el esquema XSD: {detail}")
