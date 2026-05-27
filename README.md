# CFDI PDF

[![PyPI version](https://img.shields.io/pypi/v/cfdi-pdf.svg)](https://pypi.org/project/cfdi-pdf/)
[![Python Version](https://img.shields.io/pypi/pyversions/cfdi-pdf.svg)](https://pypi.org/project/cfdi-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Tests](https://github.com/yourusername/cfdi-pdf/workflows/Tests/badge.svg)](https://github.com/yourusername/cfdi-pdf/actions)
[![Coverage](https://img.shields.io/codecov/c/github/yourusername/cfdi-pdf)](https://codecov.io/gh/yourusername/cfdi-pdf)

Biblioteca profesional para convertir CFDI 4.0 XML a PDF con templates modernos y extensibles.

> El PDF generado siempre se nombra con el **UUID del timbre fiscal** (`{uuid}.pdf`)
> y el tamaño de página es **carta** (8.5 × 11 in), estándar en México.

## Características

- **CFDI 4.0 Completo**: Soporte total para la versión 4.0 del SAT
- **Tamaño carta**: Todos los templates generan PDFs en tamaño carta (estándar SAT México)
- **Nombre por UUID**: El archivo PDF siempre se nombra `{uuid}.pdf` para trazabilidad
- **QR SAT Oficial**: Generación del código QR con especificaciones oficiales
- **3 Templates incluidos**: `minimal`, `corporativo` y `clasico`
- **Templates Extensibles**: Sistema de templates basado en Jinja2 + HTML/CSS
- **Tipado Estricto**: Pydantic v2 para validación robusta — Python 3.12+
- **Seguridad**: Protección contra XXE, XML bombs y otros ataques
- **UTF-8 Completo**: Manejo correcto de acentos, ñ y caracteres especiales
- **Catálogos SAT**: Todos los catálogos oficiales del SAT
- **CLI Incluida**: Herramienta de línea de comandos para conversiones rápidas

## Instalación

```bash
pip install cfdi-pdf
```

Requiere Python 3.12 o superior.

## Uso Rápido

### CLI (Línea de Comandos)

```bash
# Un archivo — guarda {uuid}.pdf en el mismo directorio que el XML
cfdi-pdf factura.xml

# Directorio de salida personalizado
cfdi-pdf factura.xml --output-dir ./pdfs

# Procesamiento por lotes
cfdi-pdf enero/*.xml --output-dir ./pdfs

# Con logo y template
cfdi-pdf factura.xml --template corporativo --logo logo.png

# Ver templates disponibles
cfdi-pdf --list-templates

# Salida detallada
cfdi-pdf factura.xml --verbose
```

El comando imprime la ruta completa del PDF generado:

```
✓ factura.xml → /ruta/al/cce4d168-1234-5678-9abc-def012345678.pdf
```

### API Python

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF(template="minimal")

# Convierte y guarda {uuid}.pdf en el mismo directorio del XML
output_path = pdf.render(xml_path="factura.xml")
print(output_path)  # PosixPath('/ruta/cce4d168-...-uuid.pdf')

# Especificar directorio de salida
output_path = pdf.render(xml_path="factura.xml", output_dir="./pdfs")

# Con logo
output_path = pdf.render(
    xml_path="factura.xml",
    output_dir="./pdfs",
    logo_path="logo.png",
)
```

### Desde string XML

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()

with open("factura.xml") as f:
    xml_content = f.read()

# Guarda {uuid}.pdf en el directorio indicado
output_path = pdf.render_from_string(xml_content, output_dir="./pdfs")
```

### Obtener bytes (sin escribir a disco)

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()

# Retorna (bytes, nombre_archivo) sin tocar el sistema de archivos
pdf_bytes, filename = pdf.render_bytes(xml_path="factura.xml")

# filename = "cce4d168-1234-5678-9abc-def012345678.pdf"
# Útil para APIs web, S3, etc.
with open(filename, "wb") as f:
    f.write(pdf_bytes)
```

## Templates Disponibles

| Template | Descripción | Compatibilidad |
|---|---|---|
| `minimal` | Diseño limpio y moderno (por defecto) | WeasyPrint, Chromium |
| `corporativo` | Azul corporativo `#1a3a5c`, encabezado destacado | WeasyPrint, Chromium |
| `clasico` | Blanco/negro, tipografía Times, máxima compatibilidad | WeasyPrint, Chromium, wkhtmltopdf |

Todos los templates:
- Tamaño **carta** (8.5 × 11 in / 215.9 × 279.4 mm)
- Sin propiedades CSS experimentales (compatible con motores de impresión estrictos)
- Layout con tablas HTML en secciones fiscales (compatible con wkhtmltopdf)
- Zebra striping con clases explícitas (no `:nth-child`)

### Seleccionar template

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF(template="corporativo")
output_path = pdf.render(xml_path="factura.xml")
```

```bash
cfdi-pdf factura.xml --template clasico
```

## API de Referencia

### `CFDIPDF`

```python
CFDIPDF(
    template: str = "minimal",
    locale: str = "es_MX",
    currency_format: bool = True,
    custom_template_paths: list[str | Path] | None = None,
)
```

| Método | Descripción | Retorna |
|---|---|---|
| `render(xml_path, output_dir, template, logo_path)` | Convierte XML a PDF, guarda en disco | `Path` al PDF |
| `render_from_string(xml_content, output_dir, template, logo_path)` | Igual pero desde string | `Path` al PDF |
| `render_bytes(xml_path, template, logo_path)` | Sin escribir a disco | `(bytes, filename)` |
| `parse(xml_path)` | Parsea XML sin generar PDF | `CFDI` |
| `parse_string(xml_content)` | Parsea string XML | `CFDI` |
| `list_templates()` | Lista templates disponibles | `list[str]` |

> **Nota**: El nombre del archivo siempre es `{uuid}.pdf` (UUID en minúsculas del
> timbre fiscal). Si el CFDI no tiene timbre fiscal, se lanza `CFDIPDFError`.

### Variables disponibles en templates Jinja2

| Variable | Tipo | Descripción |
|---|---|---|
| `cfdi` | `CFDI` | Objeto completo del CFDI |
| `formatted.uuid` | `str` | UUID formateado |
| `formatted.fecha` | `str` | Fecha de expedición |
| `formatted.fecha_timbrado` | `str \| None` | Fecha de timbrado |
| `formatted.total` | `str` | Total formateado con moneda |
| `formatted.sub_total` | `str` | Subtotal formateado |
| `formatted.descuento` | `str \| None` | Descuento formateado |
| `formatted.sello_cfd` | `str \| None` | Sello CFD completo, dividido en líneas de 64 chars |
| `formatted.sello_sat` | `str \| None` | Sello SAT completo, dividido en líneas de 64 chars |
| `catalogs.tipo_comprobante` | `str` | Descripción del tipo |
| `catalogs.forma_pago` | `str` | Descripción forma de pago |
| `catalogs.metodo_pago` | `str` | Descripción método de pago |
| `catalogs.uso_cfdi` | `str` | Descripción uso CFDI |
| `catalogs.regimen_fiscal_emisor` | `str` | Régimen del emisor |
| `catalogs.regimen_fiscal_receptor` | `str` | Régimen del receptor |
| `catalogs.moneda` | `str` | Descripción de moneda |
| `qr_data` | `str` | QR SAT en base64 (PNG) |
| `logo_data` | `str` | Logo en base64 data URL |
| `cadena_original` | `str` | Cadena original del timbre |
| `format_currency(amount, moneda)` | callable | Formatea importe |
| `format_tax_rate(rate)` | callable | Formatea tasa de impuesto |

## Crear Template Personalizado

1. Crea un directorio con el nombre de tu template:

```
mis_templates/
└── mi_empresa/
    ├── template.html
    └── styles.css
```

2. `styles.css` — usa siempre tamaño carta:

```css
@page {
    size: letter;          /* 8.5 × 11 in — tamaño carta México */
    margin: 15mm 15mm 20mm 15mm;
}
```

3. `template.html` — usa las variables Jinja2 estándar:

```html
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <link rel="stylesheet" href="styles.css">
</head>
<body>
    <h1>{{ catalogs.tipo_comprobante }}</h1>
    <p>UUID: {{ formatted.uuid }}</p>
    <p>Emisor: {{ cfdi.emisor.nombre }}</p>
    <p>Total: {{ formatted.total }}</p>
    {% if qr_data %}
        <img src="data:image/png;base64,{{ qr_data }}" alt="QR SAT">
    {% endif %}
</body>
</html>
```

4. Registra la ruta y usa tu template:

```python
from pathlib import Path
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF(
    template="mi_empresa",
    custom_template_paths=[Path("./mis_templates")],
)
output_path = pdf.render(xml_path="factura.xml")
```

## Estructura del Proyecto

```
src/cfdi_pdf/
├── api.py              # API principal (CFDIPDF)
├── cli.py              # Interfaz de línea de comandos
├── exceptions.py       # Excepciones personalizadas
├── models/             # Modelos Pydantic v2
│   ├── cfdi.py
│   ├── emisor.py
│   ├── receptor.py
│   ├── concepto.py
│   ├── impuestos.py
│   └── timbre.py
├── parser/             # Parser XML seguro
│   ├── xml_parser.py
│   └── sanitizer.py
├── qr/                 # Generador QR SAT oficial
│   └── generator.py
├── render/             # Motor de renderizado
│   ├── engine.py
│   └── template.py
├── sat/                # Catálogos SAT
│   ├── catalogs.py
│   └── helpers.py
├── utils/              # Utilidades
│   └── formatters.py
└── templates/          # Templates incluidos
    ├── minimal/
    │   ├── template.html
    │   └── styles.css
    ├── corporativo/
    │   ├── template.html
    │   └── styles.css
    └── clasico/
        ├── template.html
        └── styles.css
```

## Requisitos

- **Python** 3.12+
- **WeasyPrint** >= 60.0
- **Pydantic** >= 2.0.0
- **Jinja2** >= 3.1.0
- **qrcode** >= 7.4
- **Pillow** >= 10.0.0
- **lxml** >= 4.9.0

## Desarrollo

### Configuración del Entorno

```bash
git clone https://github.com/yourusername/cfdi-pdf.git
cd cfdi-pdf

python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

pip install -e ".[dev]"
```

### Ejecutar Tests

```bash
# Todos los tests
pytest

# Con cobertura HTML
pytest --cov=cfdi_pdf --cov-report=html

# Tests específicos
pytest tests/test_parser.py -v
```

### Linting y Formateo

```bash
ruff check .          # linter
ruff check --fix .    # auto-fix
black .               # formatter
mypy src              # type checker
```

### Build

```bash
python -m build
twine upload dist/*   # requiere credenciales PyPI
```

## Especificaciones Técnicas

### CFDI 4.0

- **Namespace**: `http://www.sat.gob.mx/cfd/4`
- **Timbre Fiscal Digital**: Versión 1.1
- **Catálogos SAT**: Completos y actualizados

### QR SAT

URL de verificación: `https://verificacfdi.facturaelectronica.sat.gob.mx/default.aspx`

Parámetros: `id` (UUID), `re` (RFC emisor), `rr` (RFC receptor), `tt` (total 6 decimales), `fe` (últimos 8 chars del sello).

### Seguridad

- **Protección XXE**: `resolve_entities=False` en lxml
- **XML Bombs**: `no_network=True`, `huge_tree=False`
- **Sandboxing**: `SandboxedEnvironment` de Jinja2
- **Sanitización**: Regex compilado contra caracteres inválidos XML 1.0

### Compatibilidad CSS

Los templates evitan intencionalmente propiedades CSS experimentales para máxima compatibilidad con motores de impresión:

| Propiedad | Estado |
|---|---|
| `@page size: letter` | Soportado en todos |
| `display: table` | Soportado en todos |
| `display: flex` | Solo en zonas decorativas no-fiscales |
| `display: grid` | No usado |
| CSS variables (`var(--)`) | No usado |
| `:nth-child` en tablas | No usado — zebra con clases explícitas |
| `border-radius` (clasico) | No usado |

## Roadmap

- [ ] Soporte para complemento Pagos 2.0
- [ ] Soporte para complemento Nómina 1.2
- [ ] Soporte para Carta Porte 3.1
- [ ] Validación contra esquemas XSD del SAT
- [ ] API REST lista para deploy
- [ ] Integración con PACs

## Licencia

MIT License — ver archivo [LICENSE](LICENSE) para detalles.

## Soporte

- **Bugs / Features**: [GitHub Issues](https://github.com/yourusername/cfdi-pdf/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/yourusername/cfdi-pdf/discussions)

---

**Nota**: Esta biblioteca no está afiliada oficialmente con el SAT. Verifica siempre la validez de los CFDIs en el portal oficial del SAT.
