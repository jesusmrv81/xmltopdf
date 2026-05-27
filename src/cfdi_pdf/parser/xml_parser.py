"""Secure XML parser for CFDI 4.0 documents."""

import logging
from decimal import Decimal
from pathlib import Path
from typing import Any

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
        except UnicodeDecodeError as e:
            raise XMLParseError(f"Invalid UTF-8 encoding: {e}")
        except OSError as e:
            raise XMLParseError(f"Failed to read file: {e}")

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
        # Sanitize content
        xml_content = self._sanitizer.sanitize_text(xml_content)

        # Create secure parser
        parser = self._create_secure_parser()

        try:
            root = etree.fromstring(xml_content.encode("utf-8"), parser)
        except etree.XMLSyntaxError as e:
            raise XMLParseError(f"XML syntax error: {e}")
        except etree.DocumentInvalid as e:
            raise XMLParseError(f"XML validation error: {e}")

        return self._parse_root(root)

    def _create_secure_parser(self) -> etree.XMLParser:
        """Create XML parser with security protections."""
        return etree.XMLParser(
            resolve_entities=False,  # Prevent XXE attacks
            no_network=True,  # Disable network access
            dtd_validation=False,  # Disable DTD validation
            load_dtd=False,  # Don't load DTD
            huge_tree=False,  # Prevent XML bombs
            recover=True,  # Recover from minor errors
        )

    def _parse_root(self, root: etree._Element) -> CFDI:
        """Parse root Comprobante element."""
        # Validate namespace
        if not root.tag.endswith("}Comprobante"):
            raise InvalidCFDIError("Root element is not Comprobante")

        # Extract version
        version = self._get_attr(root, "Version")
        if version != "4.0":
            raise InvalidCFDIError(f"Unsupported CFDI version: {version}. Only 4.0 is supported.")

        # Parse all components
        emisor = self._parse_emisor(root)
        receptor = self._parse_receptor(root)
        conceptos = self._parse_conceptos(root)
        impuestos = self._parse_impuestos_comprobante(root)
        timbre = self._parse_timbre_fiscal(root)
        complementos = self._parse_complementos(root)

        # Build CFDI model
        return CFDI(
            version=version,
            serie=self._get_attr(root, "Serie", required=False),
            folio=self._get_attr(root, "Folio", required=False),
            fecha=self._get_attr(root, "Fecha"),
            forma_pago=self._get_attr(root, "FormaPago"),
            metodo_pago=self._get_attr(root, "MetodoPago"),
            condiciones_pago=self._get_attr(root, "CondicionesDePago", required=False),
            sub_total=self._get_decimal(root, "SubTotal"),
            descuento=self._get_decimal(root, "Descuento", required=False),
            moneda=self._get_attr(root, "Moneda"),
            tipo_cambio=self._get_decimal(root, "TipoCambio", required=False),
            total=self._get_decimal(root, "Total"),
            tipo_comprobante=self._get_attr(root, "TipoDeComprobante"),
            exportacion=self._get_attr(root, "Exportacion"),
            lugar_expedicion=self._get_attr(root, "LugarExpedicion"),
            confirmacion=self._get_attr(root, "Confirmacion", required=False),
            no_certificado=self._get_attr(root, "NoCertificado"),
            certificado=self._get_attr(root, "Certificado"),
            emisor=emisor,
            receptor=receptor,
            conceptos=conceptos,
            impuestos=impuestos,
            timbre_fiscal=timbre,
            complementos=complementos,
        )

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

        conceptos = []
        for concepto_elem in conceptos_elem.findall(f"{{{CFDI_NS}}}Concepto"):
            concepto = self._parse_concepto(concepto_elem)
            conceptos.append(concepto)

        if not conceptos:
            raise InvalidCFDIError("Conceptos must contain at least one Concepto")

        return conceptos

    def _parse_concepto(self, elem: etree._Element) -> Concepto:
        """Parse individual Concepto element."""
        impuestos = self._parse_impuestos_concepto(elem)

        return Concepto(
            clave_prod_serv=self._get_attr(elem, "ClaveProdServ"),
            cantidad=self._get_decimal(elem, "Cantidad"),
            clave_unidad=self._get_attr(elem, "ClaveUnidad"),
            unidad=self._get_attr(elem, "Unidad", required=False),
            descripcion=self._get_attr(elem, "Descripcion"),
            valor_unitario=self._get_decimal(elem, "ValorUnitario"),
            importe=self._get_decimal(elem, "Importe"),
            descuento=self._get_decimal(elem, "Descuento", required=False),
            objeto_imp=self._get_attr(elem, "ObjetoImp"),
            impuestos=impuestos,
        )

    def _parse_impuestos_concepto(self, concepto_elem: etree._Element) -> ImpuestosConcepto | None:
        """Parse taxes at concept level."""
        impuestos_elem = concepto_elem.find(f"{{{CFDI_NS}}}Impuestos")
        if impuestos_elem is None:
            return None

        traslados = []
        retenciones = []

        # Parse traslados
        traslados_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Traslados")
        if traslados_elem is not None:
            for traslado_elem in traslados_elem.findall(f"{{{CFDI_NS}}}Traslado"):
                traslados.append(
                    Traslado(
                        base=self._get_decimal(traslado_elem, "Base"),
                        impuesto=self._get_attr(traslado_elem, "Impuesto"),
                        tipo_factor=self._get_attr(traslado_elem, "TipoFactor"),
                        tasa_o_cuota=self._get_decimal(traslado_elem, "TasaOCuota", required=False),
                        importe=self._get_decimal(traslado_elem, "Importe", required=False),
                    )
                )

        # Parse retenciones
        retenciones_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Retenciones")
        if retenciones_elem is not None:
            for retencion_elem in retenciones_elem.findall(f"{{{CFDI_NS}}}Retencion"):
                retenciones.append(
                    Retencion(
                        base=self._get_decimal(retencion_elem, "Base", required=False),
                        impuesto=self._get_attr(retencion_elem, "Impuesto"),
                        tipo_factor=self._get_attr(retencion_elem, "TipoFactor", required=False),
                        tasa_o_cuota=self._get_decimal(
                            retencion_elem, "TasaOCuota", required=False
                        ),
                        importe=self._get_decimal(retencion_elem, "Importe"),
                    )
                )

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

        traslados = []
        retenciones = []

        # Parse traslados
        traslados_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Traslados")
        if traslados_elem is not None:
            for traslado_elem in traslados_elem.findall(f"{{{CFDI_NS}}}Traslado"):
                traslados.append(
                    Traslado(
                        base=self._get_decimal(traslado_elem, "Base"),
                        impuesto=self._get_attr(traslado_elem, "Impuesto"),
                        tipo_factor=self._get_attr(traslado_elem, "TipoFactor"),
                        tasa_o_cuota=self._get_decimal(traslado_elem, "TasaOCuota", required=False),
                        importe=self._get_decimal(traslado_elem, "Importe", required=False),
                    )
                )

        # Parse retenciones
        retenciones_elem = impuestos_elem.find(f"{{{CFDI_NS}}}Retenciones")
        if retenciones_elem is not None:
            for retencion_elem in retenciones_elem.findall(f"{{{CFDI_NS}}}Retencion"):
                retenciones.append(
                    Retencion(
                        impuesto=self._get_attr(retencion_elem, "Impuesto"),
                        importe=self._get_decimal(retencion_elem, "Importe"),
                    )
                )

        return ImpuestosComprobante(
            total_impuestos_trasladados=self._get_decimal(
                impuestos_elem, "TotalImpuestosTrasladados", required=False
            ),
            total_impuestos_retenidos=self._get_decimal(
                impuestos_elem, "TotalImpuestosRetenidos", required=False
            ),
            traslados=traslados,
            retenciones=retenciones,
        )

    def _parse_timbre_fiscal(self, root: etree._Element) -> TimbreFiscalDigital | None:
        """Parse TimbreFiscalDigital from Complemento."""
        complemento_elem = root.find(f"{{{CFDI_NS}}}Complemento")
        if complemento_elem is None:
            return None

        tfd_elem = complemento_elem.find(f"{{{TFD_NS}}}TimbreFiscalDigital")
        if tfd_elem is None:
            return None

        # Build cadena original (simplified - in production, use XSLT)
        cadena_origen = self._build_cadena_original(tfd_elem)

        return TimbreFiscalDigital(
            version=self._get_attr(tfd_elem, "Version"),
            uuid=self._get_attr(tfd_elem, "UUID"),
            fecha_timbrado=self._get_attr(tfd_elem, "FechaTimbrado"),
            rfc_prov_certif=self._get_attr(tfd_elem, "RfcProvCertif"),
            sello_cfd=self._get_attr(tfd_elem, "SelloCFD"),
            sello_sat=self._get_attr(tfd_elem, "SelloSAT"),
            no_certificado_sat=self._get_attr(tfd_elem, "NoCertificadoSAT"),
            no_certificado_emisor=self._get_attr(tfd_elem, "NoCertificadoEmisor", required=False),
            cadena_origen=cadena_origen,
        )

    def _build_cadena_original(self, tfd_elem: etree._Element) -> str:
        """
        Build cadena original from TFD attributes.

        NOTE: In production, this should use the official XSLT transformation.
        This is a simplified version for demonstration.
        """
        # Official format: ||version|uuid|fecha_timbrado|rfc_prov_certif|sello_cfd|sello_sat|no_certificado_sat||
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

    def _parse_complementos(self, root: etree._Element) -> dict[str, dict]:
        """Parse additional complementos (Carta Porte, Pagos, Nómina, etc.)."""
        complemento_elem = root.find(f"{{{CFDI_NS}}}Complemento")
        if complemento_elem is None:
            return {}

        complementos = {}

        # Iterate through all children except TFD
        for child in complemento_elem:
            if child.tag.endswith("}TimbreFiscalDigital"):
                continue

            # Extract local name
            tag = child.tag
            if "}" in tag:
                local_name = tag.split("}")[1]
            else:
                local_name = tag

            # Parse as generic dict (partial support)
            complementos[local_name] = self._element_to_dict(child)
            logger.info(f"Parsed complemento: {local_name} (partial support)")

        return complementos

    def _element_to_dict(self, elem: etree._Element) -> dict:
        """Convert XML element to dictionary (for complementos)."""
        result = {}

        # Add attributes
        for key, value in elem.attrib.items():
            result[key] = value

        # Add child elements
        for child in elem:
            child_dict = self._element_to_dict(child)
            if "}" in child.tag:
                tag = child.tag.split("}")[1]
            else:
                tag = child.tag

            if tag in result:
                # Convert to list if multiple children with same tag
                if not isinstance(result[tag], list):
                    result[tag] = [result[tag]]
                result[tag].append(child_dict)
            else:
                result[tag] = child_dict

        return result

    def _get_attr(
        self, elem: etree._Element, attr_name: str, required: bool = True
    ) -> str:
        """Get attribute value with sanitization."""
        value = elem.get(attr_name)

        if value is None:
            if required:
                raise InvalidCFDIError(f"Missing required attribute: {attr_name}")
            return None  # type: ignore

        return self._sanitizer.sanitize_text(value)

    def _get_decimal(
        self, elem: etree._Element, attr_name: str, required: bool = True
    ) -> Decimal | None:
        """Get attribute as Decimal."""
        value_str = self._get_attr(elem, attr_name, required)

        if value_str is None:
            return None

        try:
            return Decimal(value_str)
        except Exception as e:
            raise InvalidCFDIError(f"Invalid decimal value for {attr_name}: {value_str}") from e
