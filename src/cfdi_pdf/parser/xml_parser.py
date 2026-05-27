"""Secure XML parser for CFDI 4.0 documents."""

import logging
from decimal import Decimal, InvalidOperation
from pathlib import Path

from lxml import etree

from ..exceptions import InvalidCFDIError, XMLParseError
from ..models import (
    CFDI,
    Concepto,
    Emisor,
    ImpuestosComprobante,
    ImpuestosConcepto,
    Receptor,
    Retencion,
    TimbreFiscalDigital,
    Traslado,
)
from .sanitizer import XMLSanitizer

logger = logging.getLogger(__name__)

# CFDI 4.0 namespaces
CFDI_NS = "http://www.sat.gob.mx/cfd/4"
TFD_NS = "http://www.sat.gob.mx/TimbreFiscalDigital"

NAMESPACES = {
    "cfdi": CFDI_NS,
    "tfd": TFD_NS,
}


class CFDIParser:
    """Secure XML parser for CFDI 4.0 documents."""

    def __init__(self) -> None:
        """Initialize parser with security protections."""
        self._sanitizer = XMLSanitizer()

    def parse_file(self, xml_path: str | Path) -> CFDI:
        """
        Parse CFDI XML from file.

        Args:
            xml_path: Path to XML file

        Returns:
            CFDI model instance

        Raises:
            XMLParseError: If XML is malformed or security issue detected
            InvalidCFDIError: If CFDI structure is invalid
        """
        path = Path(xml_path)

        if not path.exists():
            raise XMLParseError(f"XML file not found: {path}")

        if not path.is_file():
            raise XMLParseError(f"Path is not a file: {path}")

        try:
            content = path.read_text(encoding="utf-8")
            return self.parse_string(content)
        except UnicodeDecodeError as exc:
            raise XMLParseError(f"Invalid UTF-8 encoding: {exc}") from exc
        except OSError as exc:
            raise XMLParseError(f"Failed to read file: {exc}") from exc

    def parse_string(self, xml_content: str) -> CFDI:
        """
        Parse CFDI XML from string.

        Args:
            xml_content: XML content as string

        Returns:
            CFDI model instance

        Raises:
            XMLParseError: If XML is malformed or security issue detected
            InvalidCFDIError: If CFDI structure is invalid
        """
        xml_content = self._sanitizer.sanitize_text(xml_content)
        parser = self._create_secure_parser()

        try:
            root = etree.fromstring(xml_content.encode("utf-8"), parser)
        except etree.XMLSyntaxError as exc:
            raise XMLParseError(f"XML syntax error: {exc}") from exc
        except etree.DocumentInvalid as exc:
            raise XMLParseError(f"XML validation error: {exc}") from exc

        return self._parse_root(root)

    # ── parser creation ───────────────────────────────────────────────────────

    @staticmethod
    def _create_secure_parser() -> etree.XMLParser:
        """Create XML parser with security protections."""
        return etree.XMLParser(
            resolve_entities=False,  # Prevent XXE attacks
            no_network=True,         # Disable network access
            dtd_validation=False,    # Disable DTD validation
            load_dtd=False,          # Don't load DTD
            huge_tree=False,         # Prevent XML bombs
            recover=True,            # Recover from minor errors
        )

    # ── root parser ───────────────────────────────────────────────────────────

    def _parse_root(self, root: etree._Element) -> CFDI:
        """Parse root Comprobante element."""
        if not root.tag.endswith("}Comprobante"):
            raise InvalidCFDIError("Root element is not Comprobante")

        version = self._get_attr(root, "Version")
        if version != "4.0":
            raise InvalidCFDIError(
                f"Unsupported CFDI version: {version}. Only 4.0 is supported."
            )

        return CFDI(
            version=version,
            serie=self._get_optional_attr(root, "Serie"),
            folio=self._get_optional_attr(root, "Folio"),
            fecha=self._get_attr(root, "Fecha"),
            forma_pago=self._get_attr(root, "FormaPago"),
            metodo_pago=self._get_attr(root, "MetodoPago"),
            condiciones_pago=self._get_optional_attr(root, "CondicionesDePago"),
            sub_total=self._get_decimal(root, "SubTotal"),
            descuento=self._get_optional_decimal(root, "Descuento"),
            moneda=self._get_attr(root, "Moneda"),
            tipo_cambio=self._get_optional_decimal(root, "TipoCambio"),
            total=self._get_decimal(root, "Total"),
            tipo_comprobante=self._get_attr(root, "TipoDeComprobante"),
            exportacion=self._get_attr(root, "Exportacion"),
            lugar_expedicion=self._get_attr(root, "LugarExpedicion"),
            confirmacion=self._get_optional_attr(root, "Confirmacion"),
            no_certificado=self._get_attr(root, "NoCertificado"),
            certificado=self._get_attr(root, "Certificado"),
            emisor=self._parse_emisor(root),
            receptor=self._parse_receptor(root),
            conceptos=self._parse_conceptos(root),
            impuestos=self._parse_impuestos_comprobante(root),
            timbre_fiscal=self._parse_timbre_fiscal(root),
            complementos=self._parse_complementos(root),
        )

    # ── sub-element parsers ───────────────────────────────────────────────────

    def _parse_emisor(self, root: etree._Element) -> Emisor:
        """Parse Emisor element."""
        emisor_elem = root.find(f"{{{CFDI_NS}}}Emisor")
        if emisor_elem is None:
            raise InvalidCFDIError("Missing required element: Emisor")

        return Emisor(
            rfc=self._get_attr(emisor_elem, "Rfc"),
            nombre=self._get_attr(emisor_elem, "Nombre"),
            regimen_fiscal=self._get_attr(emisor_elem, "RegimenFiscal"),
        )

    def _parse_receptor(self, root: etree._Element) -> Receptor:
        """Parse Receptor element."""
        receptor_elem = root.find(f"{{{CFDI_NS}}}Receptor")
        if receptor_elem is None:
            raise InvalidCFDIError("Missing required element: Receptor")

        return Receptor(
            rfc=self._get_attr(receptor_elem, "Rfc"),
            nombre=self._get_attr(receptor_elem, "Nombre"),
            domicilio_fiscal=self._get_attr(receptor_elem, "DomicilioFiscalReceptor"),
            regimen_fiscal=self._get_attr(receptor_elem, "RegimenFiscalReceptor"),
            uso_cfdi=self._get_attr(receptor_elem, "UsoCFDI"),
        )

    def _parse_conceptos(self, root: etree._Element) -> list[Concepto]:
        """Parse Conceptos element."""
        conceptos_elem = root.find(f"{{{CFDI_NS}}}Conceptos")
        if conceptos_elem is None:
            raise InvalidCFDIError("Missing required element: Conceptos")

        conceptos = [
            self._parse_concepto(elem)
            for elem in conceptos_elem.findall(f"{{{CFDI_NS}}}Concepto")
        ]

        if not conceptos:
            raise InvalidCFDIError("Conceptos must contain at least one Concepto")

        return conceptos

    def _parse_concepto(self, elem: etree._Element) -> Concepto:
        """Parse individual Concepto element."""
        return Concepto(
            clave_prod_serv=self._get_attr(elem, "ClaveProdServ"),
            cantidad=self._get_decimal(elem, "Cantidad"),
            clave_unidad=self._get_attr(elem, "ClaveUnidad"),
            unidad=self._get_optional_attr(elem, "Unidad"),
            descripcion=self._get_attr(elem, "Descripcion"),
            valor_unitario=self._get_decimal(elem, "ValorUnitario"),
            importe=self._get_decimal(elem, "Importe"),
            descuento=self._get_optional_decimal(elem, "Descuento"),
            objeto_imp=self._get_attr(elem, "ObjetoImp"),
            impuestos=self._parse_impuestos_concepto(elem),
        )

    def _parse_impuestos_concepto(
        self, concepto_elem: etree._Element
    ) -> ImpuestosConcepto | None:
        """Parse taxes at concept level."""
        impuestos_elem = concepto_elem.find(f"{{{CFDI_NS}}}Impuestos")
        if impuestos_elem is None:
            return None

        traslados = self._parse_traslados(impuestos_elem)
        retenciones = self._parse_retenciones_concepto(impuestos_elem)

        if not traslados and not retenciones:
            return None

        return ImpuestosConcepto(traslados=traslados, retenciones=retenciones)

    def _parse_impuestos_comprobante(
        self, root: etree._Element
    ) -> ImpuestosComprobante | None:
        """Parse taxes at comprobante level."""
        impuestos_elem = root.find(f"{{{CFDI_NS}}}Impuestos")
        if impuestos_elem is None:
            return None

        traslados = self._parse_traslados(impuestos_elem)
        retenciones = self._parse_retenciones_comprobante(impuestos_elem)

        return ImpuestosComprobante(
            total_impuestos_trasladados=self._get_optional_decimal(
                impuestos_elem, "TotalImpuestosTrasladados"
            ),
            total_impuestos_retenidos=self._get_optional_decimal(
                impuestos_elem, "TotalImpuestosRetenidos"
            ),
            traslados=traslados,
            retenciones=retenciones,
        )

    def _parse_traslados(self, impuestos_elem: etree._Element) -> list[Traslado]:
        """Parse Traslados sub-element."""
        traslados_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Traslados")
        if traslados_elem is None:
            return []

        return [
            Traslado(
                base=self._get_decimal(elem, "Base"),
                impuesto=self._get_attr(elem, "Impuesto"),
                tipo_factor=self._get_attr(elem, "TipoFactor"),
                tasa_o_cuota=self._get_optional_decimal(elem, "TasaOCuota"),
                importe=self._get_optional_decimal(elem, "Importe"),
            )
            for elem in traslados_elem.findall(f"{{{CFDI_NS}}}Traslado")
        ]

    def _parse_retenciones_concepto(
        self, impuestos_elem: etree._Element
    ) -> list[Retencion]:
        """Parse Retenciones at concept level."""
        retenciones_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Retenciones")
        if retenciones_elem is None:
            return []

        return [
            Retencion(
                base=self._get_optional_decimal(elem, "Base"),
                impuesto=self._get_attr(elem, "Impuesto"),
                tipo_factor=self._get_optional_attr(elem, "TipoFactor"),
                tasa_o_cuota=self._get_optional_decimal(elem, "TasaOCuota"),
                importe=self._get_decimal(elem, "Importe"),
            )
            for elem in retenciones_elem.findall(f"{{{CFDI_NS}}}Retencion")
        ]

    def _parse_retenciones_comprobante(
        self, impuestos_elem: etree._Element
    ) -> list[Retencion]:
        """Parse Retenciones at comprobante level."""
        retenciones_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Retenciones")
        if retenciones_elem is None:
            return []

        return [
            Retencion(
                impuesto=self._get_attr(elem, "Impuesto"),
                importe=self._get_decimal(elem, "Importe"),
            )
            for elem in retenciones_elem.findall(f"{{{CFDI_NS}}}Retencion")
        ]

    def _parse_timbre_fiscal(self, root: etree._Element) -> TimbreFiscalDigital | None:
        """Parse TimbreFiscalDigital from Complemento."""
        complemento_elem = root.find(f"{{{CFDI_NS}}}Complemento")
        if complemento_elem is None:
            return None

        tfd_elem = complemento_elem.find(f"{{{TFD_NS}}}TimbreFiscalDigital")
        if tfd_elem is None:
            return None

        return TimbreFiscalDigital(
            version=self._get_attr(tfd_elem, "Version"),
            uuid=self._get_attr(tfd_elem, "UUID"),
            fecha_timbrado=self._get_attr(tfd_elem, "FechaTimbrado"),
            rfc_prov_certif=self._get_attr(tfd_elem, "RfcProvCertif"),
            sello_cfd=self._get_attr(tfd_elem, "SelloCFD"),
            sello_sat=self._get_attr(tfd_elem, "SelloSAT"),
            no_certificado_sat=self._get_attr(tfd_elem, "NoCertificadoSAT"),
            no_certificado_emisor=self._get_optional_attr(tfd_elem, "NoCertificadoEmisor"),
            cadena_origen=self._build_cadena_original(tfd_elem),
        )

    def _build_cadena_original(self, tfd_elem: etree._Element) -> str:
        """
        Build cadena original from TFD attributes.

        NOTE: In production, this should use the official SAT XSLT transformation.
        This is a simplified version for demonstration purposes.
        """
        parts = [
            self._get_attr(tfd_elem, "Version"),
            self._get_attr(tfd_elem, "UUID"),
            self._get_attr(tfd_elem, "FechaTimbrado"),
            self._get_attr(tfd_elem, "RfcProvCertif"),
            self._get_attr(tfd_elem, "SelloCFD"),
            self._get_attr(tfd_elem, "SelloSAT"),
            self._get_attr(tfd_elem, "NoCertificadoSAT"),
        ]
        return "||" + "|".join(parts) + "||"

    def _parse_complementos(self, root: etree._Element) -> dict[str, dict[str, object]]:
        """Parse additional complementos (Carta Porte, Pagos, Nómina, etc.)."""
        complemento_elem = root.find(f"{{{CFDI_NS}}}Complemento")
        if complemento_elem is None:
            return {}

        complementos: dict[str, dict[str, object]] = {}

        for child in complemento_elem:
            if child.tag.endswith("}TimbreFiscalDigital"):
                continue

            tag = child.tag
            local_name = tag.split("}")[1] if "}" in tag else tag
            complementos[local_name] = self._element_to_dict(child)
            logger.info("Parsed complemento: %s (partial support)", local_name)

        return complementos

    def _element_to_dict(self, elem: etree._Element) -> dict[str, object]:
        """Convert XML element to dictionary (for complementos)."""
        result: dict[str, object] = dict(elem.attrib)

        for child in elem:
            tag = child.tag
            local_name = tag.split("}")[1] if "}" in tag else tag
            child_dict = self._element_to_dict(child)

            existing = result.get(local_name)
            if existing is None:
                result[local_name] = child_dict
            elif isinstance(existing, list):
                existing.append(child_dict)  # type: ignore[union-attr]
            else:
                result[local_name] = [existing, child_dict]

        return result

    # ── attribute helpers (two signatures for required vs optional) ───────────

    def _get_attr(self, elem: etree._Element, attr_name: str) -> str:
        """
        Get a required attribute value with sanitization.

        Raises:
            InvalidCFDIError: If attribute is absent.
        """
        value = elem.get(attr_name)
        if value is None:
            raise InvalidCFDIError(f"Missing required attribute: {attr_name}")
        return self._sanitizer.sanitize_text(value)

    def _get_optional_attr(self, elem: etree._Element, attr_name: str) -> str | None:
        """Get an optional attribute value with sanitization, or None."""
        value = elem.get(attr_name)
        if value is None:
            return None
        return self._sanitizer.sanitize_text(value)

    def _get_decimal(self, elem: etree._Element, attr_name: str) -> Decimal:
        """
        Get a required attribute as Decimal.

        Raises:
            InvalidCFDIError: If attribute is absent or not a valid decimal.
        """
        value_str = self._get_attr(elem, attr_name)
        try:
            return Decimal(value_str)
        except InvalidOperation as exc:
            raise InvalidCFDIError(
                f"Invalid decimal value for {attr_name}: {value_str!r}"
            ) from exc

    def _get_optional_decimal(
        self, elem: etree._Element, attr_name: str
    ) -> Decimal | None:
        """Get an optional attribute as Decimal, or None."""
        value_str = self._get_optional_attr(elem, attr_name)
        if value_str is None:
            return None
        try:
            return Decimal(value_str)
        except InvalidOperation as exc:
            raise InvalidCFDIError(
                f"Invalid decimal value for {attr_name}: {value_str!r}"
            ) from exc
