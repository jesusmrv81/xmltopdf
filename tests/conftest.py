"""Test fixtures for CFDI PDF."""

import pytest


@pytest.fixture
def valid_cfdi_40_xml() -> str:
    """Valid CFDI 4.0 XML sample."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
    xsi:schemaLocation="http://www.sat.gob.mx/cfd/4 http://www.sat.gob.mx/sitio_internet/cfd/4/cfdv40.xsd"
    Version="4.0"
    Serie="A"
    Folio="123"
    Fecha="2024-01-15T10:30:00"
    FormaPago="03"
    MetodoPago="PUE"
    CondicionesDePago="Contado"
    SubTotal="1000.00"
    Descuento="0.00"
    Moneda="MXN"
    TipoCambio="1"
    Total="1160.00"
    TipoDeComprobante="I"
    Exportacion="01"
    LugarExpedicion="06600"
    NoCertificado="30001000000400002495"
    Certificado="MIIE...">
    
    <cfdi:Emisor
        Rfc="AAA010101AAA"
        Nombre="EMPRESA EJEMPLO SA DE CV"
        RegimenFiscal="601"/>
    
    <cfdi:Receptor
        Rfc="XAXX010101000"
        Nombre="PUBLICO EN GENERAL"
        DomicilioFiscalReceptor="06600"
        RegimenFiscalReceptor="616"
        UsoCFDI="S01"/>
    
    <cfdi:Conceptos>
        <cfdi:Concepto
            ClaveProdServ="01010101"
            Cantidad="2"
            ClaveUnidad="E48"
            Unidad="Pieza"
            Descripcion="Producto de ejemplo"
            ValorUnitario="500.00"
            Importe="1000.00"
            Descuento="0.00"
            ObjetoImp="02">
            
            <cfdi:Impuestos>
                <cfdi:Traslados>
                    <cfdi:Traslado
                        Base="1000.00"
                        Impuesto="002"
                        TipoFactor="Tasa"
                        TasaOCuota="0.160000"
                        Importe="160.00"/>
                </cfdi:Traslados>
            </cfdi:Impuestos>
        </cfdi:Concepto>
    </cfdi:Conceptos>
    
    <cfdi:Impuestos TotalImpuestosTrasladados="160.00">
        <cfdi:Traslados>
            <cfdi:Traslado
                Base="1000.00"
                Impuesto="002"
                TipoFactor="Tasa"
                TasaOCuota="0.160000"
                Importe="160.00"/>
        </cfdi:Traslados>
    </cfdi:Impuestos>
    
    <cfdi:Complemento>
        <tfd:TimbreFiscalDigital
            Version="1.1"
            UUID="CCE4D168-1234-5678-9ABC-DEF012345678"
            FechaTimbrado="2024-01-15T10:35:00"
            RfcProvCertif="SPR190613I52"
            SelloCFD="abc123def456ghi789jkl012mno345pqr678stu901vwx234"
            SelloSAT="xyz789abc456def012ghi345jkl678mno901pqr234stu567"
            NoCertificadoSAT="00001000000504465028"/>
    </cfdi:Complemento>
</cfdi:Comprobante>"""


@pytest.fixture
def cfdi_with_retenciones_xml() -> str:
    """CFDI 4.0 with retenciones (withholdings)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0"
    Fecha="2024-01-15T10:30:00"
    FormaPago="03"
    MetodoPago="PUE"
    SubTotal="10000.00"
    Moneda="MXN"
    Total="11600.00"
    TipoDeComprobante="I"
    Exportacion="01"
    LugarExpedicion="06600"
    NoCertificado="30001000000400002495"
    Certificado="MIIE...">
    
    <cfdi:Emisor
        Rfc="AAA010101AAA"
        Nombre="EMPRESA EJEMPLO SA DE CV"
        RegimenFiscal="601"/>
    
    <cfdi:Receptor
        Rfc="BBB010101BBB"
        Nombre="EMPRESA RECEPTORA SA DE CV"
        DomicilioFiscalReceptor="06600"
        RegimenFiscalReceptor="601"
        UsoCFDI="G03"/>
    
    <cfdi:Conceptos>
        <cfdi:Concepto
            ClaveProdServ="84111506"
            Cantidad="1"
            ClaveUnidad="E48"
            Unidad="Servicio"
            Descripcion="Servicios profesionales"
            ValorUnitario="10000.00"
            Importe="10000.00"
            ObjetoImp="02">
            
            <cfdi:Impuestos>
                <cfdi:Traslados>
                    <cfdi:Traslado
                        Base="10000.00"
                        Impuesto="002"
                        TipoFactor="Tasa"
                        TasaOCuota="0.160000"
                        Importe="1600.00"/>
                </cfdi:Traslados>
                <cfdi:Retenciones>
                    <cfdi:Retencion
                        Base="10000.00"
                        Impuesto="001"
                        TipoFactor="Tasa"
                        TasaOCuota="0.100000"
                        Importe="1000.00"/>
                </cfdi:Retenciones>
            </cfdi:Impuestos>
        </cfdi:Concepto>
    </cfdi:Conceptos>
    
    <cfdi:Impuestos TotalImpuestosTrasladados="1600.00" TotalImpuestosRetenidos="1000.00">
        <cfdi:Traslados>
            <cfdi:Traslado
                Base="10000.00"
                Impuesto="002"
                TipoFactor="Tasa"
                TasaOCuota="0.160000"
                Importe="1600.00"/>
        </cfdi:Traslados>
        <cfdi:Retenciones>
            <cfdi:Retencion
                Impuesto="001"
                Importe="1000.00"/>
        </cfdi:Retenciones>
    </cfdi:Impuestos>
    
    <cfdi:Complemento>
        <tfd:TimbreFiscalDigital
            Version="1.1"
            UUID="FFE4D168-5678-1234-ABCD-EF0123456789"
            FechaTimbrado="2024-01-15T10:35:00"
            RfcProvCertif="SPR190613I52"
            SelloCFD="ret123sel456cfd789abc012def345ghi678jkl901mno234"
            SelloSAT="ret789sel456sat012abc345def678ghi901jkl234mno567"
            NoCertificadoSAT="00001000000504465028"/>
    </cfdi:Complemento>
</cfdi:Comprobante>"""


