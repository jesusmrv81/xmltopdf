"""
Creación y uso de templates personalizados.

El template usa las variables estándar del contexto (ver README):
``cfdi``, ``formatted``, ``catalogs``, ``qr_data`` y los helpers
``format_currency``, ``format_tax_rate``, ``format_number``.
"""

from pathlib import Path

from cfdi_pdf import CFDIPDF

TEMPLATE_DIR = Path("mi_template")


def create_custom_template() -> None:
    """Crear un template personalizado."""
    TEMPLATE_DIR.mkdir(exist_ok=True)

    template_html = """<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <title>CFDI {{ formatted.uuid }}</title>
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>FACTURA</h1>
            <div class="uuid">{{ formatted.uuid }}</div>
        </header>

        <section class="info">
            <div class="emisor">
                <h2>Emisor</h2>
                <p><strong>{{ cfdi.emisor.nombre }}</strong></p>
                <p>RFC: {{ cfdi.emisor.rfc }}</p>
                <p>Régimen: {{ catalogs.regimen_fiscal_emisor }}</p>
            </div>

            <div class="receptor">
                <h2>Receptor</h2>
                <p><strong>{{ cfdi.receptor.nombre }}</strong></p>
                <p>RFC: {{ cfdi.receptor.rfc }}</p>
                <p>Uso CFDI: {{ catalogs.uso_cfdi }}</p>
            </div>
        </section>

        <section class="totales">
            <h2>Totales</h2>
            <table>
                <tr>
                    <td>Subtotal:</td>
                    <td>{{ formatted.sub_total }}</td>
                </tr>
                {% if formatted.descuento %}
                <tr>
                    <td>Descuento:</td>
                    <td>-{{ formatted.descuento }}</td>
                </tr>
                {% endif %}
                {% if cfdi.impuestos %}
                {% for traslado in cfdi.impuestos.traslados %}
                <tr>
                    <td>{{ get_impuesto(traslado.impuesto) }} {{ format_tax_rate(traslado.tasa_o_cuota) }}:</td>
                    <td>{{ format_currency(traslado.importe, moneda) }}</td>
                </tr>
                {% endfor %}
                {% endif %}
                <tr class="total">
                    <td><strong>Total:</strong></td>
                    <td><strong>{{ formatted.total }}</strong></td>
                </tr>
            </table>
        </section>

        {% if qr_data %}
        <section class="qr">
            <img src="data:image/png;base64,{{ qr_data }}" alt="QR SAT">
            <p>Código QR de verificación SAT</p>
        </section>
        {% endif %}

        <footer>
            <p>Este documento es una representación impresa de un CFDI</p>
            <p>Verificación: https://verificacfdi.facturaelectronica.sat.gob.mx</p>
        </footer>
    </div>
</body>
</html>
"""

    (TEMPLATE_DIR / "template.html").write_text(template_html, encoding="utf-8")

    styles_css = """
* { margin: 0; padding: 0; box-sizing: border-box; }

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 10pt;
    color: #333;
}

.container { max-width: 21cm; margin: 0 auto; padding: 2cm; }

header { text-align: center; margin-bottom: 2em; padding-bottom: 1em; border-bottom: 3px solid #2563eb; }
header h1 { color: #2563eb; font-size: 24pt; }
.uuid { font-family: monospace; font-size: 9pt; color: #666; }

.info { display: grid; grid-template-columns: 1fr 1fr; gap: 2em; margin-bottom: 2em; }
.info h2 { color: #2563eb; font-size: 12pt; border-bottom: 1px solid #ddd; padding-bottom: 0.3em; }

.totales { margin: 2em 0; }
.totales h2 { color: #2563eb; font-size: 12pt; margin-bottom: 1em; }
.totales table { width: 100%; border-collapse: collapse; }
.totales td { padding: 0.5em; border-bottom: 1px solid #eee; }
.totales td:last-child { text-align: right; font-family: monospace; }
.totales .total td { font-size: 14pt; border-top: 2px solid #2563eb; border-bottom: 2px solid #2563eb; }

.qr { text-align: center; margin: 2em 0; }
.qr img { width: 180px; height: 180px; }
.qr p { margin-top: 0.5em; font-size: 8pt; color: #666; }

footer { margin-top: 3em; padding-top: 1em; border-top: 1px solid #ddd; text-align: center; font-size: 8pt; color: #666; }
footer p { margin: 0.3em 0; }
"""

    (TEMPLATE_DIR / "styles.css").write_text(styles_css, encoding="utf-8")

    print(f"✓ Template creado en: {TEMPLATE_DIR}")


def use_custom_template() -> None:
    """Usar un template personalizado."""
    pdf = CFDIPDF(custom_template_paths=[Path(".")])

    output_path = pdf.render(
        xml_path="factura.xml",
        output_dir="./pdfs",
        template="mi_template",
    )

    print(f"✓ PDF generado con template personalizado: {output_path}")


if __name__ == "__main__":
    print("=== Crear Template Personalizado ===")
    create_custom_template()

    print("\n=== Usar Template Personalizado ===")
    print("Nota: Requiere un archivo factura.xml")
    # use_custom_template()
