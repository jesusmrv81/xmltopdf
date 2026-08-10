# CFDI PDF

[![PyPI version](https://img.shields.io/pypi/v/cfdi-pdf.svg)](https://pypi.org/project/cfdi-pdf/)
[![Python Version](https://img.shields.io/pypi/pyversions/cfdi-pdf.svg)](https://pypi.org/project/cfdi-pdf/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Typing](https://img.shields.io/badge/typing-strict-228B22.svg)](https://pypi.org/project/cfdi-pdf/)
[![CI / CD](https://github.com/jesusmrv81/xmltopdf/actions/workflows/ci.yml/badge.svg)](https://github.com/jesusmrv81/xmltopdf/actions)
[![Coverage](https://img.shields.io/codecov/c/github/jesusmrv81/xmltopdf)](https://codecov.io/gh/jesusmrv81/xmltopdf)

Biblioteca profesional para convertir CFDI 4.0 XML a PDF con templates modernos y extensibles.

> El PDF generado siempre se nombra con el **UUID del timbre fiscal** (`{uuid}.pdf`)
> y el tamaño de página es **carta** (8.5 × 11 in), estándar en México.

## Características

- **CFDI 4.0 Completo**: Soporte total para la versión 4.0 del SAT
- **Cadena original oficial**: genera la cadena original con los XSLT del SAT
  (`cadenaoriginal_4_0.xslt` y `cadenaoriginal_TFD_1_1.xslt` empaquetados)
- **Verificación de sellos**: `SelloVerifier` valida `SelloCFD` (certificado
  embebido) y `SelloSAT` (cert SAT) contra la cadena original
- **Validación XSD**: `validate_xsd=True` valida contra el esquema oficial
  `cfdv40.xsd` (catálogos incluidos)
- **Complemento de Pago 2.0**: modelos, parser y render dedicados
- **Complemento de Nómina 1.2**: modelos, parser y render dedicados
- **Complemento de Carta Porte 3.1**: modelos, parser y render dedicados
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

### Desde string XML y obtener bytes (sin disco)

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()

with open("factura.xml") as f:
    xml_content = f.read()

# Retorna (bytes, nombre_archivo) sin tocar el sistema de archivos
pdf_bytes, filename = pdf.render_bytes_from_string(xml_content)

# Ideal para exponer la librería detrás de un framework web (FastAPI, etc.)
```

> La librería es 100% pura: no depende de ningún framework web. Para usarla en
> un microservicio, ver el adaptador de ejemplo en
> `examples/fastapi_service.py`.

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
    custom_template_paths: list[str | Path] | None = None,
    validate_xsd: bool = False,
    validate_catalogs: bool = False,
    max_xml_size: int | None = 10_000_000,
    on_render: Callable[[CFDI, str], None] | None = None,
)
```

| Método | Descripción | Retorna |
|---|---|---|
| `render(xml_path, output_dir, template, logo_path)` | Convierte XML a PDF, guarda en disco | `Path` al PDF |
| `render_from_string(xml_content, output_dir, template, logo_path)` | Igual pero desde string | `Path` al PDF |
| `render_bytes(xml_path, template, logo_path)` | Sin escribir a disco | `(bytes, filename)` |
| `render_bytes_from_string(xml_content, template, logo_path)` | Desde string, sin escribir a disco | `(bytes, filename)` |
| `parse(xml_path)` | Parsea XML sin generar PDF | `CFDI` |
| `parse_string(xml_content)` | Parsea string XML | `CFDI` |
| `list_templates()` | Lista templates disponibles | `list[str]` |

> **Nota**: El nombre del archivo siempre es `{uuid}.pdf` (UUID en minúsculas del
> timbre fiscal). Si el CFDI no tiene timbre fiscal, se lanza `CFDIPDFError`.

### Cadena original, sellos y validación XSD

El parser calcula la **cadena original** del comprobante y del timbre con los
XSLT oficiales del SAT (`cadenaoriginal_4_0.xslt` y `cadenaoriginal_TFD_1_1.xslt`,
empaquetados en `cfdi_pdf/xslt/`).

```python
from cfdi_pdf import CFDIPDF, SelloVerifier

pdf = CFDIPDF(validate_xsd=True)  # valida contra cfdv40.xsd durante el parseo
cfdi = pdf.parse("factura.xml")

print(cfdi.cadena_original)  # cadena original del comprobante
print(cfdi.timbre_fiscal.cadena_origen)  # cadena original del TFD

# Verificar la firma del emisor contra su certificado embebido
if SelloVerifier.verify_sello_cfd(cfdi):
    print("✓ SelloCFD válido")

# Verificar la firma del SAT (requiere el certificado del SAT, identificado
# por NoCertificadoSAT)
if SelloVerifier.verify_sello_sat(cfdi, sat_certificate_pem):
    print("✓ SelloSAT válido")
```

> **Nota**: la verificación de `SelloSAT` requiere el certificado X.509 del SAT
> (no viene embebido en el XML). Se puede pasar explícitamente o dejar el
> certificado en el **store** (`~/.cache/cfdi-pdf/certs/` o la variable
> `CFDI_PDF_SAT_CERTS_DIR`); entonces se busca automáticamente por
> `NoCertificadoSAT`:
>
> ```python
> if SelloVerifier.verify_sello_sat(cfdi):  # busca en el store
>     print("✓ SelloSAT válido")
> ```

### Validación de catálogos (sin XSD)

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF(validate_catalogs=True)  # valida claves SAT (moneda, régimen, uso CFDI…)
cfdi = pdf.parse("factura.xml")  # lanza InvalidCFDIError si alguna clave es inválida
```

### Complementos soportados

Además de Pagos 2.0, Nómina 1.2 y Carta Porte 3.1, se modelan **Leyendas
Fiscales**, **IEPS** e **Información Global** (se renderizan en los templates).
La `cfdi:Addenda` se detecta (`cfdi.has_addenda`) pero **se ignora** por
seguridad: es XML arbitrario del emisor, sin valor fiscal.

### Procesamiento por lotes y rendimiento

`render_batch()` procesa varios XML reutilizando la instancia (templates
compilados una sola vez) y puede paralelizar WeasyPrint con múltiples procesos:

```python
from cfdi_pdf import CFDIPDF

pdf = CFDIPDF()
results = pdf.render_batch(
    ["enero/a.xml", "enero/b.xml"],
    output_dir="./pdfs",
    workers=4,  # None/1 = secuencial; >1 = multiproceso
)

for result in results:
    # BatchResult(source, output | None, error | None)
    print(result.source.name, result.output or result.error)
```

### Telemetría (logging JSON + hook de post-render)

Para entornos de servicio, emite logs en una línea JSON por evento:

```python
from cfdi_pdf.utils.logging import setup_json_logging

setup_json_logging()  # los logs de cfdi_pdf.* salen como JSON a stdout
```

Y registra cada render con un hook `on_render(cfdi, output)`:

```python
from cfdi_pdf import CFDIPDF


def track(cfdi, output):
    print("uuid:", cfdi.timbre_fiscal.uuid, "->", output)


pdf = CFDIPDF(on_render=track)
```

### Recursos del SAT (XSLT/XSD) — descarga en runtime

La biblioteca **no empaqueta** los XSLT/XSD del SAT (son grandes y el SAT los
actualiza con frecuencia). Se descargan bajo demanda, se cachean en disco y se
verifican por **SHA-256** contra un manifiesto empaquetado:

- **Origen**: primero `www.sat.gob.mx`; si está bloqueado (geo-bloqueo), un
  mirror verificado. Configurables con `CFDI_PDF_BASE_URLS`.
- **Caché**: `~/.cache/cfdi-pdf` (configurable con `CFDI_PDF_CACHE_DIR`).
- **Predescarga** para deploys sin red:
  ```bash
  cfdi-pdf --download-resources        # XSLT de la cadena original (~400 KB)
  cfdi-pdf --download-resources --all  # + esquemas XSD incl. catálogos (~7 MB)
  ```
  o desde Python: `CFDIPDF().ensure_resources(all_resources=True)`.

Si el SAT actualiza un archivo, el hash no coincidirá y se lanza
`SATResourceError` con el hash nuevo (detecta el cambio en vez de usar
contenido no verificado). Ver `doc/seguridad.md` para los detalles de
procedencia y el proceso de actualización del manifiesto.

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
.
├── src/cfdi_pdf/     # Código de la biblioteca
├── tests/            # Suite de tests (pytest)
├── examples/         # Ejemplos de uso (incluye integración FastAPI)
├── doc/              # Auditoría y documentación técnica
│   ├── analisis.md   #   Arquitectura y decisiones de diseño
│   ├── hallazgos.md  #   Bugs/defectos priorizados
│   ├── mejoras.md    #   Mejoras recomendadas
│   ├── seguridad.md  #   Análisis de seguridad y procedencia SAT
│   └── calidad.md    #   Tests, cobertura y CI
└── pyproject.toml
```

Detalle del paquete:

```
src/cfdi_pdf/
├── api.py              # API principal (CFDIPDF)
├── cli.py              # Interfaz de línea de comandos
├── exceptions.py       # Excepciones personalizadas
├── crypto/             # Verificación de sellos
│   └── verifier.py     #   SelloVerifier (RSA/SHA-256)
├── models/             # Modelos Pydantic v2
│   ├── cfdi.py
│   ├── emisor.py
│   ├── receptor.py
│   ├── concepto.py
│   ├── impuestos.py
│   ├── timbre.py
│   ├── pagos.py        #   Complemento de Pago 2.0
│   ├── nomina.py       #   Complemento de Nómina 1.2
│   └── carta_porte.py  #   Complemento de Carta Porte 3.1
├── parser/             # Parser XML seguro
│   ├── xml_parser.py
│   ├── sanitizer.py
│   └── xsd_validator.py #  Validación contra cfdv40.xsd
├── qr/                 # Generador QR SAT oficial
│   └── generator.py
├── render/             # Motor de renderizado
│   ├── engine.py
│   └── template.py
├── sat/                # Catálogos SAT
│   ├── catalogs.py
│   ├── helpers.py
│   ├── cadena_original.py  # XSLT oficiales (cadena original)
│   └── resources.py        # Descarga runtime + verificación SHA-256
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
- **lxml** >= 5.0.0
- **cryptography** >= 41.0.0

## Desarrollo

### Configuración del Entorno

```bash
git clone https://github.com/jesusmrv81/xmltopdf.git
cd xmltopdf

python -m venv venv
source venv/bin/activate      # Linux/macOS
# venv\Scripts\activate       # Windows

pip install -e ".[dev]"

# Predescargar los recursos del SAT (XSLT/XSD) para la cadena original y la
# validación XSD; de lo contrario se descargan en la primera ejecución
cfdi-pdf --download-resources --all
```

> Las dependencias se fijan en `requirements.lock` (con hashes) para
> reproducibilidad de CI/deploys. Para regenerarlo:
>
> ```bash
> pip-compile pyproject.toml --extra dev --generate-hashes -o requirements.lock
> ```

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
ruff format .         # formatter (incluye bloques de código en Markdown)
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

- [x] Soporte para complemento Pagos 2.0
- [x] Soporte para complemento Nómina 1.2
- [x] Soporte para complemento Carta Porte 3.1 (subconjunto esencial)
- [x] Cadena original oficial del SAT (XSLT) y validación contra esquemas XSD
- [ ] Validación de sellos contra el SAT (verificación completa SelloSAT con
      certificados del SAT actualizados)
- [ ] API REST lista para deploy (ver ejemplo `examples/fastapi_service.py`)
- [ ] Integración con PACs

## Licencia

MIT License — ver archivo [LICENSE](LICENSE) para detalles.

## Soporte

- **Bugs / Features**: [GitHub Issues](https://github.com/jesusmrv81/xmltopdf/issues)
- **Discusiones**: [GitHub Discussions](https://github.com/jesusmrv81/xmltopdf/discussions)

---

**Nota**: Esta biblioteca no está afiliada oficialmente con el SAT. Verifica siempre la validez de los CFDIs en el portal oficial del SAT.
