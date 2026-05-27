"""
Creación y uso de templates personalizados
"""

from pathlib import Path

from cfdi_pdf import CFDIPDF


def create_custom_template():
    """Crear un template personalizado"""

    # Crear directorio del template
    template_dir = Path("mi_template")
    template_dir.mkdir(exist_ok=True)

    # Crear template.html
    template_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>FACTURA</h1>
            <div class="uuid">{{ cfdi.uuid }}</div>
        </header>

        <section class="info">
            <div class="emisor">
                <h2>Emisor</h2>
                <p><strong>{{ cfdi.emisor.nombre }}</strong></p>
                <p>RFC: {{ cfdi.emisor.rfc }}</p>
                <p>Régimen: {{ get_catalog('regimen_fiscal', cfdi.emisor.regimen_fiscal) }}</p>
            </div>

            <div class="receptor">
                <h2>Receptor</h2>
                <p><strong>{{ cfdi.receptor.nombre }}</strong></p>
                <p>RFC: {{ cfdi.receptor.rfc }}</p>
                <p>Uso CFDI: {{ get_catalog('uso_cfdi', cfdi.receptor.uso_cfdi) }}</p>
            </div>
        </section>

        <section class="totales">
            <h2>Totales</h2>
            <table>
                <tr>
                    <td>Subtotal:</td>
                    <td>{{ format_currency(cfdi.subtotal, cfdi.moneda) }}</td>
                </tr>
                {% if cfdi.descuento %}
                <tr>
                    <td>Descuento:</td>
                    <td>-{{ format_currency(cfdi.descuento, cfdi.moneda) }}</td>
                </tr>
                {% endif %}
                {% for traslado in cfdi.impuestos.traslados %}
                <tr>
                    <td>{{ traslado.impuesto }} {{ format_tax_rate(traslado.tasa_o_cuota) }}:</td>
                    <td>{{ format_currency(traslado.importe, cfdi.moneda) }}</td>
                </tr>
                {% endfor %}
                <tr class="total">
                    <td><strong>Total:</strong></td>
                    <td><strong>{{ format_currency(cfdi.total, cfdi.moneda) }}</strong></td>
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

    (template_dir / "template.html").write_text(template_html)

    # Crear styles.css
    styles_css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
    font-size: 10pt;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 21cm;
    margin: 0 auto;
    padding: 2cm;
}

header {
    text-align: center;
    margin-bottom: 2em;
    padding-bottom: 1em;
    border-bottom: 3px solid #2563eb;
}

header h1 {
    color: #2563eb;
    font-size: 24pt;
    margin-bottom: 0.5em;
}

.uuid {
    font-family: monospace;
    font-size: 9pt;
    color: #666;
}

.info {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2em;
    margin-bottom: 2em;
}

.info h2 {
    color: #2563eb;
    font-size: 12pt;
    margin-bottom: 0.5em;
    border-bottom: 1px solid #ddd;
    padding-bottom: 0.3em;
}

.totales {
    margin: 2em 0;
}

.totales h2 {
    color: #2563eb;
    font-size: 12pt;
    margin-bottom: 1em;
}

.totales table {
    width: 100%;
    border-collapse: collapse;
}

.totales td {
    padding: 0.5em;
    border-bottom: 1px solid #eee;
}

.totales td:last-child {
    text-align: right;
    font-family: monospace;
}

.totales .total td {
    font-size: 14pt;
    border-top: 2px solid #2563eb;
    border-bottom: 2px solid #2563eb;
    padding: 1em 0.5em;
}

.qr {
    text-align: center;
    margin: 2em 0;
}

.qr img {
    width: 200px;
    height: 200px;
}

.qr p {
    margin-top: 0.5em;
    font-size: 8pt;
    color: #666;
}

footer {
    margin-top: 3em;
    padding-top: 1em;
    border-top: 1px solid #ddd;
    text-align: center;
    font-size: 8pt;
    color: #666;
}

