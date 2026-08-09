"""Tests para la verificación de sellos digitales (SelloCFD y SelloSAT)."""

import base64
import datetime
import re

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.x509.oid import NameOID

from cfdi_pdf import SelloVerifier
from cfdi_pdf.exceptions import InvalidCFDIError
from cfdi_pdf.parser import CFDIParser


def _make_key_and_cert() -> tuple[rsa.RSAPrivateKey, x509.Certificate]:
    """Genera una llave RSA y un certificado X.509 autofirmado de prueba."""
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "CFDI PDF TEST")])
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(datetime.datetime(2020, 1, 1))
        .not_valid_after(datetime.datetime(2035, 1, 1))
        .sign(key, hashes.SHA256())
    )
    return key, cert


def _sign(cadena_original: str, key: rsa.RSAPrivateKey) -> str:
    """Firma la cadena original (SHA-256 + RSA PKCS#1 v1.5) y la devuelve base64."""
    signature = key.sign(
        cadena_original.encode("utf-8"),
        padding=padding.PKCS1v15(),
        algorithm=hashes.SHA256(),
    )
    return base64.b64encode(signature).decode("ascii")


class TestSelloVerifier:
    """Test suite para SelloVerifier."""

    def _build_signed_xml(self, valid_cfdi_40_xml: str) -> tuple[str, rsa.RSAPrivateKey, str]:
        key, cert = _make_key_and_cert()
        cert_b64 = base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode("ascii")

        xml_base = re.sub(r'Certificado="[^"]*"', f'Certificado="{cert_b64}"', valid_cfdi_40_xml)

        # La cadena original NO incluye el sello ni el certificado, así que puede
        # calcularse antes de firmar.
        cadena = CFDIParser().parse_string(xml_base).cadena_original
        assert cadena is not None

        sello = _sign(cadena, key)
        xml_signed = re.sub(r'SelloCFD="[^"]*"', f'SelloCFD="{sello}"', xml_base)
        return xml_signed, key, sello

    def test_verify_sello_cfd_valid(self, valid_cfdi_40_xml: str) -> None:
        """Un sello firmado sobre la cadena correcta debe verificarse."""
        xml_signed, _key, _sello = self._build_signed_xml(valid_cfdi_40_xml)
        cfdi = CFDIParser().parse_string(xml_signed)

        assert SelloVerifier.verify_sello_cfd(cfdi) is True

    def test_verify_sello_cfd_tampered(self, valid_cfdi_40_xml: str) -> None:
        """Si se altera el documento, la firma ya no corresponde."""
        xml_signed, _key, _sello = self._build_signed_xml(valid_cfdi_40_xml)
        tampered = xml_signed.replace('Total="1160.00"', 'Total="9999.99"')
        cfdi = CFDIParser().parse_string(tampered)

        assert SelloVerifier.verify_sello_cfd(cfdi) is False

    def test_verify_sello_cfd_wrong_signature(self, valid_cfdi_40_xml: str) -> None:
        """Un sello aleatorio no debe verificarse."""
        xml_signed, _key, _sello = self._build_signed_xml(valid_cfdi_40_xml)
        bad_sello = base64.b64encode(b"x" * 256).decode("ascii")
        corrupted = re.sub(r'SelloCFD="[^"]*"', f'SelloCFD="{bad_sello}"', xml_signed)
        cfdi = CFDIParser().parse_string(corrupted)

        assert SelloVerifier.verify_sello_cfd(cfdi) is False

    def test_verify_sello_sat_valid(self, valid_cfdi_40_xml: str) -> None:
        """Verificación de SelloSAT contra la cadena del timbre."""
        key, cert = _make_key_and_cert()
        cert_b64 = base64.b64encode(cert.public_bytes(serialization.Encoding.DER)).decode("ascii")

        # Cadena del timbre (calculada por el parser con la XSLT oficial)
        tfd_cadena = CFDIParser().parse_string(valid_cfdi_40_xml).timbre_fiscal.cadena_origen
        assert tfd_cadena is not None

        sello_sat = _sign(tfd_cadena, key)
        xml_signed = re.sub(r'SelloSAT="[^"]*"', f'SelloSAT="{sello_sat}"', valid_cfdi_40_xml)
        cfdi = CFDIParser().parse_string(xml_signed)

        assert SelloVerifier.verify_sello_sat(cfdi, cert_b64) is True

    def test_verify_requires_timbre(self, valid_cfdi_40_xml: str) -> None:
        """Sin timbre fiscal, la verificación debe lanzar InvalidCFDIError."""
        from lxml import etree

        root = etree.fromstring(valid_cfdi_40_xml.encode("utf-8"))
        complemento = root.find("{http://www.sat.gob.mx/cfd/4}Complemento")
        if complemento is not None:
            root.remove(complemento)
        no_timbre = etree.tostring(root, encoding="unicode")

        cfdi = CFDIParser().parse_string(no_timbre)
        with pytest.raises(InvalidCFDIError):
            SelloVerifier.verify_sello_cfd(cfdi)
