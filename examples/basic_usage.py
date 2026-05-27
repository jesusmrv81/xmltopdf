"""
Uso básico de CFDI PDF
"""

from pathlib import Path

from cfdi_pdf import CFDIPDF


def basic_conversion():
    """Conversión básica de XML a PDF"""
    # Inicializar con template por defecto
    pdf = CFDIPDF(template="minimal")
    
    # Convertir desde archivo
    pdf.render(
        xml_path="factura.xml",
        output="factura.pdf"
    )
    print("✓ PDF generado: factura.pdf")


def conversion_from_string():
    """Conversión desde string XML"""
    pdf = CFDIPDF()
    
    # Leer XML como string
    with open("factura.xml", "r", encoding="utf-8") as f:
        xml_content = f.read()
    
    # Convertir y obtener bytes
    pdf_bytes = pdf.render_from_string(xml_content)
    
    # Guardar resultado
    with open("factura.pdf", "wb") as f:
        f.write(pdf_bytes)
    
    print(f"✓ PDF generado: {len(pdf_bytes)} bytes")


def conversion_with_logo():
    """Conversión con logo personalizado"""
    pdf = CFDIPDF()
    
    pdf.render(
        xml_path="factura.xml",
        output="factura.pdf",
        logo_path="logo.png"
    )
    print("✓ PDF generado con logo")


def access_cfdi_data():
    """Acceder a datos del CFDI sin generar PDF"""
    pdf = CFDIPDF()
    
    # Parsear XML
    cfdi = pdf.parse("factura.xml")
    
    # Acceder a datos
    print(f"UUID: {cfdi.uuid}")
    print(f"Versión: {cfdi.version}")
    print(f"Fecha: {cfdi.fecha}")
    print(f"Lugar de expedición: {cfdi.lugar_expedicion}")
    
    # Emisor
    print(f"\nEmisor:")
    print(f"  RFC: {cfdi.emisor.rfc}")
    print(f"  Nombre: {cfdi.emisor.nombre}")
    print(f"  Régimen: {cfdi.emisor.regimen_fiscal}")
    
    # Receptor
    print(f"\nReceptor:")
    print(f"  RFC: {cfdi.receptor.rfc}")
    print(f"  Nombre: {cfdi.receptor.nombre}")
    print(f"  Uso CFDI: {cfdi.receptor.uso_cfdi}")
    
    # Totales
    print(f"\nTotales:")
    print(f"  Subtotal: ${cfdi.subtotal:,.2f}")
    if cfdi.descuento:
        print(f"  Descuento: ${cfdi.descuento:,.2f}")
    print(f"  Moneda: {cfdi.moneda}")
    print(f"  Total: ${cfdi.total:,.2f}")
    
    # Conceptos
    print(f"\nConceptos ({len(cfdi.conceptos)}):")
    for i, concepto in enumerate(cfdi.conceptos, 1):
        print(f"\n  {i}. {concepto.descripcion}")
        print(f"     Cantidad: {concepto.cantidad}")
        print(f"     Unidad: {concepto.unidad}")
        print(f"     Precio unitario: ${concepto.valor_unitario:,.2f}")
        print(f"     Importe: ${concepto.importe:,.2f}")
    
    # Impuestos
    if cfdi.impuestos:
        print(f"\nImpuestos:")
        
        if cfdi.impuestos.traslados:
            print(f"\n  Traslados:")
            for traslado in cfdi.impuestos.traslados:
                tasa = traslado.tasa_o_cuota * 100
                print(f"    {traslado.impuesto} {tasa}%: ${traslado.importe:,.2f}")
        
        if cfdi.impuestos.retenciones:
            print(f"\n  Retenciones:")
            for retencion in cfdi.impuestos.retenciones:
                tasa = retencion.tasa_o_cuota * 100
                print(f"    {retencion.impuesto} {tasa}%: ${retencion.importe:,.2f}")
    
    # Timbre Fiscal Digital
    if cfdi.timbre_fiscal:
        print(f"\nTimbre Fiscal Digital:")
        print(f"  Versión: {cfdi.timbre_fiscal.version}")
        print(f"  UUID: {cfdi.timbre_fiscal.uuid}")
        print(f"  Fecha timbrado: {cfdi.timbre_fiscal.fecha_timbrado}")
        print(f"  PAC: {cfdi.timbre_fiscal.rfc_prov_certif}")
        print(f"  Certificado SAT: {cfdi.timbre_fiscal.no_certificado_sat}")


def list_available_templates():
    """Listar templates disponibles"""
    pdf = CFDIPDF()
    templates = pdf.list_templates()
    
    print("Templates disponibles:")
    for template in templates:
        print(f"  - {template}")


if __name__ == "__main__":
    # Ejemplo básico
    print("=== Conversión Básica ===")
    basic_conversion()
    
    # Listar templates
    print("\n=== Templates Disponibles ===")
    list_available_templates()
    
    # Acceder a datos
    print("\n=== Datos del CFDI ===")
    access_cfdi_data()
