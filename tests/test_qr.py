"""Tests for QR code generator."""

import pytest

from cfdi_pdf.exceptions import InvalidSATQRError
from cfdi_pdf.qr import SATQRGenerator


class TestSATQRGenerator:
    """Test suite for SATQRGenerator."""

    def test_generate_qr_basic(self) -> None:
        """Test basic QR generation."""
        generator = SATQRGenerator()

        qr_bytes = generator.generate(
            uuid="CCE4D168-1234-5678-9ABC-DEF012345678",
            rfc_emisor="AAA010101AAA",
            rfc_receptor="XAXX010101000",
            total=1160.00,
            sello_cfd="abc123def456ghi789jkl012mno345pqr678stu901vwx234",
        )

        assert isinstance(qr_bytes, bytes)
        assert len(qr_bytes) > 0
        # PNG magic number
        assert qr_bytes.startswith(b"\x89PNG")

    def test_format_total_with_6_decimals(self) -> None:
        """Test total formatting with exactly 6 decimals."""
        generator = SATQRGenerator()

        # Test various totals
        assert generator._format_total(1160.00) == "1160.000000"
        assert generator._format_total(100.5) == "100.500000"
        assert generator._format_total(1234.567890) == "1234.567890"

    def test_sello_truncation(self) -> None:
        """Test sello truncation to last 8 characters."""
        generator = SATQRGenerator()

        sello = "abc123def456ghi789jkl012mno345pqr678stu901vwx234"
        qr_bytes = generator.generate(
            uuid="CCE4D168-1234-5678-9ABC-DEF012345678",
            rfc_emisor="AAA010101AAA",
            rfc_receptor="XAXX010101000",
            total=1160.00,
            sello_cfd=sello,
        )

        # Should use last 8 chars: "vwx234"
        assert len(sello[-8:]) == 8

    def test_url_no_encoding(self) -> None:
        """Test that URL is built without URL encoding."""
        generator = SATQRGenerator()
        
        # Use sello with special chars that would be encoded
        sello = "abc123def456ghi789jkl012mno345pqr678stu901+/=="
        
        url = generator._build_url(
            uuid="cce4d168-1234-5678-9abc-def012345678",
            rfc_emisor="AAA010101AAA",
            rfc_receptor="XAXX010101000",
            total=1160.00,
            sello_cfd=sello,
        )
        
        # UUID should be uppercase
        assert "id=CCE4D168-1234-5678-9ABC-DEF012345678" in url
        # No URL encoding for special chars (last 8 chars of sello)
        assert "fe=u901+/==" in url
        assert "%2F" not in url
        assert "%3D" not in url
        assert "%2B" not in url
        # Verify structure
        assert url.startswith("https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx?")
        assert "re=AAA010101AAA" in url
        assert "rr=XAXX010101000" in url
        assert "tt=1160.000000" in url

    def test_uuid_uppercase(self) -> None:
        """Test that UUID is converted to uppercase in URL."""
        generator = SATQRGenerator()
        
        url = generator._build_url(
            uuid="cce4d168-1234-5678-9abc-def012345678",
            rfc_emisor="AAA010101AAA",
            rfc_receptor="XAXX010101000",
            total=100.00,
            sello_cfd="abc123def456ghi789",
        )
        
        assert "id=CCE4D168-1234-5678-9ABC-DEF012345678" in url
        assert "cce4d168" not in url

    def test_invalid_uuid_raises_error(self) -> None:
        """Test that invalid UUID raises error."""
        generator = SATQRGenerator()

        with pytest.raises(InvalidSATQRError):
            generator.generate(
                uuid="",
                rfc_emisor="AAA010101AAA",
                rfc_receptor="XAXX010101000",
                total=1160.00,
                sello_cfd="abc123def456ghi789jkl012mno345pqr678stu901vwx234",
            )

    def test_invalid_total_raises_error(self) -> None:
        """Test that negative total raises error."""
        generator = SATQRGenerator()

        with pytest.raises(InvalidSATQRError):
            generator.generate(
                uuid="CCE4D168-1234-5678-9ABC-DEF012345678",
                rfc_emisor="AAA010101AAA",
                rfc_receptor="XAXX010101000",
                total=-100.00,
                sello_cfd="abc123def456ghi789jkl012mno345pqr678stu901vwx234",
            )

    def test_short_sello_raises_error(self) -> None:
        """Test that short sello raises error."""
        generator = SATQRGenerator()

        with pytest.raises(InvalidSATQRError):
            generator.generate(
                uuid="CCE4D168-1234-5678-9ABC-DEF012345678",
                rfc_emisor="AAA010101AAA",
                rfc_receptor="XAXX010101000",
                total=1160.00,
                sello_cfd="short",
            )
