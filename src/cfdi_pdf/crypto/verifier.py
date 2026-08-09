"""Verificación de los sellos digitales de un CFDI 4.0.

La cadena original del comprobante se genera en el parser usando la XSLT
oficial ``cadenaoriginal_4_0.xslt``; la del timbre con
``cadenaoriginal_TFD_1_1.xslt``. El sello se valida con RSA (PKCS#1 v1.5)
contra el hash SHA-256 de la cadena original.
"""

import base64
import logging
import re
from typing import TYPE_CHECKING

from cryptography import x509
from cryptography.exceptions import InvalidSignature, UnsupportedAlgorithm
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from ..exceptions import InvalidCFDIError

if TYPE_CHECKING:
    from ..models import CFDI

logger = logging.getLogger(__name__)

# Base64 puede traer saltos de línea/espacios dentro del atributo
_WHITESPACE = re.compile(r"\s+")


class SelloVerifier:
    """Verifica ``SelloCFD`` (emisor) y ``SelloSAT`` contra su cadena original."""

    @staticmethod
    def verify_sello_cfd(cfdi: "CFDI") -> bool:
        """
        Verifica la firma del emisor (``SelloCFD``).

        Usa el certificado embebido en el atributo ``Certificado`` del CFDI y
        la cadena original del comprobante calculada por el parser.

        Raises:
            InvalidCFDIError: si el CFDI no tiene timbre, certificado o cadena.
        """
        if cfdi.timbre_fiscal is None:
            raise InvalidCFDIError("CFDI incompleto para verificar SelloCFD: falta timbre fiscal")
        if not cfdi.certificado:
            raise InvalidCFDIError("CFDI incompleto para verificar SelloCFD: falta Certificado")
        if not cfdi.cadena_original:
            raise InvalidCFDIError("CFDI incompleto para verificar SelloCFD: falta cadena original")

        return _verify_signature(
            cadena_original=cfdi.cadena_original,
            sello=cfdi.timbre_fiscal.sello_cfd,
            certificate_der=base64.b64decode(_WHITESPACE.sub("", cfdi.certificado)),
        )

    @staticmethod
    def verify_sello_sat(cfdi: "CFDI", sat_certificate: str | bytes) -> bool:
        """
        Verifica la firma del SAT (``SelloSAT``).

        El certificado del SAT no está embebido en el XML; debe pasarse el
        certificado X.509 del SAT identificado por ``NoCertificadoSAT``. Se
        acepta en formato PEM (``-----BEGIN CERTIFICATE-----``), DER (bytes) o
        base64 (como el atributo ``Certificado`` de un CFDI).

        Raises:
            InvalidCFDIError: si el CFDI no tiene timbre o el certificado es inválido.
        """
        if cfdi.timbre_fiscal is None:
            raise InvalidCFDIError("CFDI incompleto para verificar SelloSAT: falta timbre fiscal")
        if not cfdi.timbre_fiscal.cadena_origen:
            raise InvalidCFDIError(
                "CFDI incompleto para verificar SelloSAT: falta cadena original del timbre"
            )

        certificate_der = _certificate_to_der(sat_certificate)
        return _verify_signature(
            cadena_original=cfdi.timbre_fiscal.cadena_origen,
            sello=cfdi.timbre_fiscal.sello_sat,
            certificate_der=certificate_der,
        )


def _certificate_to_der(certificate: str | bytes) -> bytes:
    """Convierte un certificado PEM / DER / base64 a bytes DER."""
    if isinstance(certificate, bytes):
        # Bytes: puede ser PEM o DER.
        if certificate.lstrip().startswith(b"-----BEGIN"):
            return x509.load_pem_x509_certificate(certificate).public_bytes(
                serialization.Encoding.DER
            )
        return certificate
    # String: puede ser PEM o base64.
    if "-----BEGIN CERTIFICATE-----" in certificate:
        return x509.load_pem_x509_certificate(certificate.encode("utf-8")).public_bytes(
            serialization.Encoding.DER
        )
    return base64.b64decode(_WHITESPACE.sub("", certificate))


def _verify_signature(cadena_original: str, sello: str, certificate_der: bytes) -> bool:
    """Verifica RSA PKCS#1 v1.5 + SHA-256 (con fallback a SHA-1)."""
    try:
        certificate = x509.load_der_x509_certificate(certificate_der)
    except (ValueError, TypeError) as exc:
        raise InvalidCFDIError(f"Certificado X.509 inválido: {exc}") from exc

    public_key = certificate.public_key()
    if not isinstance(public_key, rsa.RSAPublicKey):
        logger.warning("El certificado no usa RSA; no se puede verificar el sello")
        return False

    try:
        signature = base64.b64decode(sello)
    except ValueError as exc:
        raise InvalidCFDIError("Sello no es base64 válido") from exc

    data = cadena_original.encode("utf-8")
    for algorithm in (hashes.SHA256(), hashes.SHA1()):
        try:
            public_key.verify(
                signature=signature,
                data=data,
                padding=padding.PKCS1v15(),
                algorithm=algorithm,
            )
            return True
        except InvalidSignature:
            continue
        except UnsupportedAlgorithm:
            continue
    return False