footer p {
    margin: 0.3em 0;
}
"""

    (template_dir / "styles.css").write_text(styles_css)

    print(f"✓ Template creado en: {template_dir}")
    print(f"  - {template_dir / 'template.html'}")
    print(f"  - {template_dir / 'styles.css'}")


def use_custom_template():
    """Usar template personalizado"""

    # Registrar directorio de templates
    pdf = CFDIPDF(template_dirs=[Path(".")])

    # Usar template personalizado
    pdf.render(xml_path="factura.xml", output="factura_custom.pdf", template="mi_template")

    print("✓ PDF generado con template personalizado: factura_custom.pdf")


def create_minimal_modern_template():
    """Crear un template minimalista moderno"""

    template_dir = Path("minimal_modern")
    template_dir.mkdir(exist_ok=True)

    # Template con diseño ultra-minimalista
    template_html = """<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <div class="page">
        <div class="header">
            <div class="left">
                <div class="title">COMPROBANTE FISCAL DIGITAL</div>
                <div class="subtitle">CFDI 4.0</div>
            </div>
            <div class="right">
                <div class="uuid">{{ cfdi.uuid }}</div>
            </div>
        </div>

        <div class="grid">
            <div class="card">
                <div class="label">EMISOR</div>
                <div class="value">{{ cfdi.emisor.nombre }}</div>
                <div class="subvalue">{{ cfdi.emisor.rfc }}</div>
            </div>

            <div class="card">
                <div class="label">RECEPTOR</div>
                <div class="value">{{ cfdi.receptor.nombre }}</div>
                <div class="subvalue">{{ cfdi.receptor.rfc }}</div>
            </div>
        </div>

        <div class="amount">
            <div class="label">TOTAL</div>
            <div class="value">{{ format_currency(cfdi.total, cfdi.moneda) }}</div>
            <div class="subvalue">{{ format_date(cfdi.fecha) }}</div>
        </div>

        {% if qr_data %}
        <div class="qr-section">
            <img src="data:image/png;base64,{{ qr_data }}" class="qr">
            <div class="qr-text">Verificación SAT</div>
        </div>
        {% endif %}

        <div class="footer">
            Representación impresa de CFDI
        </div>
    </div>
</body>
</html>
"""

    styles_css = """
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    background: #fff;
}

.page {
    max-width: 21cm;
    margin: 0 auto;
    padding: 3cm;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: flex-start;
    margin-bottom: 3em;
}

.title {
    font-size: 18pt;
    font-weight: 700;
    letter-spacing: -0.5px;
}

.subtitle {
    font-size: 10pt;
    color: #666;
    margin-top: 0.3em;
}

.uuid {
    font-family: 'SF Mono', Monaco, monospace;
    font-size: 9pt;
    color: #999;
    text-align: right;
}

.grid {
    display: grid;
    grid-template-columns: 1fr 1fr;
    gap: 2em;
    margin-bottom: 3em;
}

.card {
    padding: 1.5em;
    background: #f8f9fa;
    border-radius: 8px;
}

.label {
    font-size: 8pt;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 1px;
    color: #999;
    margin-bottom: 0.5em;
}

.value {
    font-size: 14pt;
    font-weight: 600;
    color: #333;
}

.subvalue {
    font-size: 10pt;
    color: #666;
    margin-top: 0.3em;
}

.amount {
    text-align: center;
    padding: 2em;
    background: #000;
    color: #fff;
    border-radius: 12px;
    margin-bottom: 3em;
}

.amount .label {
    color: #999;
}

.amount .value {
    font-size: 32pt;
    color: #fff;
    font-weight: 700;
}

.amount .subvalue {
    color: #ccc;
}

.qr-section {
    text-align: center;
    margin: 3em 0;
}

.qr {
    width: 180px;
    height: 180px;
}

.qr-text {
    margin-top: 1em;
    font-size: 8pt;
    color: #999;
}

.footer {
    text-align: center;
    font-size: 8pt;
    color: #ccc;
    margin-top: 3em;
    padding-top: 2em;
    border-top: 1px solid #eee;
}
"""

    (template_dir / "template.html").write_text(template_html)
    (template_dir / "styles.css").write_text(styles_css)

    print(f"✓ Template minimalista moderno creado: {template_dir}")


if __name__ == "__main__":
    print("=== Crear Template Personalizado ===")
    create_custom_template()

    print("\n=== Crear Template Minimalista Moderno ===")
    create_minimal_modern_template()

    print("\n=== Usar Template Personalizado ===")
    print("Nota: Requiere un archivo factura.xml")
    # use_custom_template()