@pytest.fixture
def invalid_xml() -> str:
    """Invalid XML (malformed)."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante xmlns:cfdi="http://www.sat.gob.mx/cfd/4" Version="4.0">
    <cfdi:Emisor Rfc="AAA010101AAA" Nombre="Test"
    <!-- Missing closing tag -->
</cfdi:Comprobante>"""


@pytest.fixture
def cfdi_with_special_chars_xml() -> str:
    """CFDI with special characters and accents."""
    return """<?xml version="1.0" encoding="UTF-8"?>
<cfdi:Comprobante
    xmlns:cfdi="http://www.sat.gob.mx/cfd/4"
    xmlns:tfd="http://www.sat.gob.mx/TimbreFiscalDigital"
    Version="4.0"
    Fecha="2024-01-15T10:30:00"
    FormaPago="03"
    MetodoPago="PUE"
    SubTotal="1000.00"
    Moneda="MXN"
    Total="1160.00"
    TipoDeComprobante="I"
    Exportacion="01"
    LugarExpedicion="06600"
    NoCertificado="30001000000400002495"
    Certificado="MIIE...">
    
    <cfdi:Emisor
        Rfc="AAA010101AAA"
        Nombre="EMPRESA EJEMPLO SA DE CV"
        RegimenFiscal="601"/>
    
    <cfdi:Receptor
        Rfc="XAXX010101000"
        Nombre="PUBLICO EN GENERAL"
        DomicilioFiscalReceptor="06600"
        RegimenFiscalReceptor="616"
        UsoCFDI="S01"/>
    
    <cfdi:Conceptos>
        <cfdi:Concepto
            ClaveProdServ="01010101"
            Cantidad="1"
            ClaveUnidad="E48"
            Unidad="Pieza"
            Descripcion="Producto con acentos: café, niño, año &amp; más"
            ValorUnitario="1000.00"
            Importe="1000.00"
            ObjetoImp="02">
            
            <cfdi:Impuestos>
                <cfdi:Traslados>
                    <cfdi:Traslado
                        Base="1000.00"
                        Impuesto="002"
                        TipoFactor="Tasa"
                        TasaOCuota="0.160000"
                        Importe="160.00"/>
                </cfdi:Traslados>
            </cfdi:Impuestos>
        </cfdi:Concepto>
    </cfdi:Conceptos>
    
    <cfdi:Impuestos TotalImpuestosTrasladados="160.00">
        <cfdi:Traslados>
            <cfdi:Traslado
                Base="1000.00"
                Impuesto="002"
                TipoFactor="Tasa"
                TasaOCuota="0.160000"
                Importe="160.00"/>
        </cfdi:Traslados>
    </cfdi:Impuestos>
    
    <cfdi:Complemento>
        <tfd:TimbreFiscalDigital
            Version="1.1"
            UUID="AAB4D168-9ABC-5678-1234-DEF012345678"
            FechaTimbrado="2024-01-15T10:35:00"
            RfcProvCertif="SPR190613I52"
            SelloCFD="special123chars456test789abc012def345ghi678jkl901"
            SelloSAT="special789chars456test012abc345def678ghi901jkl234"
            NoCertificadoSAT="00001000000504465028"/>
    </cfdi:Complemento>
</cfdi:Comprobante>"""
