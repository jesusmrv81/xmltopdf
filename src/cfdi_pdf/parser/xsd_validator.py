"""Validación de CFDI 4.0 contra el esquema XSD oficial del SAT.

El esquema ``cfdv40.xsd`` y sus dependencias (``catCFDI.xsd``, ``tdCFDI.xsd``)
se descargan en runtime desde el SAT mediante :class:`SATResourceManager` (no
se empaquetan). Un resolver de lxml mapea los ``schemaLocation`` absolutos del
SAT a los archivos locales en caché (sin red).
"""

import logging
from functools import lru_cache
from pathlib import Path
from typing import Any, cast

from lxml import etree

from ..exceptions import InvalidCFDIError
from ..sat.resources import XSD_RESOURCES, get_manager

logger = logging.getLogger(__name__)


class _SchemaResolver(etree.Resolver):
    """Resuelve los imports del XSD del SAT a los archivos locales en caché."""

    def __init__(self, cache_dir: Path) -> None:
        self.cache_dir = cache_dir

    def resolve(  # type: ignore[override]  # lxml pasa (system_url, public_id, context)
        self, system_url: str, public_id: str, context: object
    ) -> etree.Resolver | None:
        for relative in XSD_RESOURCES:
            if system_url.endswith(relative):
                path = self.cache_dir / relative
                if path.exists():
                    return self.resolve_filename(str(path), context)  # type: ignore[attr-defined, no-any-return]
        return None


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
    get_manager().ensure_many(XSD_RESOURCES)
    parser = _secure_parser()
    parser.resolvers.add(_SchemaResolver(get_manager().cache_dir))
    xsd_path = str(get_manager().path("4/cfdv40.xsd"))
    document = etree.parse(xsd_path, parser)
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
