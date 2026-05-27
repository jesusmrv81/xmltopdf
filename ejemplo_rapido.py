#!/usr/bin/env python3
"""
Ejemplo de uso rápido de CFDI PDF
Demuestra la conversión de un CFDI 4.0 XML a PDF
"""

from pathlib import Path
from cfdi_pdf import CFDIPDF

# Inicializar el conversor
pdf = CFDIPDF(template="minimal")

# Convertir el XML de ejemplo
xml_file = Path("tests/fixtures/sample_cfdi.xml")
output_pdf = Path("ejemplo_factura.pdf")

print("Convirtiendo CFDI 4.0 a PDF...")
print(f"  Input:  {xml_file}")
print(f"  Output: {output_pdf}")

pdf.render(
    xml_path=xml_file,
    output=output_pdf,
    template="minimal"
)

print(f"\n✅ PDF generado exitosamente: {output_pdf}")
print(f"   Tamaño: {output_pdf.stat().st_size:,} bytes")

# Mostrar información del CFDI
print("\n📋 Información del CFDI:")
cfdi = pdf.parse(xml_file)
print(f"   UUID: {cfdi.timbre_fiscal.uuid if cfdi.timbre_fiscal else 'N/A'}")
print(f"   Emisor: {cfdi.emisor.nombre} ({cfdi.emisor.rfc})")
print(f"   Receptor: {cfdi.receptor.nombre} ({cfdi.receptor.rfc})")
print(f"   Total: ${cfdi.total:,.2f} {cfdi.moneda}")
print(f"   Fecha: {cfdi.fecha}")
print(f"   Conceptos: {len(cfdi.conceptos)}")

if cfdi.impuestos:
    print(f"\n💰 Impuestos:")
    if cfdi.impuestos.total_impuestos_trasladados:
        print(f"   Trasladados: ${cfdi.impuestos.total_impuestos_trasladados:,.2f}")
    if cfdi.impuestos.total_impuestos_retenidos:
        print(f"   Retenidos: ${cfdi.impuestos.total_impuestos_retenidos:,.2f}")

print("\n✅ Ejemplo completado exitosamente")
