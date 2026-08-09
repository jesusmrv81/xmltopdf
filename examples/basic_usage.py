"""
Uso básico de CFDI PDF.
"""

from pathlib import Path

from cfdi_pdf import CFDIPDF


def basic_conversion() -> None:
    """Conversión básica de XML a PDF (guarda {uuid}.pdf junto al XML)."""
    pdf = CFDIPDF(template="minimal")
    output_path = pdf.render(xml_path="factura.xml")
    print(f"✓ PDF generado: {output_path}")


def conversion_to_directory() -> None:
    """Especificar un directorio de salida."""
    pdf = CFDIPDF()
    output_path = pdf.render(xml_path="factura.xml", output_dir=Path("./pdfs"))
    print(f"✓ PDF generado: {output_path}")


def conversion_from_string() -> None:
    """Conversión desde un string XML."""
    pdf = CFDIPDF()

    with open("factura.xml", encoding="utf-8") as f:
        xml_content = f.read()

    output_path = pdf.render_from_string(xml_content, output_dir="./pdfs")
    print(f"✓ PDF generado: {output_path}")


def conversion_to_bytes() -> None:
    """Obtener bytes sin escribir a disco (útil para APIs web)."""
    pdf = CFDIPDF()

    with open("factura.xml", encoding="utf-8") as f:
        xml_content = f.read()

    pdf_bytes, filename = pdf.render_bytes_from_string(xml_content)
    print(f"✓ {len(pdf_bytes)} bytes, archivo sugerido: {filename}")


def conversion_with_logo() -> None:
    """Conversión con logo personalizado."""
    pdf = CFDIPDF()
    output_path = pdf.render(xml_path="factura.xml", output_dir="./pdfs", logo_path="logo.png")
    print(f"✓ PDF generado con logo: {output_path}")


def access_cfdi_data() -> None:
    """Acceder a los datos del CFDI sin generar PDF."""
    pdf = CFDIPDF()
    cfdi = pdf.parse("factura.xml")

    tfd = cfdi.timbre_fiscal
    print(f"UUID: {tfd.uuid if tfd else 'N/A'}")
    print(f"Versión: {cfdi.version}")
    print(f"Fecha: {cfdi.fecha}")
    print(f"Lugar de expedición: {cfdi.lugar_expedicion}")

    print("\nEmisor:")
    print(f"  RFC: {cfdi.emisor.rfc}")
    print(f"  Nombre: {cfdi.emisor.nombre}")
    print(f"  Régimen: {cfdi.emisor.regimen_fiscal}")

    print("\nReceptor:")
    print(f"  RFC: {cfdi.receptor.rfc}")
    print(f"  Nombre: {cfdi.receptor.nombre}")
    print(f"  Uso CFDI: {cfdi.receptor.uso_cfdi}")

    print("\nTotales:")
    print(f"  Subtotal: {cfdi.sub_total:,.2f}")
    if cfdi.descuento:
        print(f"  Descuento: {cfdi.descuento:,.2f}")
    print(f"  Moneda: {cfdi.moneda}")
    print(f"  Total: {cfdi.total:,.2f}")

    print(f"\nConceptos ({len(cfdi.conceptos)}):")
    for concepto in cfdi.conceptos:
        print(f"  - {concepto.descripcion} | {concepto.cantidad} x {concepto.valor_unitario:,.2f}")

    if cfdi.timbre_fiscal:
        tfd = cfdi.timbre_fiscal
        print("\nTimbre Fiscal Digital:")
        print(f"  Versión: {tfd.version}")
        print(f"  UUID: {tfd.uuid}")
        print(f"  Fecha timbrado: {tfd.fecha_timbrado}")
        print(f"  PAC: {tfd.rfc_prov_certif}")
        print(f"  Certificado SAT: {tfd.no_certificado_sat}")


def list_available_templates() -> None:
    """Listar templates disponibles."""
    pdf = CFDIPDF()
    print("Templates disponibles:")
    for template in pdf.list_templates():
        print(f"  - {template}")


if __name__ == "__main__":
    print("=== Conversión Básica ===")
    # basic_conversion()

    print("\n=== Templates Disponibles ===")
    list_available_templates()

    print("\n=== Datos del CFDI ===")
    print("Nota: Requiere un archivo factura.xml")
    # access_cfdi_data()
