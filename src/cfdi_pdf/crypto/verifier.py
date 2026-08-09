"""Verificación de los sellos digitales de un CFDI 4.0.

La cadena original del comprobante se genera en el parser usando la XSLT
oficial ``cadenaoriginal_4_0.xslt``; la del timbre con
``cadenaoriginal_TFD_1_1.xslt``. El sello se valida con RSA (PKCS#1 v1.5)
contra el hash SHA-256 de la cadena original.

Para ``verify_sello_sat`` se puede pasar el certificado del SAT directamente o
dejarlo en el **store de certificados** (``~/.cache/cfdi-pdf/certs/`` o la
variable ``CFDI_PDF_SAT_CERTS_DIR``); se buscará el que coincida con
``NoCertificadoSAT`` por número de serie.
"""

import base64
import logging
import os
import re
from pathlib import Path
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


def get_sat_cert_store_dir() -> Path:
    """Directorio del store de certificados SAT (override con CFDI_PDF_SAT_CERTS_DIR)."""
    env = os.environ.get("CFDI_PDF_SAT_CERTS_DIR")
    if env:
        return Path(env).expanduser()
    from ..sat.resources import default_cache_dir

    return default_cache_dir() / "certs"


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
    def verify_sello_sat(cfdi: "CFDI", sat_certificate: str | bytes | None = None) -> bool:
        """
        Verifica la firma del SAT (``SelloSAT``).

        El certificado del SAT no está embebido en el XML. Se acepta:

        - ``sat_certificate`` explícito: PEM, DER (bytes) o base64 (como el
          atributo ``Certificado`` de un CFDI).
        - ``None``: se busca en el store de certificados (``get_sat_cert_store_dir``)
          el certificado cuyo número de serie coincida con ``NoCertificadoSAT``.

        Raises:
            InvalidCFDIError: si el CFDI no tiene timbre, no se encuentra el
                certificado o el certificado es inválido.
        """
        if cfdi.timbre_fiscal is None:
            raise InvalidCFDIError("CFDI incompleto para verificar SelloSAT: falta timbre fiscal")
        if not cfdi.timbre_fiscal.cadena_origen:
            raise InvalidCFDIError(
                "CFDI incompleto para verificar SelloSAT: falta cadena original del timbre"
            )

        if sat_certificate is not None:
            certificate_der = _certificate_to_der(sat_certificate)
        else:
            certificate_der = _find_sat_certificate(cfdi.timbre_fiscal.no_certificado_sat)

        return _verify_signature(
            cadena_original=cfdi.timbre_fiscal.cadena_origen,
            sello=cfdi.timbre_fiscal.sello_sat,
            certificate_der=certificate_der,
        )


def _find_sat_certificate(no_certificado_sat: str) -> bytes:
    """Busca en el store un certificado SAT cuyo número de serie coincida."""
    store_dir = get_sat_cert_store_dir()
    serial = _WHITESPACE.sub("", no_certificado_sat).upper()

    if not store_dir.is_dir():
        raise InvalidCFDIError(
            "No se encontró el certificado SAT: el store "
            f"'{store_dir}' no existe. Proporciona el certificado en "
            "verify_sello_sat(cfdi, cert) o agrega el PEM a ese directorio."
        )

    for path in sorted(store_dir.iterdir()):
        if not path.is_file():
            continue
        try:
            certificate = _load_certificate(path.read_bytes())
        except (ValueError, TypeError):
            continue
        serial_decimal = str(certificate.serial_number).upper()
        serial_hex = format(certificate.serial_number, "X")
        if serial in (serial_decimal, serial_hex, serial_hex.zfill(len(serial))):
            return certificate.public_bytes(serialization.Encoding.DER)

    raise InvalidCFDIError(
        f"No se encontró el certificado SAT con serie {no_certificado_sat} "
        f"en el store '{store_dir}'"
    )


def _load_certificate(data: bytes) -> x509.Certificate:
    """Carga un certificado PEM o DER."""
    if data.lstrip().startswith(b"-----BEGIN"):
        return x509.load_pem_x509_certificate(data)
    return x509.load_der_x509_certificate(data)


def _certificate_to_der(certificate: str | bytes) -> bytes:
    """Convierte un certificado PEM / DER / base64 a bytes DER."""
    if isinstance(certificate, bytes):
        return _load_certificate(certificate).public_bytes(serialization.Encoding.DER)
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
